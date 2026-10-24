import pandas as pd

from monitorear import textos_menor_confianza_tema


def test_top_agrupa_textos_repetidos():
    puntuado = pd.DataFrame({
        "comentario_id": ["a", "b", "c", "d", "e"],
        "comentario": ["soporte malo", "soporte malo", "soporte malo", "delivery cold", "todo rico"],
        "tema": ["app", "app", "app", "precio", "comida"],
        "confianza_tema": [0.2, 0.2, 0.2, 0.3, 0.9],
    })
    top = textos_menor_confianza_tema(puntuado, top_n=2)
    assert [(t["comentario"], t["veces"], t["ejemplo_id"]) for t in top] == [
        ("soporte malo", 3, "a"),
        ("delivery cold", 1, "d"),
    ]
