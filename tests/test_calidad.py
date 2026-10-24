import pandas as pd
import pytest

from calidad import LoteInvalido, aplicar_reglas, leer_lote

COLUMNAS = ["comentario_id", "pedido_id", "restaurante_id", "cliente_id", "calificacion", "comentario", "fecha"]


def fila(cid, calificacion="5", comentario="Todo llegó muy rico"):
    return {"comentario_id": cid, "pedido_id": "p", "restaurante_id": "r", "cliente_id": "c",
            "calificacion": calificacion, "comentario": comentario, "fecha": "2026-09-01"}


def test_reglas_de_calidad():
    df = pd.DataFrame([
        fila("a"),
        fila("a"),                    # duplicado
        fila("b", comentario="   "),  # vacío
        fila("c", comentario="ok"),   # muy corto
        fila("d", calificacion="7"),  # calificación inválida
        fila("e", calificacion=""),   # sin calificación: se mantiene
        fila("f"),                    # mismo texto con otro id: se mantiene
    ])
    validas, excluidas = aplicar_reglas(df, min_palabras=3)
    assert list(validas["comentario_id"]) == ["a", "e", "f"]
    assert dict(zip(excluidas["comentario_id"], excluidas["motivo_exclusion"])) == {
        "a": "duplicado", "b": "comentario_vacio", "c": "comentario_muy_corto", "d": "calificacion_invalida",
    }


def test_columna_faltante_detiene(tmp_path):
    archivo = tmp_path / "lote.csv"
    pd.DataFrame([fila("a")]).drop(columns=["calificacion"]).to_csv(archivo, index=False)
    with pytest.raises(LoteInvalido, match="calificacion"):
        leer_lote(archivo, COLUMNAS)


def test_lote_vacio_detiene(tmp_path):
    archivo = tmp_path / "lote.csv"
    pd.DataFrame(columns=COLUMNAS).to_csv(archivo, index=False)
    with pytest.raises(LoteInvalido, match="no tiene filas"):
        leer_lote(archivo, COLUMNAS)


def test_archivo_inexistente_detiene(tmp_path):
    with pytest.raises(LoteInvalido, match="No existe"):
        leer_lote(tmp_path / "no_existe.csv", COLUMNAS)
