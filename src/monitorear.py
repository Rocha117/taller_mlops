"""Stage 5 · Monitorear.

Compara las métricas del lote puntuado con la línea base y publica el reporte.
La deriva SOLO AVISA (::warning:: y encabezado del resumen): el job termina en
verde. Falla únicamente si falta la línea base.

Uso: python src/monitorear.py
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import advertencia, cargar_config, error, guardar_json, leer_json, resumen, ruta  # noqa: E402
from metricas import a_booleano, calcular  # noqa: E402

NOMBRES = {
    "pct_baja_confianza_sentimiento": "Baja confianza en sentimiento (%)",
    "pct_baja_confianza_tema": "Baja confianza en tema (%)",
    "pct_palabras_no_vistas": "Palabras no vistas al entrenar (%)",
    "pct_sospechosos": "Sospechosos (%)",
    "pct_excluidos": "Filas excluidas por calidad (%)",
    "confianza_media_sentimiento": "Confianza media · sentimiento",
    "confianza_media_tema": "Confianza media · tema",
}


def comparar(lote: dict, base: dict, metricas_alerta: list[str], puntos: float) -> list[dict]:
    filas = []
    for clave, nombre in NOMBRES.items():
        diferencia = round(lote[clave] - base[clave], 3 if clave.startswith("confianza") else 1)
        vigilada = clave in metricas_alerta
        filas.append({
            "metrica": clave,
            "nombre": nombre,
            "linea_base": base[clave],
            "lote": lote[clave],
            "diferencia": diferencia,
            "umbral": f"+{puntos}" if vigilada else None,
            "alerta": vigilada and diferencia > puntos,
        })
    for dimension in ("sentimiento", "tema"):
        clases = sorted(set(base[f"distribucion_{dimension}"]) | set(lote[f"distribucion_{dimension}"]))
        for clase in clases:
            b = base[f"distribucion_{dimension}"].get(clase, 0.0)
            l = lote[f"distribucion_{dimension}"].get(clase, 0.0)
            filas.append({
                "metrica": f"distribucion_{dimension}.{clase}",
                "nombre": f"{dimension.capitalize()} · {clase} (%)",
                "linea_base": b, "lote": l, "diferencia": round(l - b, 1), "umbral": None, "alerta": False,
            })
    return filas


def celda(texto: str) -> str:
    return str(texto).replace("|", "\\|").replace("\n", " ")


def construir_reporte(reporte: dict, puntuado: pd.DataFrame, top_n: int) -> str:
    alertas = [f for f in reporte["comparacion"] if f["alerta"]]
    encabezado = (
        f"🔔 ALERTA DE DERIVA · {len(alertas)} métrica(s) sobre el umbral"
        if alertas
        else "✅ Sin deriva"
    )
    lineas = [
        f"## 5 · Monitorear `{reporte['lote']}` · {encabezado}",
        "",
        f"- Modelo del lote: `{reporte['modelo_version']}` · línea base: `{reporte['linea_base']['lote']}` "
        f"con `{reporte['linea_base']['modelo_version']}`",
        f"- Regla: alerta si una métrica vigilada sube más de **{reporte['umbral_puntos']} puntos** sobre la línea base. "
        "La alerta **avisa**, no detiene el pipeline.",
        "",
        "| Métrica | Línea base | Lote | Diferencia | Umbral | Estado |",
        "|---|---|---|---|---|---|",
    ]
    for f in reporte["comparacion"]:
        estado = "🔔 Alerta" if f["alerta"] else ("✅ OK" if f["umbral"] else "—")
        dif = f"{f['diferencia']:+}"
        lineas.append(
            f"| {f['nombre']} | {f['linea_base']} | {f['lote']} | {dif} | {f['umbral'] or '—'} | {estado} |"
        )

    c = reporte["calidad"]
    motivos = ", ".join(f"{m}: {n}" for m, n in c["excluidas_por_motivo"].items()) or "ninguna"
    lineas += [
        "",
        "### Calidad del lote",
        f"{c['filas_leidas']} leídas · {c['filas_excluidas']} excluidas ({motivos}) · "
        f"{c['filas_sin_calificacion']} sin calificación · **{c['filas_validas']} puntuadas**",
        "",
        f"### Para Producto · los {top_n} comentarios con menor confianza en tema",
        "Pistas de temas que el modelo no conoce (los asigna a otro tema sin avisar).",
        "",
        "| comentario_id | Tema asignado | Confianza | Comentario (enmascarado) |",
        "|---|---|---|---|",
    ]
    for _, r in puntuado.nsmallest(top_n, "confianza_tema").iterrows():
        lineas.append(f"| {r.comentario_id} | {r.tema} | {r.confianza_tema} | {celda(r.comentario)} |")

    sospechosos = puntuado[a_booleano(puntuado["es_sospechoso"])]
    lineas += [
        "",
        f"### Para Calidad de Restaurantes · {len(sospechosos)} comentarios sospechosos",
        "",
        "| comentario_id | ★ | Sentimiento | Confianza | Motivo | Palabras que pesaron | Comentario (enmascarado) |",
        "|---|---|---|---|---|---|---|",
    ]
    for _, r in sospechosos.sort_values("confianza_sentimiento", ascending=False).iterrows():
        lineas.append(
            f"| {r.comentario_id} | {r.calificacion} | {r.sentimiento} | {r.confianza_sentimiento} | "
            f"{r.motivo_sospecha} | {celda(str(r.palabras_clave).replace('|', ', '))} | {celda(r.comentario)} |"
        )
    return "\n".join(lineas) + "\n"


def main() -> int:
    config = cargar_config()
    archivo_base = ruta(config["datos"]["linea_base"])
    if not archivo_base.exists():
        error(f"Falta {config['datos']['linea_base']}. Genérala con: python src/linea_base.py", "Sin línea base")
        resumen("## 5 · Monitorear\n\n🛑 **Falta la línea base** (`monitoreo/linea_base.json`).\n")
        return 1

    base = leer_json(archivo_base)
    calidad = leer_json(ruta(config["salidas"]["calidad"]) / "calidad.json")
    vocabulario = set(leer_json(ruta(config["salidas"]["modelo"]) / "vocabulario.json")["palabras"])
    puntuado = pd.read_csv(
        ruta(config["salidas"]["puntuado"]) / f"{calidad['lote']}_puntuado.csv",
        dtype=str, keep_default_na=False, encoding="utf-8",
    )
    puntuado["confianza_tema"] = puntuado["confianza_tema"].astype(float)
    puntuado["confianza_sentimiento"] = puntuado["confianza_sentimiento"].astype(float)

    mon = config["monitoreo"]
    metricas = calcular(puntuado, vocabulario, calidad, mon["baja_confianza"])
    comparacion = comparar(metricas, base["metricas"], mon["metricas_alerta"], mon["alerta_puntos"])
    alertas = [f for f in comparacion if f["alerta"]]
    reporte = {
        "lote": calidad["lote"],
        "modelo_version": puntuado["modelo_version"].iloc[0] if len(puntuado) else None,
        "run_id": puntuado["run_id"].iloc[0] if len(puntuado) else None,
        "fecha_monitoreo": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "linea_base": {k: base[k] for k in ("lote", "modelo_version", "fecha_generacion")},
        "umbral_puntos": mon["alerta_puntos"],
        "alerta": bool(alertas),
        "metricas_en_alerta": [f["metrica"] for f in alertas],
        "metricas": metricas,
        "calidad": calidad,
        "comparacion": comparacion,
    }

    salida = ruta(config["salidas"]["monitoreo"])
    guardar_json(reporte, salida / "reporte_monitoreo.json")
    markdown = construir_reporte(reporte, puntuado, mon["top_comentarios_tema"])
    (salida / "reporte_monitoreo.md").write_text(markdown, encoding="utf-8")
    resumen(markdown)

    for f in alertas:
        advertencia(
            f"{f['nombre']}: {f['linea_base']} → {f['lote']} ({f['diferencia']:+} puntos, umbral +{mon['alerta_puntos']}) "
            f"en {calidad['lote']}",
            "Alerta de deriva",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
