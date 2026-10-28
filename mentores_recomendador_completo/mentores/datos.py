"""Generación de datos SINTÉTICOS (declarados como tales). No hay datos personales."""
import numpy as np
import pandas as pd

from config import (CARRERAS, COEF_REGLA, FRANJAS, INTERESES, NECESIDADES, RUIDO_REGLA, SEMILLA)
from modelo import crear_atributos


def z_regla(atributos: pd.DataFrame) -> np.ndarray:
    """Parte determinista de la regla simulada (sin ruido)."""
    c = COEF_REGLA
    return (c["intercepto"] + c["misma_carrera"] * atributos["misma_carrera"]
            + c["mismo_interes"] * atributos["mismo_interes"]
            + c["cubre_necesidad"] * atributos["cubre_necesidad"]
            + c["misma_franja"] * atributos["misma_franja"]
            + c["dif_semestres"] * atributos["dif_semestres"]).to_numpy()


def generar_catalogo(rng, n_mentores=60) -> pd.DataFrame:
    return pd.DataFrame({
        "mentor_id": [f"M-{i:03d}" for i in range(1, n_mentores + 1)],
        "carrera": rng.choice(CARRERAS, n_mentores),
        "semestre": rng.integers(5, 11, n_mentores),          # mentores de 5.º a 10.º semestre
        "interes": rng.choice(INTERESES, n_mentores),
        "especialidad": rng.choice(NECESIDADES, n_mentores),
        "franja": rng.choice(FRANJAS, n_mentores),
    })


def generar_estudiantes(rng, n=500) -> pd.DataFrame:
    return pd.DataFrame({
        "est_id": [f"E-{i:04d}" for i in range(n)],
        "carrera": rng.choice(CARRERAS, n), "interes": rng.choice(INTERESES, n),
        "necesidad": rng.choice(NECESIDADES, n), "franja": rng.choice(FRANJAS, n),
        "semestre": rng.integers(1, 3, n),                     # estudiantes nuevos: 1.º o 2.º
    })


def armar_pares(est: pd.DataFrame, mentores: pd.DataFrame, indices_mentor) -> pd.DataFrame:
    """Une cada fila de `est` con el mentor indicado (misma longitud)."""
    m = mentores.iloc[indices_mentor].reset_index(drop=True)
    e = est.reset_index(drop=True)
    return pd.DataFrame({
        "est_id": e["est_id"], "est_carrera": e["carrera"], "est_interes": e["interes"],
        "est_necesidad": e["necesidad"], "est_franja": e["franja"], "est_semestre": e["semestre"],
        "mentor_id": m["mentor_id"], "men_carrera": m["carrera"], "men_interes": m["interes"],
        "men_especialidad": m["especialidad"], "men_franja": m["franja"], "men_semestre": m["semestre"],
    })


def etiquetar(pares: pd.DataFrame, rng) -> pd.DataFrame:
    """Etiqueta SIMULADA `compatible` = regla del equipo + ruido (no es un resultado real)."""
    a = crear_atributos(pares)
    z = z_regla(a) + rng.normal(0, RUIDO_REGLA, len(a))
    pares = pares.copy()
    pares["compatible"] = (rng.random(len(a)) < 1 / (1 + np.exp(-z))).astype(int)
    return pares


def generar_datos_entrenamiento(semilla=SEMILLA, n_mentores=60, n_estudiantes=500, pares_por_estudiante=12):
    rng = np.random.default_rng(semilla)
    mentores = generar_catalogo(rng, n_mentores)
    est = generar_estudiantes(rng, n_estudiantes)
    e = est.loc[est.index.repeat(pares_por_estudiante)].reset_index(drop=True)
    idx = rng.integers(0, n_mentores, len(e))
    return mentores, etiquetar(armar_pares(e, mentores, idx), rng)
