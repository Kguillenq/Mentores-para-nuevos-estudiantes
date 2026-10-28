# Limitaciones conocidas y riesgos

## Limitaciones
1. **Datos y etiqueta sintéticos:** el modelo aprende la regla que definió el equipo; las métricas no demuestran utilidad con personas reales.
2. **Cinco atributos solamente** (carrera, interés, necesidad, franja, diferencia de semestres); no incluye personalidad, rendimiento, experiencias previas, etc.
3. **Rango de entrenamiento:** estudiantes de 1.º y 2.º semestre; fuera de ese rango se emite advertencia (extrapolación).
4. **Catálogo de demostración:** 60 mentores generados; no representa la oferta real de mentores.
5. **Sin retroalimentación:** el sistema no aprende de mentorías reales ni de la satisfacción de los estudiantes.
6. **Demo local:** sin autenticación, sin persistencia, sin pruebas de carga.

## Riesgos (y mitigaciones)
| Riesgo | Detalle | Mitigación / pendiente |
|---|---|---|
| Sesgo de diseño | La regla favorece "misma carrera"; puede reducir la mentoría entre carreras | Revisar pesos con la coordinación antes de usar datos reales |
| Privacidad | Con datos reales habría datos personales/estudiantiles | El prototipo usa solo datos sintéticos; con datos reales se requiere autorización y anonimización |
| Sobreconfianza | Un % de compatibilidad puede leerse como garantía | La interfaz muestra la limitación y usa el ranking como ayuda, no como decisión |
| Seguridad | Credenciales o secretos en el repositorio | No hay claves en el proyecto; `.gitignore` excluye `.env`; revisar antes de subir |
| Licencias | Dependencias de terceros | Según los metadatos de las versiones instaladas (28-10-2026): scikit-learn, pandas, numpy y joblib: BSD-3-Clause; Gradio: Apache-2.0; pytest: MIT; matplotlib: licencia propia de matplotlib (basada en PSF). Todas permiten uso académico. El equipo debe contrastarlo con la página de cada paquete en PyPI antes del informe |
