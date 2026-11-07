# Bitácora de validación

Ejecución: 28-10-2026 · Python 3.13 · scikit-learn 1.9.1, pandas 3.0.5, numpy 2.5.3, gradio 6.31.0 · semilla 42.
Los números salen de `resultados/` (logs completos en `resultados/log_entrenar.txt`, `log_validar.txt`, `log_pytest.txt`).
**El equipo debe volver a ejecutar `entrenar.py` y `validar.py` en su propio equipo y confirmar que los números coinciden** (la semilla es fija; si usan otras versiones de las librerías, pueden variar en decimales) antes de entregar.

## 1. Comparación de modelos (`resultados/comparacion_modelos.csv`)
- Protocolo: validación cruzada de 5 particiones **agrupada por estudiante** (un mismo estudiante nunca está a la vez en entrenamiento y prueba). 6.000 pares.

| Modelo | AUC media | AUC desv. | Accuracy | F1 |
|---|---|---|---|---|
| Regresión logística | 0.7319 | 0.0049 | 0.7330 | 0.4513 |
| Gradient Boosting | 0.7244 | 0.0052 | 0.7272 | 0.4337 |
| Random Forest | 0.7225 | 0.0055 | 0.7267 | 0.4319 |
| Árbol de decisión (prof. 4) | 0.7208 | 0.0043 | 0.7257 | 0.4638 |
| Línea base (clase mayoritaria) | 0.5000 | 0.0000 | 0.6860 | 0.0000 |

- Decisión: **regresión logística**. Tiene el mejor AUC, es la más simple y sus coeficientes se pueden explicar (cada atributo suma o resta a la compatibilidad). Las diferencias con los otros modelos son pequeñas (≈0.01 de AUC, similar a la desviación entre particiones), así que la simplicidad y la explicabilidad pesan en la elección. El árbol tiene un F1 algo mayor, pero peor AUC.
- La exactitud sola engaña: la línea base que siempre dice "no compatible" ya logra 0.686 de accuracy porque solo ~31 % de los pares son compatibles; por eso se miran también AUC y F1.
- Modelo final en una partición de prueba por estudiante: accuracy 0.734 · F1 0.421 · AUC 0.735 (coherente con la validación cruzada).

## 2. Ranking vs. líneas base (`resultados/metricas_ranking.csv`, `resultados/ranking.png`)
300 estudiantes nuevos (semilla distinta a la de entrenamiento), cada uno contra los 60 mentores. Proporción de pares compatibles en prueba: 0.314.

| Estrategia | Precisión@1 | Precisión@3 | Precisión@5 |
|---|---|---|---|
| Azar | 0.333 | 0.326 | 0.329 |
| Contar coincidencias (sin modelo) | 0.800 | 0.721 | 0.668 |
| **Regresión logística** | **0.820** | **0.752** | **0.706** |
| Regla real (cota superior) | 0.837 | 0.758 | 0.700 |

- Interpretación: el modelo supera claramente al azar (≈ +0.42 en precisión@3) y supera a "contar coincidencias" por una diferencia pequeña (≈ +0.03 en precisión@3). Queda muy cerca de la regla real, que es la mejor posible. Con datos sintéticos esto era esperable: la regla que genera la etiqueta es casi "contar coincidencias con pesos", así que la ventaja del modelo es el peso de cada atributo y el desempate por diferencia de semestres.
- Con k = 5 la regla real (0.700) queda levemente bajo el modelo (0.706): es una diferencia dentro del ruido de la muestra de 300 estudiantes, no una mejora real del modelo sobre la regla.

## 3. Recuperación de la regla simulada (`resultados/coeficientes.csv`)

| Atributo | Regla real | Aprendido |
|---|---|---|
| misma_carrera | 1.3 | 1.189 |
| mismo_interes | 0.9 | 0.870 |
| cubre_necesidad | 1.6 | 1.441 |
| misma_franja | 0.8 | 0.728 |
| dif_semestres | −0.10 | −0.115 |
| intercepto | −1.4 | −1.145 |

- Los aprendidos conservan el orden de importancia (necesidad > carrera > interés > franja). Son algo menores en valor absoluto porque la etiqueta tiene ruido (se añade un ruido aleatorio y luego se muestrea la etiqueta), lo que atenúa los coeficientes estimados. Esto solo se puede comprobar porque los datos son sintéticos.
- El top-1 del modelo coincide con el de la regla real en 92.7 % de los estudiantes.

## 4. Análisis de errores (`resultados/errores_por_grupo.csv`)
- Se comparó la precisión@3 del modelo con la de la regla real por carrera, necesidad y franja del estudiante. La brecha máxima es 0.013 (necesidad = Estadística; después Ingeniería Informática, Ingeniería Comercial, Cálculo y franja Noche).
- No hay un grupo donde el modelo falle de forma sistemática. La precisión absoluta sí varía entre grupos (por ejemplo, 0.68 en Ingeniería Comercial y en la franja Noche, frente a 0.80 en Estadística). Posible explicación: con pocos mentores que coincidan en esos perfiles en un catálogo aleatorio de 60, hay menos candidatos realmente compatibles. Es una hipótesis, no se probó por separado.
- Cada grupo tiene entre ≈50 y ≈90 estudiantes de prueba, así que diferencias de ~0.01 no son concluyentes.

## 5. Casos límite (`resultados/casos_limite.csv`) y pruebas (`pytest -q`)
- Los 375 perfiles posibles con semestre 1 (5×5×5×3) se ejecutan sin error; la compatibilidad del top-1 va de 0.62 a 0.93 y ningún perfil activa el aviso de "baja compatibilidad" (< 50 %).
- Se **bloquean** (el modelo no se ejecuta): semestre 0, semestre 10, 1.5, `True`, `"1"` y `None`.
- Se ejecutan con **advertencia** de extrapolación: semestres 3 y 9 (el modelo solo vio 1.º y 2.º). Con semestre 9 quedan solo 6 candidatos.
- `pytest -q`: **22 pruebas pasan** (entradas inválidas nunca llegan al modelo, `k` inválido, la inferencia no modifica el modelo y es determinista, ranking ordenado y con mentores de semestre superior, advertencia de extrapolación, función de la interfaz Gradio y reproducibilidad de los datos sintéticos).

## 6. Qué NO demuestra esta validación
- Que las recomendaciones funcionen con estudiantes reales: los datos y la etiqueta son sintéticos.
- Que el modelo sea mejor que una heurística simple en la práctica: la ventaja sobre "contar coincidencias" es pequeña incluso en datos sintéticos.
- Que el sistema escale o sea seguro para producción (sin autenticación ni pruebas de carga).
