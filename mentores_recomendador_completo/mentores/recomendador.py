"""Integración: entrada -> validación -> pipeline guardado -> salida. La inferencia NUNCA llama a fit."""
import joblib
import numpy as np
import pandas as pd

from config import (CARRERAS, COLUMNAS_PAR, FRANJAS, INTERESES, K_MAX, LIMITACION, NECESIDADES,
                    RUTA_CATALOGO, RUTA_MODELO, SEM_ENTRENAMIENTO, SEM_MIN_EST, UMBRAL_AVISO)
from modelo import crear_atributos  # noqa: F401  (necesario para que joblib encuentre la función al cargar)

CAMPOS = ["carrera", "interes", "necesidad", "franja", "semestre"]
OPCIONES = {"carrera": CARRERAS, "interes": INTERESES, "necesidad": NECESIDADES, "franja": FRANJAS}


class EntradaInvalida(ValueError):
    """La entrada no cumple el contrato: el modelo NO se ejecuta."""


def cargar_recursos(ruta_modelo=RUTA_MODELO, ruta_catalogo=RUTA_CATALOGO):
    return joblib.load(ruta_modelo), pd.read_csv(ruta_catalogo)


def _es_entero(v):
    return isinstance(v, (int, np.integer)) and not isinstance(v, bool)


def validar_entrada(entrada, catalogo, k=3):
    """Devuelve advertencias (no bloqueantes). Lanza EntradaInvalida si hay errores."""
    errores, advertencias = [], []
    if not isinstance(entrada, dict):
        raise EntradaInvalida("La entrada debe ser un diccionario con los campos: " + ", ".join(CAMPOS))

    faltan = [c for c in CAMPOS if c not in entrada or entrada[c] in (None, "")]
    if faltan:
        errores.append(f"Faltan campos obligatorios: {faltan}")
    extra = [c for c in entrada if c not in CAMPOS]
    if extra:
        errores.append(f"Campos no reconocidos: {extra}")

    for c, opciones in OPCIONES.items():
        if c in faltan:
            continue
        v = entrada[c]
        if not isinstance(v, str):
            errores.append(f"{c} debe ser texto (recibido: {v!r}).")
        elif v not in opciones:
            errores.append(f"{c}={v!r} no es una opción válida. Opciones: {opciones}")

    sem_max = int(catalogo["semestre"].max()) - 1   # debe existir al menos un mentor de semestre superior
    if "semestre" not in faltan:
        s = entrada["semestre"]
        if not _es_entero(s):
            errores.append(f"semestre debe ser un número entero (recibido: {s!r}).")
        elif s < SEM_MIN_EST or s > sem_max:
            errores.append(f"semestre={s} no es válido: debe estar entre {SEM_MIN_EST} y {sem_max} "
                           "(tiene que existir algún mentor de semestre superior).")
        elif not (SEM_ENTRENAMIENTO[0] <= s <= SEM_ENTRENAMIENTO[1]):
            advertencias.append(f"semestre={s} está fuera del rango visto en el entrenamiento {SEM_ENTRENAMIENTO}; "
                                "la recomendación es una extrapolación.")

    if not _es_entero(k) or not (1 <= k <= K_MAX):
        errores.append(f"k debe ser un entero entre 1 y {K_MAX} (recibido: {k!r}).")

    if errores:
        raise EntradaInvalida(" | ".join(errores))
    return advertencias


def recomendar_mentores(entrada, k=3, modelo=None, catalogo=None):
    """Entrada (dict del estudiante) -> salida (dict) con top-k mentores, motivos, advertencias y limitación."""
    if modelo is None or catalogo is None:
        modelo, catalogo = cargar_recursos()
    advertencias = validar_entrada(entrada, catalogo, k)          # si hay error, se detiene aquí
    cand = catalogo[catalogo["semestre"] > entrada["semestre"]].reset_index(drop=True)
    n = len(cand)
    pares = pd.DataFrame({
        "est_carrera": [entrada["carrera"]] * n, "est_interes": [entrada["interes"]] * n,
        "est_necesidad": [entrada["necesidad"]] * n, "est_franja": [entrada["franja"]] * n,
        "est_semestre": [entrada["semestre"]] * n,
        "men_carrera": cand["carrera"], "men_interes": cand["interes"],
        "men_especialidad": cand["especialidad"], "men_franja": cand["franja"], "men_semestre": cand["semestre"],
    })[COLUMNAS_PAR]
    probs = modelo.predict_proba(pares)[:, 1]
    flags = crear_atributos(pares)
    orden = np.argsort(-probs, kind="stable")[:k]
    recomendados = []
    for i in orden:
        motivos = []
        if flags.loc[i, "misma_carrera"]:   motivos.append("misma carrera")
        if flags.loc[i, "mismo_interes"]:   motivos.append(f"comparte interés en {entrada['interes']}")
        if flags.loc[i, "cubre_necesidad"]: motivos.append(f"puede reforzar {entrada['necesidad']}")
        if flags.loc[i, "misma_franja"]:    motivos.append(f"disponible en la franja {entrada['franja']}")
        recomendados.append({
            "mentor_id": cand.loc[i, "mentor_id"], "compatibilidad": round(float(probs[i]), 3),
            "carrera": cand.loc[i, "carrera"], "semestre": int(cand.loc[i, "semestre"]),
            "interes": cand.loc[i, "interes"], "especialidad": cand.loc[i, "especialidad"],
            "franja": cand.loc[i, "franja"], "motivos": motivos or ["sin coincidencias directas"],
        })
    if recomendados[0]["compatibilidad"] < UMBRAL_AVISO:
        advertencias.append(f"Ningún mentor disponible supera {UMBRAL_AVISO:.0%} de compatibilidad; "
                            "considera ampliar la franja horaria o hablar con la coordinación.")
    return {"n_candidatos": n, "recomendados": recomendados, "advertencias": advertencias, "limitacion": LIMITACION}
