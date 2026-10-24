"""Stage 4 · Puntuar.

Predice sentimiento y tema del lote limpio con el modelo que aprobó el gate,
marca los comentarios sospechosos con su motivo y guarda en cada fila la
versión del modelo, la ejecución y la fecha.

Uso: python src/puntuar.py
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import cargar_config, error, leer_json, resumen, ruta, run_id  # noqa: E402
from enmascarar import enmascarar  # noqa: E402

COLUMNAS_SALIDA = [
    "comentario_id", "pedido_id", "restaurante_id", "cliente_id", "calificacion", "comentario", "fecha",
    "sentimiento", "confianza_sentimiento", "tema", "confianza_tema",
    "es_sospechoso", "motivo_sospecha", "palabras_clave",
    "modelo_version", "run_id", "fecha_puntuacion",
]


def palabras_clave(modelo: Pipeline, textos: pd.Series, clases_pred: np.ndarray, n: int = 3) -> list[str]:
    """Los n términos con más peso (TF-IDF × coeficiente) hacia la clase predicha."""
    tfidf, clf = modelo.named_steps["tfidf"], modelo.named_steps["clf"]
    x = tfidf.transform(textos)
    nombres = tfidf.get_feature_names_out()
    indice_clase = {c: i for i, c in enumerate(clf.classes_)}
    salida = []
    for fila, clase in zip(range(x.shape[0]), clases_pred):
        vector = x.getrow(fila)
        pesos = vector.data * clf.coef_[indice_clase[clase], vector.indices]
        orden = np.argsort(-pesos)[:n]
        salida.append("|".join(nombres[vector.indices[i]] for i in orden if pesos[i] > 0))
    return salida


def motivo_sospecha(calificacion: str, sentimiento: str) -> str:
    if calificacion == "":
        return "sin_calificacion"
    if calificacion == "5" and sentimiento == "negativo":
        return "5_estrellas_texto_negativo"
    if calificacion == "1" and sentimiento == "positivo":
        return "1_estrella_texto_positivo"
    return ""


def puntuar(lote: pd.DataFrame, modelos: dict[str, Pipeline], version: str, ejecucion: str) -> pd.DataFrame:
    df = lote.copy()
    df["comentario"] = df["comentario"].map(enmascarar)  # idempotente: nunca se puntúa texto sin enmascarar
    for obj in ("sentimiento", "tema"):
        proba = modelos[obj].predict_proba(df["comentario"])
        df[obj] = modelos[obj].classes_[proba.argmax(axis=1)]
        df[f"confianza_{obj}"] = proba.max(axis=1).round(3)
    df["palabras_clave"] = palabras_clave(modelos["sentimiento"], df["comentario"], df["sentimiento"].to_numpy())
    df["motivo_sospecha"] = [motivo_sospecha(c, s) for c, s in zip(df["calificacion"], df["sentimiento"])]
    df["es_sospechoso"] = df["motivo_sospecha"].isin(["5_estrellas_texto_negativo", "1_estrella_texto_positivo"])
    df["modelo_version"] = version
    df["run_id"] = ejecucion
    df["fecha_puntuacion"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return df[COLUMNAS_SALIDA]


def main() -> int:
    config = cargar_config()
    gate = leer_json(ruta(config["salidas"]["gate"]) / "gate.json")
    if not gate.get("aprobado"):
        error("El modelo no aprobó el gate: no se puntúa el lote", "Modelo no aprobado")
        return 1

    carpeta_modelo = ruta(config["salidas"]["modelo"])
    modelos = {obj: joblib.load(carpeta_modelo / f"{obj}.joblib") for obj in ("sentimiento", "tema")}
    version = leer_json(carpeta_modelo / "metadata.json")["modelo_version"]
    calidad = leer_json(ruta(config["salidas"]["calidad"]) / "calidad.json")
    lote = pd.read_csv(
        ruta(config["salidas"]["calidad"]) / "lote_limpio.csv", dtype=str, keep_default_na=False, encoding="utf-8"
    )

    puntuado = puntuar(lote, modelos, version, run_id())
    salida = ruta(config["salidas"]["puntuado"])
    salida.mkdir(parents=True, exist_ok=True)
    archivo = salida / f"{calidad['lote']}_puntuado.csv"
    puntuado.to_csv(archivo, index=False)

    sospechosos = puntuado[puntuado["es_sospechoso"]]
    motivos = sospechosos["motivo_sospecha"].value_counts().to_dict()
    resumen(
        f"## 4 · Puntuar `{calidad['lote']}`\n\n"
        f"- Filas puntuadas: **{len(puntuado)}** → `{archivo.name}`\n"
        f"- Versión del modelo en cada fila: `{version}` · ejecución `{run_id()}`\n"
        f"- Sospechosos: **{len(sospechosos)}** "
        + (f"({', '.join(f'{m}: {n}' for m, n in motivos.items())})" if motivos else "")
        + "\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
