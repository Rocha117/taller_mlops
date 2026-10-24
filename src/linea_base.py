"""Genera la línea base del monitoreo (monitoreo/linea_base.json).

Puntúa el lote 1 (la "foto normal") con el modelo de este commit y guarda sus
métricas. No corre en el pipeline: se ejecuta a mano y el archivo se sube por
Pull Request, para que cualquier cambio de la línea base quede revisado.

Uso: python src/linea_base.py
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from calidad import aplicar_reglas, leer_lote  # noqa: E402
from comun import cargar_config, guardar_json, nombre_lote, ruta, ruta_lote  # noqa: E402
from enmascarar import enmascarar  # noqa: E402
from entrenar import entrenar  # noqa: E402
from metricas import calcular  # noqa: E402
from puntuar import puntuar  # noqa: E402


def main() -> int:
    config = cargar_config()
    archivo = ruta_lote(config["datos"]["lote_linea_base"], config)
    df = leer_lote(archivo, config["calidad"]["columnas_lote"])
    validas, excluidas = aplicar_reglas(df, config["calidad"]["min_palabras"])
    validas["comentario"] = validas["comentario"].map(enmascarar)
    calidad = {"pct_excluidos": round(100 * len(excluidas) / len(df), 1)}

    modelos, metadata, vocabulario = entrenar(config)
    puntuado = puntuar(validas, modelos, metadata["modelo_version"], "linea_base")
    metricas = calcular(puntuado, set(vocabulario), calidad, config["monitoreo"]["baja_confianza"])

    destino = ruta(config["datos"]["linea_base"])
    guardar_json(
        {
            "lote": nombre_lote(archivo, config),
            "archivo": archivo.name,
            "modelo_version": metadata["modelo_version"],
            "fecha_generacion": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "metricas": metricas,
        },
        destino,
    )
    print(f"Línea base escrita en {destino.relative_to(ruta('.'))}")
    for clave, valor in metricas.items():
        print(f"  {clave}: {valor}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
