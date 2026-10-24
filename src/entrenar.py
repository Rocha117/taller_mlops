"""Stage 2 · Entrenar.

Entrena dos modelos TF-IDF + regresión logística (sentimiento y tema) con
data/train/ y los parámetros de config/modelo.yaml. Guarda los modelos, su
metadata y el vocabulario de entrenamiento (para medir palabras no vistas).

Uso: python src/entrenar.py
"""
from __future__ import annotations

import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import cargar_config, commit_sha, guardar_json, modelo_version, palabras, resumen, ruta  # noqa: E402

OBJETIVOS = ["sentimiento", "tema"]


def construir_pipeline(config: dict) -> Pipeline:
    tfidf = dict(config["modelo"]["tfidf"])
    tfidf["ngram_range"] = tuple(tfidf["ngram_range"])
    return Pipeline([
        ("tfidf", TfidfVectorizer(**tfidf)),
        ("clf", LogisticRegression(**config["modelo"]["regresion_logistica"])),
    ])


def sha256(archivo: Path) -> str:
    return hashlib.sha256(archivo.read_bytes()).hexdigest()


def entrenar(config: dict) -> tuple[dict[str, Pipeline], dict, list[str]]:
    """Devuelve (modelos, metadata, vocabulario de palabras del entrenamiento)."""
    archivo = ruta(config["datos"]["entrenamiento"])
    df = pd.read_csv(archivo, dtype=str, keep_default_na=False, encoding="utf-8")
    modelos = {obj: construir_pipeline(config).fit(df["comentario"], df[obj]) for obj in OBJETIVOS}
    vocabulario = sorted({p for texto in df["comentario"] for p in palabras(texto)})
    metadata = {
        "modelo_version": modelo_version(),
        "commit": commit_sha(),
        "fecha_entrenamiento": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "datos_entrenamiento": {
            "archivo": config["datos"]["entrenamiento"],
            "sha256": sha256(archivo),
            "filas": len(df),
        },
        "parametros": config["modelo"],
        "modelos": {
            obj: {
                "clases": modelos[obj].classes_.tolist(),
                "tamano_vocabulario_tfidf": len(modelos[obj].named_steps["tfidf"].vocabulary_),
            }
            for obj in OBJETIVOS
        },
    }
    return modelos, metadata, vocabulario


def main() -> int:
    config = cargar_config()
    modelos, metadata, vocabulario = entrenar(config)
    salida = ruta(config["salidas"]["modelo"])
    salida.mkdir(parents=True, exist_ok=True)
    for obj, modelo in modelos.items():
        joblib.dump(modelo, salida / f"{obj}.joblib")
    guardar_json(metadata, salida / "metadata.json")
    guardar_json({"palabras": vocabulario}, salida / "vocabulario.json")

    filas = "\n".join(
        f"| {obj} | {', '.join(m['clases'])} | {m['tamano_vocabulario_tfidf']} |"
        for obj, m in metadata["modelos"].items()
    )
    resumen(
        f"## 2 · Entrenar\n\n"
        f"- Versión del modelo: `{metadata['modelo_version']}`\n"
        f"- Datos: `{metadata['datos_entrenamiento']['archivo']}` "
        f"({metadata['datos_entrenamiento']['filas']} filas, sha256 `{metadata['datos_entrenamiento']['sha256'][:12]}…`)\n\n"
        f"| Modelo | Clases | Términos TF-IDF |\n|---|---|---|\n{filas}\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
