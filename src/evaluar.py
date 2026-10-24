"""Stage 3 · Desplegar (gate).

Examina los modelos contra el golden set. Si sentimiento o tema no llegan a su
umbral de acierto, termina con error y el pipeline se detiene.

Uso: python src/evaluar.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import cargar_config, error, guardar_json, leer_json, resumen, ruta  # noqa: E402

ESPERADO = {"sentimiento": "sentimiento_esperado", "tema": "tema_esperado"}


def evaluar(modelos: dict, golden: pd.DataFrame, umbrales: dict) -> dict:
    resultado = {}
    for obj, columna in ESPERADO.items():
        pred = modelos[obj].predict(golden["comentario"])
        acierto = float(accuracy_score(golden[columna], pred))
        resultado[obj] = {
            "acierto": round(acierto, 4),
            "f1_macro": round(float(f1_score(golden[columna], pred, average="macro")), 4),
            "umbral": umbrales[obj],
            "errores": int((golden[columna] != pred).sum()),
            "aprobado": acierto >= umbrales[obj],
        }
    return {
        "golden_set_filas": len(golden),
        "modelos": resultado,
        "aprobado": all(r["aprobado"] for r in resultado.values()),
    }


def main() -> int:
    config = cargar_config()
    carpeta_modelo = ruta(config["salidas"]["modelo"])
    modelos = {obj: joblib.load(carpeta_modelo / f"{obj}.joblib") for obj in ESPERADO}
    golden = pd.read_csv(ruta(config["datos"]["golden_set"]), dtype=str, keep_default_na=False, encoding="utf-8")

    gate = evaluar(modelos, golden, config["gate"])
    metadata = leer_json(carpeta_modelo / "metadata.json")
    gate["modelo_version"] = metadata["modelo_version"]
    metadata["gate"] = gate
    guardar_json(metadata, carpeta_modelo / "metadata.json")
    guardar_json(gate, ruta(config["salidas"]["gate"]) / "gate.json")

    filas = "\n".join(
        f"| {obj} | **{r['acierto']:.1%}** | ≥ {r['umbral']:.0%} | {r['f1_macro']:.3f} | {r['errores']} | "
        f"{'✅ Aprueba' if r['aprobado'] else '🛑 No aprueba'} |"
        for obj, r in gate["modelos"].items()
    )
    veredicto = (
        "✅ **El modelo aprueba el examen y se publica.**"
        if gate["aprobado"]
        else "🛑 **El modelo NO aprueba el examen: no se publica y el pipeline se detiene.**"
    )
    resumen(
        f"## 3 · Desplegar (gate) · golden set\n\n{veredicto}\n\n"
        f"Versión: `{gate['modelo_version']}` · {gate['golden_set_filas']} comentarios etiquetados por personas\n\n"
        f"| Modelo | Acierto | Umbral | F1 macro | Errores | Resultado |\n|---|---|---|---|---|---|\n{filas}\n"
    )
    if not gate["aprobado"]:
        for obj, r in gate["modelos"].items():
            if not r["aprobado"]:
                error(f"{obj}: acierto {r['acierto']:.1%} por debajo del umbral {r['umbral']:.0%}", "Gate no aprobado")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
