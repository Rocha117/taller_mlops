"""Métricas de monitoreo de un lote puntuado.

La usan la línea base (src/linea_base.py) y el monitoreo (src/monitorear.py),
para que ambos midan exactamente lo mismo.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import palabras  # noqa: E402


def _pct(valor: float) -> float:
    return round(100 * float(valor), 1)


def a_booleano(serie: pd.Series) -> pd.Series:
    """es_sospechoso llega como bool en memoria o como 'True'/'False' desde el CSV."""
    return serie.astype(str).str.lower().eq("true")


def calcular(puntuado: pd.DataFrame, vocabulario: set[str], calidad: dict, baja_confianza: float) -> dict:
    conf_s = puntuado["confianza_sentimiento"].astype(float)
    conf_t = puntuado["confianza_tema"].astype(float)
    todas = [p for texto in puntuado["comentario"] for p in palabras(texto)]
    no_vistas = sum(p not in vocabulario for p in todas)
    sospechosos = a_booleano(puntuado["es_sospechoso"])
    return {
        "filas_puntuadas": len(puntuado),
        "pct_baja_confianza_sentimiento": _pct((conf_s < baja_confianza).mean()),
        "pct_baja_confianza_tema": _pct((conf_t < baja_confianza).mean()),
        "pct_palabras_no_vistas": _pct(no_vistas / len(todas)) if todas else 0.0,
        "confianza_media_sentimiento": round(float(conf_s.mean()), 3),
        "confianza_media_tema": round(float(conf_t.mean()), 3),
        "distribucion_sentimiento": {k: _pct(v) for k, v in puntuado["sentimiento"].value_counts(normalize=True).sort_index().items()},
        "distribucion_tema": {k: _pct(v) for k, v in puntuado["tema"].value_counts(normalize=True).sort_index().items()},
        "sospechosos": int(sospechosos.sum()),
        "pct_sospechosos": _pct(sospechosos.mean()),
        "pct_excluidos": calidad["pct_excluidos"],
    }
