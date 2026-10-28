# Recomendador de mentores universitarios (Proyecto Integrador DSI · EVAL-01)

Prototipo que, a partir del perfil de un estudiante de 1.º–2.º semestre, ordena a los mentores de semestres superiores
según su compatibilidad y explica los motivos. Interfaz web con **Gradio**; modelo: **regresión logística** en un `Pipeline` de scikit-learn.

> ⚠️ **Datos sintéticos.** No hay datos personales. La etiqueta `compatible` se simula con una regla definida por el equipo
> más ruido. Las probabilidades NO miden el éxito real de una mentoría. Ver `docs/limitaciones_riesgos.md`.

## Problema, usuarios y alcance
- **Problema:** los estudiantes de 1.º–2.º semestre necesitan elegir un mentor de semestres superiores, y hoy esa elección se hace sin criterio sistemático (por conocidos o al azar). El sistema ordena a los mentores por compatibilidad (carrera, interés, necesidad académica, franja horaria y diferencia de semestres) para apoyar esa decisión; la coordinación del programa puede usarlo para orientar asignaciones. [El equipo debe confirmar que describe el contexto real de su caso.]
- **Usuarios:** estudiantes de primer año y coordinación del programa.
- **Alcance del prototipo:** recomendar top-k mentores con motivos. Fuera de alcance: agendar sesiones, datos reales, autenticación.

## Estructura
| Archivo | Rol |
|---|---|
| `config.py` | Vocabularios del contrato, regla simulada, constantes |
| `datos.py` | Generación de datos sintéticos (semilla fija) |
| `modelo.py` | Atributos del par estudiante–mentor y `Pipeline` |
| `entrenar.py` | Compara modelos (CV agrupada por estudiante), entrena y guarda `.joblib` + catálogo |
| `recomendador.py` | Validación de entrada + inferencia (`predict_proba`, nunca `fit`) |
| `app.py` | Interfaz Gradio (también expone una API: `api_name="recomendar"`) |
| `validar.py` | Métricas de ranking, líneas base, coeficientes, errores por grupo y casos límite |
| `diagrama.py` | Genera el diagrama de componentes (`resultados/diagrama_componentes.png`) |
| `test_recomendador.py`, `test_app_y_datos.py` | Pruebas automáticas (`pytest`): validación, inferencia, interfaz Gradio y datos |
| `docs/` | Datos, limitaciones y riesgos, bitácora de validación, declaración de uso de IA |
| `resultados/` | Salidas reales de la última ejecución: CSV de métricas, gráficos y logs (`log_*.txt`) |

## Arquitectura (flujo de datos)
```
Formulario Gradio ──► validar_entrada() ──► Pipeline (atributos → escalado → regresión logística) ──► top-k + motivos
 (app.py)             (error: bloquea)        ▲ catálogo de mentores (catalogo_mentores.csv)          (tabla + avisos)
```

## Requisitos y ejecución (Python 3.10+)
```bash
pip install -r requirements.txt
python entrenar.py      # genera datos sintéticos, compara modelos y guarda el modelo y el catálogo
python validar.py       # genera resultados/ (métricas, coeficientes, errores, casos límite, gráfico)
python diagrama.py      # genera resultados/diagrama_componentes.png
pytest -q               # pruebas automáticas (22)
python app.py           # abre http://127.0.0.1:7860
```
En Google Colab: sube la carpeta, ejecuta `!pip install -r requirements.txt`, `!python entrenar.py` y luego
`!python app.py` (Gradio mostrará un enlace). Todo es reproducible: semilla fija (`SEMILLA = 42` en `config.py`).

## Resultados
Los resultados salen de ejecutar `entrenar.py` y `validar.py` (carpeta `resultados/`). Resumen y análisis: `docs/bitacora_validacion.md`.
Resumen: AUC 0.732 (validación cruzada agrupada), precisión@3 de 0.752 frente a 0.326 del azar y 0.721 de contar coincidencias. Con datos sintéticos esto solo muestra que el pipeline aprende la regla simulada.
Datos y su generación: `docs/datos.md`. Diagrama: `resultados/diagrama_componentes.png`.

## Uso de IA generativa
Ver `docs/declaracion_ia.md`. 
