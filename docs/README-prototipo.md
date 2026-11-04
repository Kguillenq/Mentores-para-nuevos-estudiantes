# Plataforma de mentorías universitarias · Prototipo visual

Prototipo **solo visual** de una plataforma de mentorías **grupales** para estudiantes de primer año. Cada mentor de cursos superiores dirige una clase; el estudiante indica sus intereses y preferencias y la página le muestra las clases ordenadas por afinidad, con horario, cupos e inscripción.

> Es una maqueta navegable. No tiene backend, base de datos, inicio de sesión ni modelo de recomendación entrenado. Todo el estado vive en memoria y se pierde al recargar la página.

## Cómo ejecutarlo

No requiere instalar nada ni compilar.

**Opción 1:** abre `index.html` con doble clic en tu navegador.

**Opción 2 (servidor local):** desde la carpeta del proyecto:

```bash
python -m http.server 8000
# luego abre http://localhost:8000
```

Las tipografías (DM Sans y Fraunces) se cargan desde Google Fonts; sin internet la página usa fuentes del sistema y se ve igual de funcional.

## Estructura de carpetas

```
mentorias-prototipo/
├── README.md          # Este archivo
├── index.html         # Estructura base de la página
├── css/
│   └── styles.css     # Estilos, paleta y colores por área
└── js/
    ├── data.js        # Datos de ejemplo: intereses, tipos de sesión, mentores
    └── app.js         # Lógica visual: pantallas, puntaje de afinidad, inscripción
```

## Qué hace el prototipo

1. **Tu perfil:** eliges intereses, tipo de sesión (charla de orientación, taller de proyecto o clase técnica), frecuencia de sesiones y canal de apoyo del grupo.
2. **Clases recomendadas:** ranking de clases con porcentaje de afinidad, motivos de coincidencia, horario, cupos disponibles y botón **Inscribirme en la clase** (descuenta un cupo y cambia a "Inscripción confirmada").

### Puntaje de afinidad

Es una regla simple e ilustrativa (suma 100), definida en `js/data.js` (`weights`) y calculada en `js/app.js` (`scoreMentors`):

| Criterio | Puntos |
|---|---|
| Áreas de especialidad (coincidencia con tus intereses) | 40 |
| Tipo de sesión | 30 |
| Frecuencia de sesiones | 15 |
| Canal de apoyo | 15 |

## Origen de los datos

- Los **5 mentores** (cargo, nivel, años de experiencia, especialidades, lenguaje principal, disponibilidad, tipo de mentoría y canal) son las primeras filas del dataset **Mentor Recommendation (IT Mentor-Mentee Matching)**, de Hank Carter, publicado en Zenodo: <https://zenodo.org/records/13942111>. Consulta la ficha del dataset para su licencia y condiciones de uso.
- Equivalencias con las columnas del dataset:

| Columna del dataset | Cómo se usa en la interfaz |
|---|---|
| `Position`, `Experience_Level`, `Years_of_Experience` | Perfil del mentor que dirige la clase |
| `Expertise` | Áreas de interés y etiquetas de la clase |
| `Mentoring_Preferences` | Tipo de sesión |
| `Availability` | Frecuencia de sesiones (tiempo completo = dos por semana, medio tiempo = una, freelance = flexible) |
| `Communication_Methods` | Canal de apoyo del grupo |
| `Primary_Language` | Lenguaje principal del mentor |
| `Gender` | **No se usa** para emparejar |

- **Datos de ejemplo inventados para el prototipo** (el dataset no los incluye): título de cada clase, horario, cupos totales y cupos ya ocupados.

## Limitaciones

- El dataset es del sector TI, no universitario, y no trae pares emparejados ni satisfacción. Sirve para representar perfiles, pero **no permite validar la calidad de las recomendaciones**.
- El puntaje no es un modelo de machine learning: es una regla de ponderación para mostrar cómo se vería el ranking.
- No hay filtro por carrera porque el dataset no tiene esa columna.

## Cómo personalizarlo

- **Cambiar colores:** edita las variables al inicio de `css/styles.css` (`:root` y las clases `.cat-tech`, `.cat-robot`, `.cat-vr`, `.cat-mkt`).
- **Agregar o editar mentores y clases:** modifica el arreglo `mentors` en `js/data.js`. Cada mentor usa los `id` de `interests`, `needs`, `frequencies` y `channels`.
- **Agregar un área de interés:** añade una entrada en `interests` con su `cat` (color) y úsala en `expertise` de algún mentor.
- **Ajustar el puntaje:** cambia `weights` en `js/data.js`; deben sumar 100.

## Próximos pasos posibles

- Cargar los 4.000 mentores desde el CSV real en lugar de 5 perfiles fijos.
- Filtros adicionales (carrera, nivel del mentor, horario).
- Backend con inscripciones reales, cupos y autenticación.
- Reemplazar la regla de ponderación por un modelo evaluado con datos de emparejamientos reales.
