"""Genera el diagrama de componentes en resultados/diagrama_componentes.png.  Uso:  python diagrama.py"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from config import CARPETA_RESULTADOS


def caja(ax, x, y, ancho, alto, texto, color, tam=9):
    ax.add_patch(FancyBboxPatch((x, y), ancho, alto, boxstyle="round,pad=0.05", fc=color, ec="#334155", lw=1.5))
    ax.text(x + ancho / 2, y + alto / 2, texto, ha="center", va="center", fontsize=tam)


def flecha(ax, x0, y0, x1, y1, color="#334155"):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="->", lw=2, color=color))


def main():
    os.makedirs(CARPETA_RESULTADOS, exist_ok=True)
    fig, ax = plt.subplots(figsize=(15, 5.5))
    ax.axis("off"); ax.set_xlim(0, 15); ax.set_ylim(0, 5.5)

    caja(ax, 0.2, 1.9, 2.9, 2.3, "INTERFAZ WEB\n(docs/index.html · app.js)\ncarrera · interés\nnecesidad · franja\nsemestre · k", "#dbeafe")
    caja(ax, 3.9, 1.9, 2.9, 2.3, "VALIDACIÓN\nvalidar_entrada() / app.js\nobligatorios · tipos\ncategorías · semestre · k", "#fef3c7")
    caja(ax, 7.6, 1.9, 2.9, 2.3, "MODELO (modelo.js)\natributos del par →\nStandardScaler →\nRegresión Logística\n(solo probabilidad)", "#dcfce7")
    caja(ax, 11.3, 1.9, 3.4, 2.3, "SALIDA\ntop-k mentores · compatibilidad\nmotivos · advertencias\nlimitación (ranking en la web)", "#fce7f3")
    for x in (3.15, 6.85, 10.55):
        flecha(ax, x, 3.05, x + 0.7, 3.05)

    caja(ax, 7.6, 0.15, 2.9, 0.95, "CATÁLOGO DE MENTORES\n(en modelo.js)", "#e0e7ff", 8.5)
    flecha(ax, 9.05, 1.15, 9.05, 1.9)
    flecha(ax, 5.35, 1.9, 5.35, 1.15, "#b91c1c")
    ax.text(5.35, 0.45, "Entrada inválida → no se calcula\n(el modelo NO se ejecuta)", ha="center", fontsize=8.5, color="#b91c1c")

    caja(ax, 7.6, 4.45, 7.1, 0.8, "OFFLINE: datos.py (sintéticos, semilla 42) → entrenar.py (compara 5 modelos, GroupKFold)\n"
                                  "→ modelo .joblib + catálogo → exportar_web.py → docs/js/modelo.js", "#f1f5f9", 8)
    flecha(ax, 9.05, 4.45, 9.05, 4.2, "#166534")
    ax.set_title("Recorrido: interfaz → validación → modelo → salida", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(f"{CARPETA_RESULTADOS}/diagrama_componentes.png", dpi=200)
    print("Guardado:", f"{CARPETA_RESULTADOS}/diagrama_componentes.png")


if __name__ == "__main__":
    main()

