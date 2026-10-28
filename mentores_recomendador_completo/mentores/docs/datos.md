# Datos: origen, generación y limitaciones

## Origen y licencia
- **No se usa ningún dataset externo para entrenar.** Todos los datos se generan con `datos.py` (semilla `SEMILLA = 42` en `config.py`), por lo que no hay licencia de terceros ni datos personales.
- Se evaluó y **descartó** el dataset docente de mentores (`mentors_dataset.csv`, https://zenodo.org/records/13942111) porque solo describe mentores: no trae estudiantes ni resultados de emparejamiento, así que no permite aprender qué mentor le conviene a qué estudiante. [El equipo debe confirmar la condición de uso que figura en esa página de Zenodo si lo citan en el informe.]

## Cómo se generan
| Elemento | Cantidad | Cómo |
|---|---|---|
| Mentores (catálogo) | 60 | Carrera, interés, especialidad y franja al azar de los vocabularios de `config.py`; semestre 5 a 10 |
| Estudiantes | 500 | Mismos vocabularios; semestre 1 o 2 |
| Pares estudiante–mentor | 6.000 | 12 mentores al azar por estudiante |
| Etiqueta `compatible` (0/1) | 6.000 | **Simulada**: regla del equipo (`COEF_REGLA`) + ruido normal (σ = 0.6) y muestreo con probabilidad logística |

Regla simulada (parte determinista): `z = −1.4 + 1.3·misma_carrera + 0.9·mismo_interes + 1.6·cubre_necesidad + 0.8·misma_franja − 0.10·dif_semestres`.

## Preparación y partición
- Atributos del par (`modelo.crear_atributos`): `misma_carrera`, `mismo_interes`, `cubre_necesidad`, `misma_franja` (0/1) y `dif_semestres` (semestre del mentor − semestre del estudiante), escalado con `StandardScaler`. Se calculan dentro del `Pipeline`, igual en entrenamiento e inferencia.
- Comparación de modelos: validación cruzada de 5 particiones **agrupada por estudiante** (`GroupKFold`) para evitar fuga de información entre pares del mismo estudiante.
- Referencia final: partición 80/20 **por estudiante** (`GroupShuffleSplit`). El modelo que se guarda se reentrena con todos los pares.
- Validación del ranking (`validar.py`): 300 estudiantes nuevos con otra semilla, contra los 60 mentores.
- Proporción de pares compatibles: ≈ 0.31 en entrenamiento y 0.314 en el conjunto de prueba del ranking (clase minoritaria).

## Limitaciones
- La etiqueta no es un resultado real: el modelo aprende la regla del equipo, no el éxito de una mentoría.
- Estudiantes y mentores se distribuyen de manera uniforme y al azar; en la realidad habría carreras y franjas desbalanceadas.
- No hay datos personales ni sensibles en el proyecto. Con datos reales se requeriría autorización y anonimización.
