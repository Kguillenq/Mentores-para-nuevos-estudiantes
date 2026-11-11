# Recomendador de mentores universitarios (Proyecto Integrador DSI · EVAL-01)

Prototipo que, a partir del perfil de un estudiante de 1.º–2.º semestre, ordena a los mentores de semestres superiores
según su compatibilidad y explica los motivos. Interfaz web (HTML + CSS + JS); modelo: **regresión logística** en un `Pipeline` de scikit-learn.

> ⚠️ **Datos sintéticos.** No hay datos personales. La etiqueta `compatible` se simula con una regla definida por el equipo
> más ruido. Las probabilidades NO miden el éxito real de una mentoría. Ver `docs/limitaciones_riesgos.md`.

## Problema, usuarios y alcance
- **Problema:** los estudiantes de 1.º–2.º semestre necesitan elegir un mentor de semestres superiores, y hoy esa elección se hace sin criterio sistemático (por conocidos o al azar). El sistema ordena a los mentores por compatibilidad (carrera, interés, necesidad académica, franja horaria y diferencia de semestres) para apoyar esa decisión; la coordinación del programa puede usarlo para orientar asignaciones.
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
| `validar.py` | Métricas de ranking, líneas base, coeficientes, errores por grupo y casos límite |
| `exportar_web.py` | Exporta el modelo y el catálogo a `docs/js/modelo.js` para la interfaz web |
| `diagrama.py` | Genera el diagrama de componentes (`resultados/diagrama_componentes.png`) |
| `test_recomendador.py`, `test_app_y_datos.py` | Pruebas automáticas (`pytest`): validación, inferencia y datos sintéticos |
| `docs/` (dentro de `mentores/`) | Datos, limitaciones y riesgos, bitácora de validación, declaración de uso de IA |
| `resultados/` | Salidas reales de la última ejecución: CSV de métricas, gráficos y logs (`log_*.txt`) |
| `docs/` (en la raíz del repositorio) | Interfaz web (`index.html`, `css/`, `js/`). Ver la sección «Sitio web» |

## Arquitectura (flujo de datos)
```
Formulario web ──► validación de entrada ──► Regresión logística (coeficientes de modelo.js) ──► top-k + motivos
(docs/index.html)   (error: no calcula)       ▲ catálogo de mentores (en modelo.js)             (ranking + avisos)
```
El modelo se entrena fuera de línea con `entrenar.py` y se exporta a la web con `exportar_web.py`.
El backend en Python (`recomendador.py`) hace la misma validación e inferencia y se usa para las pruebas y la validación.

## Requisitos y ejecución (Python 3.10+)
Desde la carpeta `mentores_recomendador_completo/mentores/`:
```bash
pip install -r requirements.txt
python entrenar.py      # genera datos sintéticos, compara modelos y guarda el modelo y el catálogo
python validar.py       # genera resultados/ (métricas, coeficientes, errores, casos límite, gráfico)
python diagrama.py      # genera resultados/diagrama_componentes.png
pytest -q               # pruebas automáticas (19)
python exportar_web.py  # actualiza docs/js/modelo.js con el modelo entrenado
```
Luego abre `docs/index.html` (carpeta raíz del repositorio) en el navegador.
Todo es reproducible: semilla fija (`SEMILLA = 42` en `config.py`).

## Resultados
Los resultados salen de ejecutar `entrenar.py` y `validar.py` (carpeta `resultados/`). Resumen y análisis: `docs/bitacora_validacion.md`.
Resumen: AUC 0.732 (validación cruzada agrupada), precisión@3 de 0.752 frente a 0.326 del azar y 0.721 de contar coincidencias. Con datos sintéticos esto solo muestra que el pipeline aprende la regla simulada.
Datos y su generación: `docs/datos.md`. Diagrama: `resultados/diagrama_componentes.png`.

## Uso de IA generativa
Ver `docs/declaracion_ia.md`.

## Sitio web (interfaz)
La carpeta [`docs/`](docs/) de la raíz contiene la **interfaz web** (HTML + CSS + JS, sin servidor ni inicio de sesión). Sigue el mismo contrato que el backend:
el estudiante elige **carrera, área de interés, necesidad académica, franja horaria y semestre** y la página muestra los mentores con mayor
**compatibilidad**, junto con los motivos (misma carrera, comparte interés, puede reforzar la necesidad, misma franja).

- **Es el mismo modelo, no una maqueta:** `mentores/exportar_web.py` exporta los coeficientes de la regresión logística y el catálogo de mentores a `docs/js/modelo.js`;
  `docs/js/app.js` calcula la probabilidad con esos coeficientes. Se comprobó contra `recomendar_mentores()` en 750 perfiles × 10 mentores: mismos mentores, mismo orden, mismos motivos y misma compatibilidad.
- **Ver en local:** abrir `docs/index.html` o ejecutar `python -m http.server 8000 --directory docs` y entrar a http://localhost:8000
- **Si reentrenas el modelo** (`python entrenar.py`), vuelve a ejecutar `python exportar_web.py` (desde `mentores_recomendador_completo/mentores/`) para actualizar la web.
- **Publicar (GitHub Pages):** *Settings → Pages → Source: Deploy from a branch → Branch: `main` / carpeta `/docs`* → Save. Queda en `https://kguillenq.github.io/Mentores-para-nuevos-estudiantes/`.
- Detalles de la interfaz: [`docs/README-prototipo.md`](docs/README-prototipo.md).
