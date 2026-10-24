"""Stage 1 · Calidad del lote.

Valida el CSV del lote y aplica las reglas de datos antes de puntuar.
Las filas que no se pueden usar se excluyen con su motivo; nunca se corrigen.

Uso: python src/calidad.py --lote lote_01
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import advertencia, cargar_config, error, guardar_json, nombre_lote, resumen, ruta, ruta_lote  # noqa: E402
from enmascarar import enmascarar  # noqa: E402

CALIFICACIONES_VALIDAS = {"1", "2", "3", "4", "5"}


class LoteInvalido(Exception):
    """El archivo del lote no se puede usar: detiene el pipeline."""


def leer_lote(archivo: Path, columnas: list[str]) -> pd.DataFrame:
    if not archivo.exists():
        raise LoteInvalido(f"No existe el archivo del lote: {archivo}")
    try:
        df = pd.read_csv(archivo, dtype=str, keep_default_na=False, encoding="utf-8")
    except Exception as exc:  # archivo corrupto, codificación, etc.
        raise LoteInvalido(f"No se pudo leer {archivo.name}: {exc}") from exc
    faltan = [c for c in columnas if c not in df.columns]
    if faltan:
        raise LoteInvalido(f"Faltan columnas en {archivo.name}: {', '.join(faltan)}")
    if df.empty:
        raise LoteInvalido(f"El lote {archivo.name} no tiene filas")
    return df[columnas]


def aplicar_reglas(df: pd.DataFrame, min_palabras: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devuelve (filas válidas, filas excluidas con motivo_exclusion). Reglas en orden."""
    df = df.copy()
    df["comentario"] = df["comentario"].str.strip()
    df["calificacion"] = df["calificacion"].str.strip()
    motivo = pd.Series("", index=df.index)

    def marcar(condicion: pd.Series, etiqueta: str) -> None:
        motivo[(motivo == "") & condicion] = etiqueta

    marcar(df.duplicated("comentario_id", keep="first"), "duplicado")
    marcar(df["comentario"] == "", "comentario_vacio")
    marcar(df["comentario"].str.split().str.len() < min_palabras, "comentario_muy_corto")
    marcar(
        (df["calificacion"] != "") & ~df["calificacion"].isin(CALIFICACIONES_VALIDAS),
        "calificacion_invalida",
    )
    validas = df[motivo == ""].reset_index(drop=True)
    excluidas = df[motivo != ""].assign(motivo_exclusion=motivo[motivo != ""]).reset_index(drop=True)
    return validas, excluidas


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lote", default="lote_01", help="lote_01, lote_02, ultimo o ruta a un CSV")
    args = parser.parse_args()

    config = cargar_config()
    archivo = ruta_lote(args.lote, config)
    lote = nombre_lote(archivo, config)
    salida = ruta(config["salidas"]["calidad"])
    salida.mkdir(parents=True, exist_ok=True)

    try:
        df = leer_lote(archivo, config["calidad"]["columnas_lote"])
    except LoteInvalido as exc:
        error(str(exc), "Lote inválido")
        resumen(f"## 1 · Calidad del lote\n\n🛑 **Lote inválido:** {exc}\n")
        return 1

    validas, excluidas = aplicar_reglas(df, config["calidad"]["min_palabras"])
    # Ningún artefacto guarda el texto original (datos personales).
    validas["comentario"] = validas["comentario"].map(enmascarar)
    excluidas["comentario"] = excluidas["comentario"].map(enmascarar)
    validas.to_csv(salida / "lote_limpio.csv", index=False)
    excluidas.to_csv(salida / "excluidos.csv", index=False)

    por_motivo = {k: int(v) for k, v in excluidas["motivo_exclusion"].value_counts().items()}
    pct_excluidos = round(100 * len(excluidas) / len(df), 1)
    informe = {
        "lote": lote,
        "archivo": archivo.name,
        "filas_leidas": len(df),
        "filas_excluidas": len(excluidas),
        "excluidas_por_motivo": por_motivo,
        "pct_excluidos": pct_excluidos,
        "filas_sin_calificacion": int((validas["calificacion"] == "").sum()),
        "filas_validas": len(validas),
    }
    guardar_json(informe, salida / "calidad.json")

    limite = config["calidad"]["max_pct_excluidos"]
    filas = "\n".join(f"| Excluidas · `{m}` | {n} |" for m, n in sorted(por_motivo.items()))
    estado = "✅ Lote usable"
    if pct_excluidos > limite:
        estado = f"⚠️ Se excluyó el {pct_excluidos}% de las filas (límite {limite}%)"
        advertencia(f"Se excluyó el {pct_excluidos}% de las filas del {lote} (límite {limite}%)", "Calidad del lote")
    resumen(
        f"## 1 · Calidad del lote `{lote}`\n\n{estado}\n\n"
        f"| Concepto | Filas |\n|---|---|\n"
        f"| Leídas | {informe['filas_leidas']} |\n{filas}\n"
        f"| **Excluidas (total)** | **{informe['filas_excluidas']}** ({pct_excluidos}%) |\n"
        f"| Sin calificación (se puntúan, no pueden ser sospechosas) | {informe['filas_sin_calificacion']} |\n"
        f"| **Válidas** | **{informe['filas_validas']}** |\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
