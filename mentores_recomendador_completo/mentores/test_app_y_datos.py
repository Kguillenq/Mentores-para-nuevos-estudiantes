import pandas as pd

from config import COLUMNAS_PAR, SEM_ENTRENAMIENTO
from datos import generar_datos_entrenamiento

def test_datos_sinteticos_son_reproducibles_y_consistentes():
    m1, p1 = generar_datos_entrenamiento()
    m2, p2 = generar_datos_entrenamiento()
    pd.testing.assert_frame_equal(p1, p2)
    assert len(m1) == 60 and len(p1) == 500 * 12
    assert set(p1["compatible"].unique()) == {0, 1}
    assert p1["est_semestre"].between(*SEM_ENTRENAMIENTO).all()
    assert (p1["men_semestre"] > p1["est_semestre"]).all()
    assert set(COLUMNAS_PAR) <= set(p1.columns)
    assert not p1.isna().any().any()
