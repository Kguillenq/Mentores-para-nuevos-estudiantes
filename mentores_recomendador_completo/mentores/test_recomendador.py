"""Pruebas automáticas.  Uso:  pytest -q   (requiere haber ejecutado antes python entrenar.py)"""
import joblib
import pytest

from recomendador import EntradaInvalida, cargar_recursos, recomendar_mentores

MODELO, CATALOGO = cargar_recursos()
VALIDO = {"carrera": "Ingeniería Informática", "interes": "Datos e IA",
          "necesidad": "Estadística", "franja": "Tarde", "semestre": 1}


class ModeloCentinela:
    """Falla si alguien intenta predecir o reajustar: prueba que la validación bloquea ANTES del modelo."""
    def predict_proba(self, *a, **k): raise AssertionError("El modelo se ejecutó con una entrada inválida")
    def fit(self, *a, **k): raise AssertionError("Se intentó reajustar el modelo")


@pytest.mark.parametrize("malo", [
    {}, "texto", {**VALIDO, "extra": 1}, {**VALIDO, "carrera": "Medicina"}, {**VALIDO, "carrera": 123},
    {**VALIDO, "semestre": 0}, {**VALIDO, "semestre": 10}, {**VALIDO, "semestre": 1.5},
    {**VALIDO, "semestre": True}, {**VALIDO, "semestre": "1"},
    {c: v for c, v in VALIDO.items() if c != "franja"},
])
def test_entrada_invalida_no_llega_al_modelo(malo):
    with pytest.raises(EntradaInvalida):
        recomendar_mentores(malo, 3, ModeloCentinela(), CATALOGO)


@pytest.mark.parametrize("k", [0, 11, 2.5, True])
def test_k_invalido(k):
    with pytest.raises(EntradaInvalida):
        recomendar_mentores(VALIDO, k, ModeloCentinela(), CATALOGO)


def test_inferencia_no_modifica_el_modelo_y_es_determinista():
    antes = joblib.hash(MODELO)
    r1 = recomendar_mentores(VALIDO, 5, MODELO, CATALOGO)
    r2 = recomendar_mentores(VALIDO, 5, MODELO, CATALOGO)
    assert joblib.hash(MODELO) == antes
    assert r1 == r2


def test_ranking_ordenado_y_mentores_de_semestre_superior():
    r = recomendar_mentores(VALIDO, 5, MODELO, CATALOGO)
    comp = [m["compatibilidad"] for m in r["recomendados"]]
    assert comp == sorted(comp, reverse=True) and len(comp) == 5
    assert all(m["semestre"] > VALIDO["semestre"] for m in r["recomendados"])
    assert all(0 <= c <= 1 for c in comp)


def test_advertencia_fuera_del_rango_de_entrenamiento():
    r = recomendar_mentores({**VALIDO, "semestre": 4}, 2, MODELO, CATALOGO)
    assert any("extrapolación" in a for a in r["advertencias"])
