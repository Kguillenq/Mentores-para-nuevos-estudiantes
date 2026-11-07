"""Pruebas de la interfaz Gradio (función `recomendar`) y de los datos sintéticos.
Uso:  pytest -q   (requiere haber ejecutado antes python entrenar.py)"""
import pandas as pd

import app
from config import COLUMNAS_PAR, SEM_ENTRENAMIENTO
from datos import generar_datos_entrenamiento


def test_app_entrada_valida_devuelve_tabla_y_mensaje():
    tabla, msg = app.recomendar("Ingeniería Informática", "Datos e IA", "Estadística", "Tarde", 1, 3)
    assert list(tabla.columns) == app.COLUMNAS_TABLA
    assert len(tabla) == 3
    assert "mentores recomendados" in msg and "SINTÉTICOS" in msg


def test_app_acepta_floats_enteros_de_gradio():
    tabla, _ = app.recomendar("Psicología", "Salud y bienestar", "Cálculo", "Noche", 2.0, 5.0)
    assert len(tabla) == 5


def test_app_entrada_invalida_muestra_error_y_tabla_vacia():
    tabla, msg = app.recomendar("Psicología", "Salud y bienestar", "Cálculo", "Noche", 0, 3)
    assert tabla.empty and "Entrada no válida" in msg
    tabla, msg = app.recomendar("Psicología", "Salud y bienestar", "Cálculo", "Noche", 1.5, 3)
    assert tabla.empty and "entero" in msg


def test_datos_sinteticos_son_reproducibles_y_consistentes():
    m1, p1 = generar_datos_entrenamiento()
    m2, p2 = generar_datos_entrenamiento()
    pd.testing.assert_frame_equal(p1, p2)
    assert len(m1) == 60 and len(p1) == 500 * 12
    assert set(p1["compatible"].unique()) == {0, 1}
    assert p1["est_semestre"].between(*SEM_ENTRENAMIENTO).all()
    assert (p1["men_semestre"] > p1["est_semestre"]).all()
    assert set(COLUMNAS_PAR) <= set(p1.columns)
    assert not p1.isna().any().any()
