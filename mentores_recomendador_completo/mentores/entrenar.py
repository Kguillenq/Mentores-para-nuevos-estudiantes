"""Entrena y guarda el pipeline + catálogo. Compara modelos con validación cruzada AGRUPADA por estudiante.

Uso:  python entrenar.py
Salidas: modelo_recomendador_mentores.joblib, catalogo_mentores.csv, resultados/comparacion_modelos.csv
"""
import os

import joblib
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import GroupKFold, GroupShuffleSplit, cross_validate
from sklearn.tree import DecisionTreeClassifier

from config import CARPETA_RESULTADOS, COLUMNAS_PAR, RUTA_CATALOGO, RUTA_MODELO, SEMILLA
from datos import generar_datos_entrenamiento
from modelo import construir_pipeline

CANDIDATOS = {
    "Línea base (clase mayoritaria)": DummyClassifier(strategy="most_frequent"),
    "Regresión logística": LogisticRegression(max_iter=1000),
    "Árbol de decisión (prof. 4)": DecisionTreeClassifier(max_depth=4, random_state=SEMILLA),
    "Random Forest": RandomForestClassifier(n_estimators=200, random_state=SEMILLA, n_jobs=-1),
    "Gradient Boosting": HistGradientBoostingClassifier(random_state=SEMILLA),
}


def comparar_modelos(X, y, grupos) -> pd.DataFrame:
    """Compara con GroupKFold: un mismo estudiante nunca está en entrenamiento y prueba a la vez."""
    filas = []
    for nombre, clf in CANDIDATOS.items():
        r = cross_validate(construir_pipeline(clf), X, y, groups=grupos, cv=GroupKFold(n_splits=5),
                           scoring=["roc_auc", "accuracy", "f1"])
        filas.append({"modelo": nombre,
                      "auc_media": r["test_roc_auc"].mean(), "auc_desv": r["test_roc_auc"].std(),
                      "accuracy_media": r["test_accuracy"].mean(), "f1_media": r["test_f1"].mean()})
    return pd.DataFrame(filas).sort_values("auc_media", ascending=False).round(4)


def main():
    os.makedirs(CARPETA_RESULTADOS, exist_ok=True)
    mentores, pares = generar_datos_entrenamiento()
    X, y, grupos = pares[COLUMNAS_PAR], pares["compatible"], pares["est_id"]

    tabla = comparar_modelos(X, y, grupos)
    tabla.to_csv(f"{CARPETA_RESULTADOS}/comparacion_modelos.csv", index=False)
    print("Comparación de modelos (validación cruzada agrupada por estudiante):")
    print(tabla.to_string(index=False))

    # Partición final por ESTUDIANTE (no por par) para una referencia en prueba
    tr, te = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=SEMILLA).split(X, y, grupos))
    pipeline = construir_pipeline().fit(X.iloc[tr], y.iloc[tr])
    p = pipeline.predict_proba(X.iloc[te])[:, 1]
    print(f"\nModelo final (regresión logística) en prueba -> accuracy: {accuracy_score(y.iloc[te], p >= 0.5):.3f} "
          f"| F1: {f1_score(y.iloc[te], p >= 0.5):.3f} | AUC: {roc_auc_score(y.iloc[te], p):.3f}")

    # Se guarda el modelo reentrenado con todos los pares (el protocolo de evaluación ya se hizo arriba)
    pipeline = construir_pipeline().fit(X, y)
    joblib.dump(pipeline, RUTA_MODELO)
    mentores.to_csv(RUTA_CATALOGO, index=False)
    print("Guardados:", RUTA_MODELO, "y", RUTA_CATALOGO)


if __name__ == "__main__":
    main()
