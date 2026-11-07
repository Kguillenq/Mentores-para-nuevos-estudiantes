"""Atributos del par estudiante-mentor y construcción del pipeline."""
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from config import ATRIBUTOS_NUM


def crear_atributos(pares: pd.DataFrame) -> pd.DataFrame:
    """Convierte cada par estudiante-mentor en atributos de compatibilidad (sin parámetros aprendidos)."""
    return pd.DataFrame({
        "misma_carrera":   (pares["est_carrera"] == pares["men_carrera"]).astype(int),
        "mismo_interes":   (pares["est_interes"] == pares["men_interes"]).astype(int),
        "cubre_necesidad": (pares["est_necesidad"] == pares["men_especialidad"]).astype(int),
        "misma_franja":    (pares["est_franja"] == pares["men_franja"]).astype(int),
        "dif_semestres":   (pares["men_semestre"] - pares["est_semestre"]).astype(float),
    }, index=pares.index)


def construir_pipeline(clasificador=None) -> Pipeline:
    """Pipeline completo: atributos -> escalado de lo numérico -> clasificador (por defecto, regresión logística)."""
    return Pipeline([
        ("atributos", FunctionTransformer(crear_atributos)),
        ("prep", ColumnTransformer([("num", StandardScaler(), ATRIBUTOS_NUM)], remainder="passthrough")),
        ("clf", clasificador if clasificador is not None else LogisticRegression(max_iter=1000)),
    ])
