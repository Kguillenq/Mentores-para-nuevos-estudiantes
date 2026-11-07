"""Interfaz Gradio del recomendador de mentores.  Uso:  python app.py   (abre http://127.0.0.1:7860)"""
import gradio as gr
import pandas as pd

from config import CARRERAS, FRANJAS, INTERESES, K_MAX, LIMITACION, NECESIDADES
from recomendador import EntradaInvalida, cargar_recursos, recomendar_mentores

MODELO, CATALOGO = cargar_recursos()   # carga única al iniciar; no se reentrena nunca aquí
COLUMNAS_TABLA = ["Posición", "Mentor", "Compatibilidad", "Carrera", "Semestre", "Interés", "Especialidad",
                  "Franja", "Motivos"]


def _entero(v):
    """Gradio puede entregar 3.0; se convierte a int solo si es un entero exacto (si no, la validación lo rechaza)."""
    return int(v) if isinstance(v, float) and v.is_integer() else v


def recomendar(carrera, interes, necesidad, franja, semestre, k):
    entrada = {"carrera": carrera, "interes": interes, "necesidad": necesidad,
               "franja": franja, "semestre": _entero(semestre)}
    try:
        r = recomendar_mentores(entrada, k=_entero(k), modelo=MODELO, catalogo=CATALOGO)
    except EntradaInvalida as e:
        return pd.DataFrame(columns=COLUMNAS_TABLA), f"### ❌ Entrada no válida\n{str(e).replace(' | ', chr(10) + '- ')}"
    filas = [[i, m["mentor_id"], f"{m['compatibilidad']:.1%}", m["carrera"], m["semestre"], m["interes"],
              m["especialidad"], m["franja"], "; ".join(m["motivos"])] for i, m in enumerate(r["recomendados"], 1)]
    msg = f"### ✅ {len(filas)} mentores recomendados de {r['n_candidatos']} candidatos\n"
    if r["advertencias"]:
        msg += "\n".join(f"- ⚠️ {a}" for a in r["advertencias"]) + "\n"
    msg += f"\n_{r['limitacion']}_"
    return pd.DataFrame(filas, columns=COLUMNAS_TABLA), msg


with gr.Blocks(title="Recomendador de mentores") as demo:
    gr.Markdown("# Recomendador de mentores universitarios\n"
                "Indica tu perfil y el sistema ordena a los mentores de semestres superiores según su compatibilidad.\n\n"
                f"> **Prototipo académico con datos sintéticos.** {LIMITACION}")
    with gr.Row():
        with gr.Column():
            carrera = gr.Dropdown(CARRERAS, value=CARRERAS[0], label="Carrera")
            interes = gr.Dropdown(INTERESES, value=INTERESES[0], label="Área de interés")
            necesidad = gr.Dropdown(NECESIDADES, value=NECESIDADES[0], label="Necesidad académica")
            franja = gr.Dropdown(FRANJAS, value=FRANJAS[1], label="Franja horaria")
            semestre = gr.Number(value=1, precision=0, label="Semestre que cursas")
            k = gr.Slider(1, K_MAX, value=3, step=1, label="Cantidad de mentores (k)")
            boton = gr.Button("Recomendar mentores", variant="primary")
        with gr.Column(scale=2):
            estado = gr.Markdown()
            tabla = gr.Dataframe(headers=COLUMNAS_TABLA, interactive=False, wrap=True)
    boton.click(recomendar, [carrera, interes, necesidad, franja, semestre, k], [tabla, estado], api_name="recomendar")

if __name__ == "__main__":
    demo.launch()
