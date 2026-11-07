# Interfaz web · Recomendador de mentores

Página estática que permite al estudiante de 1.º–2.º semestre **seleccionar sus categorías** y ver los **mentores con mayor compatibilidad**.
No tiene servidor, base de datos ni inicio de sesión (la autenticación está fuera del alcance del proyecto).

## Cómo ejecutarlo
Abre `index.html` con doble clic, o desde esta carpeta: `python -m http.server 8000` y entra a http://localhost:8000
(las tipografías vienen de Google Fonts; sin internet se usan fuentes del sistema).

## Flujo
1. **Tu perfil:** carrera, área de interés, necesidad académica, franja horaria, semestre (1.º o 2.º) y cuántos mentores ver (3, 5 o 10).
   Si falta alguna categoría, la página lo indica y no calcula nada (igual que `validar_entrada()` en el backend).
2. **Tus mentores:** ranking con la compatibilidad (%) de cada mentor y los motivos de la recomendación. Si el mejor mentor no supera 50 %,
   se muestra un aviso, igual que en el backend.

## Estructura
```
docs/
├── index.html        # Estructura de la página
├── css/styles.css    # Estilos y colores por categoría
└── js/
    ├── modelo.js     # GENERADO por mentores/exportar_web.py: coeficientes, vocabularios y catálogo de mentores
    └── app.js        # Pantallas y cálculo de la compatibilidad (réplica de recomendador.py)
```

## Relación con el backend
- `modelo.js` contiene el intercepto, los coeficientes y la estandarización de `dif_semestres` del `Pipeline` entrenado, además del catálogo de 60 mentores.
- `app.js` calcula `1 / (1 + e^-z)` con esos valores, ordena de mayor a menor (los empates conservan el orden del catálogo) y arma los motivos con las mismas frases que `recomendar_mentores()`.
- Si reentrenas el modelo, ejecuta `python exportar_web.py` en `mentores_recomendador_completo/mentores/` para regenerar `modelo.js`.

## Limitaciones
- Los mentores y el entrenamiento son **datos sintéticos**: la compatibilidad refleja la regla definida por el equipo, no resultados reales de mentorías.
- Esta interfaz solo recomienda: no agenda sesiones ni inscribe a nadie.
