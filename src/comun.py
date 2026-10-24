"""Utilidades compartidas por todos los stages del pipeline."""
from __future__ import annotations

import json
import os
import re
import subprocess
import unicodedata
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent


def cargar_config() -> dict:
    with open(RAIZ / "config" / "modelo.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ruta(relativa: str) -> Path:
    return RAIZ / relativa


def ruta_lote(lote: str, config: dict) -> Path:
    """Convierte 'lote_01', 'ultimo' o una ruta a CSV en la ruta del archivo del lote."""
    carpeta = ruta(config["datos"]["carpeta_lotes"])
    prefijo = config["datos"]["prefijo_lote"]
    if lote == "ultimo":
        archivos = sorted(carpeta.glob(f"{prefijo}*.csv"))
        if not archivos:
            raise FileNotFoundError(f"No hay lotes en {carpeta}")
        return archivos[-1]
    if lote.endswith(".csv"):
        return Path(lote).resolve()
    return carpeta / f"{prefijo}{lote}.csv"


def nombre_lote(ruta_csv: Path, config: dict) -> str:
    """'comentarios_lote_01.csv' -> 'lote_01'."""
    return ruta_csv.stem.removeprefix(config["datos"]["prefijo_lote"])


def _git(*args: str) -> str | None:
    try:
        return subprocess.run(
            ["git", *args], cwd=RAIZ, capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def commit_sha() -> str:
    return _git("rev-parse", "HEAD") or "local"


def modelo_version() -> str:
    """AAAA.MM.DD-<sha7> con la fecha del commit, para que el mismo commit dé la misma versión."""
    fecha = _git("log", "-1", "--format=%cd", "--date=format:%Y.%m.%d")
    sha = _git("rev-parse", "--short=7", "HEAD")
    if not fecha or not sha:
        return "local"
    return f"{fecha}-{sha}"


def run_id() -> str:
    return os.environ.get("GITHUB_RUN_ID", "local")


def resumen(markdown: str) -> None:
    """Escribe en el resumen de la ejecución de GitHub Actions (o en consola si es local)."""
    destino = os.environ.get("GITHUB_STEP_SUMMARY")
    if destino:
        with open(destino, "a", encoding="utf-8") as f:
            f.write(markdown + "\n")
    else:
        print(markdown)


def advertencia(mensaje: str, titulo: str = "Advertencia") -> None:
    print(f"::warning title={titulo}::{mensaje}", flush=True)


def error(mensaje: str, titulo: str = "Error") -> None:
    print(f"::error title={titulo}::{mensaje}", flush=True)


def guardar_json(datos: dict, destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
        f.write("\n")


def leer_json(origen: Path) -> dict:
    with open(origen, encoding="utf-8") as f:
        return json.load(f)


def normalizar(texto: str) -> str:
    """Minúsculas y sin tildes, igual que el TF-IDF (strip_accents='unicode')."""
    texto = unicodedata.normalize("NFKD", str(texto).lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def palabras(texto: str) -> list[str]:
    """Palabras de un texto normalizado (sin signos), para medir vocabulario."""
    return re.findall(r"[a-z0-9]+", normalizar(texto))
