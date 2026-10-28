"""Validación del recomendador con ejecuciones reales. Uso:  python validar.py  (después de python entrenar.py)

Genera en resultados/: metricas_ranking.csv, coeficientes.csv, errores_por_grupo.csv, casos_limite.csv, ranking.png
IMPORTANTE: los datos y la etiqueta son sintéticos; estas métricas muestran que el pipeline aprende la regla simulada
y ordena mejor que las líneas base, NO que las recomendaciones funcionen con personas reales.
"""
import itertools
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import (ATRIBUTOS_BIN, CARPETA_RESULTADOS, CARRERAS, COEF_REGLA, COLUMNAS_PAR, FRANJAS, INTERESES,
                    NECESIDADES, SEMILLA, UMBRAL_AVISO)
from datos import armar_pares, etiquetar, generar_estudiantes, z_regla
from modelo import crear_atributos
from recomendador import EntradaInvalida, cargar_recursos, recomendar_mentores

KS = (1, 3, 5)


def conjunto_prueba(catalogo, n_estudiantes=300):
    """Estudiantes NUEVOS (semilla distinta a la de entrenamiento) contra TODOS los mentores elegibles."""
    rng = np.random.default_rng(SEMILLA + 1)
    est = generar_estudiantes(rng, n_estudiantes)
    est["est_id"] = [f"T-{i:04d}" for i in range(n_estudiantes)]
    e = est.loc[est.index.repeat(len(catalogo))].reset_index(drop=True)
    idx = np.tile(np.arange(len(catalogo)), n_estudiantes)
    pares = armar_pares(e, catalogo, idx)
    return etiquetar(pares, rng), rng


def metricas_ranking(df, score, k):
    """Precisión@k, acierto@k (al menos un compatible en el top-k) y NDCG@k (relevancia binaria)."""
    p, h, n = [], [], []
    desc = 1 / np.log2(np.arange(2, k + 2))
    for _, g in df.groupby("est_id", sort=False):
        top = g.iloc[np.argsort(-g[score].to_numpy(), kind="stable")[:k]]["compatible"].to_numpy()
        ideal = np.sort(g["compatible"].to_numpy())[::-1][:k]
        p.append(top.mean()); h.append(float(top.any()))
        n.append((top * desc[:len(top)]).sum() / max((ideal * desc[:len(ideal)]).sum(), 1e-9) if ideal.sum() else np.nan)
    return np.mean(p), np.mean(h), np.nanmean(n)


def main():
    os.makedirs(CARPETA_RESULTADOS, exist_ok=True)
    modelo, catalogo = cargar_recursos()
    df, rng = conjunto_prueba(catalogo)
    a = crear_atributos(df)
    df["s_modelo"] = modelo.predict_proba(df[COLUMNAS_PAR])[:, 1]
    df["s_azar"] = rng.random(len(df))
    df["s_coincidencias"] = a[ATRIBUTOS_BIN].sum(axis=1) + rng.random(len(df)) * 1e-3   # línea base sin modelo
    df["s_regla_real"] = z_regla(a)                                                    # cota superior (conoce la regla)
    nombres = {"s_azar": "Azar", "s_coincidencias": "Contar coincidencias (sin modelo)",
               "s_modelo": "Regresión logística", "s_regla_real": "Regla real (cota superior)"}

    filas = []
    for s, nombre in nombres.items():
        for k in KS:
            p, h, n = metricas_ranking(df, s, k)
            filas.append({"estrategia": nombre, "k": k, "precision_k": p, "acierto_k": h, "ndcg_k": n})
    mr = pd.DataFrame(filas).round(4)
    mr.to_csv(f"{CARPETA_RESULTADOS}/metricas_ranking.csv", index=False)
    print("Métricas de ranking (estudiantes de prueba nuevos):\n", mr.to_string(index=False))
    print(f"\nProporción de pares compatibles en prueba: {df['compatible'].mean():.3f}")

    # 1) ¿El modelo recupera la regla simulada? (solo posible con datos sintéticos)
    lr = modelo.named_steps["clf"]
    esc = modelo.named_steps["prep"].named_transformers_["num"]
    escala = esc.scale_[0]
    # el escalado centra dif_semestres: se devuelve el intercepto a la escala original para poder compararlo
    intercepto = float(lr.intercept_[0] - lr.coef_[0][0] * esc.mean_[0] / escala)
    aprendidos = {"dif_semestres": lr.coef_[0][0] / escala, **dict(zip(ATRIBUTOS_BIN, lr.coef_[0][1:]))}
    co = pd.DataFrame([{"atributo": k, "coef_regla_real": COEF_REGLA[k], "coef_aprendido": aprendidos[k]}
                       for k in ["misma_carrera", "mismo_interes", "cubre_necesidad", "misma_franja", "dif_semestres"]]
                      + [{"atributo": "intercepto", "coef_regla_real": COEF_REGLA["intercepto"],
                          "coef_aprendido": intercepto}]).round(3)
    co.to_csv(f"{CARPETA_RESULTADOS}/coeficientes.csv", index=False)
    print("\nCoeficientes (el ruido de la regla atenúa un poco los aprendidos):\n", co.to_string(index=False))

    # 2) Análisis de errores: ¿en qué perfiles el top-3 del modelo rinde peor?
    reg = []
    for col, nombre in [("est_carrera", "carrera"), ("est_necesidad", "necesidad"), ("est_franja", "franja")]:
        for val, g in df.groupby(col):
            pm, _, _ = metricas_ranking(g, "s_modelo", 3)
            pr, _, _ = metricas_ranking(g, "s_regla_real", 3)
            reg.append({"variable": nombre, "valor": val, "n_estudiantes": g["est_id"].nunique(),
                        "precision_3_modelo": pm, "precision_3_regla_real": pr, "brecha": pr - pm})
    err = pd.DataFrame(reg).round(4).sort_values("brecha", ascending=False)
    err.to_csv(f"{CARPETA_RESULTADOS}/errores_por_grupo.csv", index=False)
    top1_modelo = df.loc[df.groupby("est_id")["s_modelo"].idxmax(), ["est_id", "mentor_id"]]
    top1_real = df.loc[df.groupby("est_id")["s_regla_real"].idxmax(), ["est_id", "mentor_id"]]
    coincide = (top1_modelo.set_index("est_id")["mentor_id"] == top1_real.set_index("est_id")["mentor_id"]).mean()
    print(f"\nTop-1 del modelo coincide con el de la regla real en {coincide:.1%} de los estudiantes")
    print("Grupos con mayor brecha:\n", err.head(5).to_string(index=False))

    # 3) Casos límite: todos los perfiles posibles + semestres fuera de rango
    sin_error, total, bajo_umbral, tops = 0, 0, 0, []
    for c, i, n, f in itertools.product(CARRERAS, INTERESES, NECESIDADES, FRANJAS):
        total += 1
        r = recomendar_mentores({"carrera": c, "interes": i, "necesidad": n, "franja": f, "semestre": 1}, 3, modelo, catalogo)
        sin_error += 1
        tops.append(r["recomendados"][0]["compatibilidad"])
        bajo_umbral += any("supera" in w for w in r["advertencias"])
    casos = [{"caso": "Todos los perfiles posibles (semestre 1)", "resultado":
              f"{sin_error}/{total} sin error; top-1 entre {min(tops):.2f} y {max(tops):.2f}; "
              f"{bajo_umbral} con aviso de baja compatibilidad (<{UMBRAL_AVISO:.0%})"}]
    base = {"carrera": "Psicología", "interes": "Salud y bienestar", "necesidad": "Cálculo", "franja": "Noche"}
    for s in (0, 1, 2, 3, 9, 10, 1.5, True, "1", None):
        try:
            r = recomendar_mentores({**base, "semestre": s}, 3, modelo, catalogo)
            res = f"OK ({r['n_candidatos']} candidatos); avisos: {len(r['advertencias'])}"
        except EntradaInvalida as e:
            res = "BLOQUEADO: " + str(e)[:90]
        casos.append({"caso": f"semestre={s!r}", "resultado": res})
    pd.DataFrame(casos).to_csv(f"{CARPETA_RESULTADOS}/casos_limite.csv", index=False)
    print("\nCasos límite:\n", pd.DataFrame(casos).to_string(index=False))

    # Figura
    fig, ax = plt.subplots(figsize=(7, 4))
    w = 0.2
    for j, (s, nombre) in enumerate(nombres.items()):
        sub = mr[mr["estrategia"] == nombre]
        ax.bar(np.arange(len(KS)) + j * w, sub["precision_k"], w, label=nombre)
    ax.set_xticks(np.arange(len(KS)) + 1.5 * w); ax.set_xticklabels([f"top-{k}" for k in KS])
    ax.set_ylabel("Precisión@k (pares compatibles)"); ax.set_title("Calidad del ranking en estudiantes nuevos (datos sintéticos)")
    ax.set_ylim(0, 1.0); ax.legend(fontsize=7, ncol=2, loc="upper center"); plt.tight_layout(); plt.savefig(f"{CARPETA_RESULTADOS}/ranking.png", dpi=150)
    print("\nArchivos guardados en", CARPETA_RESULTADOS)


if __name__ == "__main__":
    main()
