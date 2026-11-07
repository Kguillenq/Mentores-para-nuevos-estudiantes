"""Exporta el modelo entrenado y el catálogo a docs/js/modelo.js, para que la página web calcule
EXACTAMENTE las mismas recomendaciones que el backend, sin necesidad de un servidor.

Uso (después de `python entrenar.py`):  python exportar_web.py
Salida: ../../docs/js/modelo.js   (se vuelve a generar cada vez que se reentrena el modelo)
"""
import json
import os

from config import (ATRIBUTOS_BIN, ATRIBUTOS_NUM, CARRERAS, FRANJAS, INTERESES, K_MAX, LIMITACION, NECESIDADES,
                    SEM_ENTRENAMIENTO, SEM_MIN_EST, UMBRAL_AVISO)
from recomendador import cargar_recursos

DESTINO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "js", "modelo.js")


def main():
    modelo, catalogo = cargar_recursos()
    esc = modelo.named_steps["prep"].named_transformers_["num"]
    clf = modelo.named_steps["clf"]
    nombres = ATRIBUTOS_NUM + ATRIBUTOS_BIN          # mismo orden de columnas que ve el clasificador
    datos = {
        "carreras": CARRERAS, "intereses": INTERESES, "necesidades": NECESIDADES, "franjas": FRANJAS,
        "k_max": K_MAX, "umbral_aviso": UMBRAL_AVISO, "sem_min_est": SEM_MIN_EST,
        "sem_entrenamiento": list(SEM_ENTRENAMIENTO), "limitacion": LIMITACION,
        "modelo": {
            "intercepto": float(clf.intercept_[0]),
            "media_dif_semestres": float(esc.mean_[0]), "desv_dif_semestres": float(esc.scale_[0]),
            "coef": {n: float(c) for n, c in zip(nombres, clf.coef_[0])},
        },
        "catalogo": catalogo.to_dict(orient="records"),
    }
    with open(DESTINO, "w", encoding="utf-8") as f:
        f.write("/* GENERADO por mentores/exportar_web.py: no editar a mano. */\n")
        f.write("window.MODELO = " + json.dumps(datos, ensure_ascii=False, indent=1) + ";\n")
    print("Escrito", os.path.normpath(DESTINO))


if __name__ == "__main__":
    main()
