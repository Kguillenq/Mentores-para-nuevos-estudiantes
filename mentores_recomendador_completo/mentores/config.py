"""Constantes compartidas: vocabularios del contrato y rutas."""
SEMILLA = 42

CARRERAS = ["Ingeniería Informática", "Ingeniería Comercial", "Psicología", "Enfermería", "Derecho"]
INTERESES = ["Datos e IA", "Desarrollo web", "Emprendimiento", "Salud y bienestar", "Investigación"]
NECESIDADES = ["Cálculo", "Programación", "Estadística", "Técnicas de estudio", "Redacción académica"]
FRANJAS = ["Mañana", "Tarde", "Noche"]

COLUMNAS_PAR = ["est_carrera", "est_interes", "est_necesidad", "est_franja", "est_semestre",
                "men_carrera", "men_interes", "men_especialidad", "men_franja", "men_semestre"]
ATRIBUTOS_BIN = ["misma_carrera", "mismo_interes", "cubre_necesidad", "misma_franja"]
ATRIBUTOS_NUM = ["dif_semestres"]
ATRIBUTOS = ATRIBUTOS_BIN + ATRIBUTOS_NUM

# Regla SIMULADA que genera la etiqueta (parte determinista). Se usa para generar datos
# y para comprobar si el modelo la recupera (solo es posible porque los datos son sintéticos).
COEF_REGLA = {"intercepto": -1.4, "misma_carrera": 1.3, "mismo_interes": 0.9,
              "cubre_necesidad": 1.6, "misma_franja": 0.8, "dif_semestres": -0.10}
RUIDO_REGLA = 0.6

RUTA_MODELO = "modelo_recomendador_mentores.joblib"
RUTA_CATALOGO = "catalogo_mentores.csv"
CARPETA_RESULTADOS = "resultados"

SEM_ENTRENAMIENTO = (1, 2)   # semestres de estudiantes vistos al entrenar
SEM_MIN_EST = 1
K_MAX = 10
UMBRAL_AVISO = 0.5

LIMITACION = ("La compatibilidad es una probabilidad estimada por un modelo entrenado con datos SINTÉTICOS: "
              "refleja la regla que definió el equipo, no resultados reales de mentorías. "
              "Es una ayuda para ordenar opciones, no una garantía.")
