# Fase 1 · Desplegar y monitorear · Plan

Tareas pequeñas, en orden. Cada una dice qué archivo crea o modifica. Se trabaja solo en la rama `fase-1-desplegar-monitorear`.

## Grupo A · Base del proyecto

1. **Dependencias.** Crear `requirements.txt` con versiones fijas: `scikit-learn`, `pandas`, `numpy`, `joblib`, `pyyaml`, `pytest`.
2. **Configuración.** Crear `config/modelo.yaml` con:
   - parámetros de TF-IDF (`ngram_range: [1, 2]`, `sublinear_tf: true`, `strip_accents: unicode`, `lowercase: true`) y de la regresión logística (`C: 1.0`, `class_weight: balanced`, `max_iter: 1000`, `random_state: 42`),
   - umbrales: gate (`sentimiento: 0.85`, `tema: 0.80`), `baja_confianza: 0.5`, `alerta_puntos: 10`, `min_palabras: 3`, `max_pct_excluidos: 20`,
   - rutas de datos y columnas esperadas del lote.
3. **Utilidades comunes.** Crear `src/comun.py`: cargar la configuración, calcular `modelo_version` (fecha del commit + sha7; fuera de Git, `local`), leer `GITHUB_RUN_ID`, escribir en `GITHUB_STEP_SUMMARY` si existe y emitir `::warning::`.
4. **`.gitignore`.** Ignorar `salidas/`, `__pycache__/` y `.pytest_cache/`.

## Grupo B · Stage 1 · Calidad

5. **Enmascarado.** Crear `src/enmascarar.py` con la función `enmascarar(texto)` y los patrones de `requerimientos.md` (correo, teléfono, documento, nombre, dirección).
6. **Reglas de calidad.** Crear `src/calidad.py`: lee `data/source/<lote>.csv`, valida columnas y aplica las reglas 1 a 7 en orden. Escribe `salidas/calidad/lote_limpio.csv`, `excluidos.csv` y `calidad.json`. Avisa si se excluye más del 20% y deja una tabla de conteos en el resumen de la ejecución.
7. **Pruebas.** Crear `tests/test_enmascarar.py` (casos sintéticos de cada patrón y textos que no se deben tocar, como "La app guarda mis direcciones") y `tests/test_calidad.py` (duplicado, vacío, corto, sin calificación, calificación inválida, columna faltante).

## Grupo C · Stages 2 y 3 · Entrenar y gate

8. **Entrenar.** Crear `src/entrenar.py`: entrena los pipelines TF-IDF + regresión logística de `sentimiento` y `tema` con `data/train/`. Guarda `salidas/modelo/sentimiento.joblib`, `tema.joblib` y `metadata.json` (versión, commit, hash SHA-256 del entrenamiento, parámetros, tamaño del vocabulario).
9. **Gate.** Crear `src/evaluar.py`: carga los modelos, predice el golden set y calcula el acierto y el F1 macro. Escribe `salidas/gate/gate.json`, agrega el resultado a `metadata.json`, publica una tabla en el resumen y termina con código 1 si algún modelo no llega a su umbral.

## Grupo D · Stage 4 · Puntuar

10. **Puntuar.** Crear `src/puntuar.py`: lee `lote_limpio.csv`, enmascara el texto, predice sentimiento y tema con su confianza, calcula `palabras_clave` (las 3 entradas TF-IDF × coeficiente con más peso hacia la clase predicha), marca los sospechosos con su motivo y agrega `modelo_version`, `run_id` y `fecha_puntuacion`. Escribe `salidas/puntuado/lote_XX_puntuado.csv`.

## Grupo E · Stage 5 · Monitorear

11. **Métricas.** Crear `src/metricas.py` con una función que calcule las métricas de monitoreo de un lote puntuado (más el vocabulario de entrenamiento y `calidad.json`). La usan la línea base y el monitoreo, para que ambos midan exactamente lo mismo.
12. **Línea base.** Crear `src/linea_base.py`: corre calidad → entrenar → puntuar sobre el lote 1 y escribe `monitoreo/linea_base.json` (métricas, `modelo_version`, fecha). Ejecutarlo una vez y **commitear** el archivo.
13. **Monitorear.** Crear `src/monitorear.py`: compara el lote con la línea base, decide la alerta (+10 puntos en baja confianza de sentimiento, baja confianza de tema o palabras no vistas), emite un `::warning::` por cada métrica que cruza el umbral, arma el top 10 de textos distintos con menor confianza en tema (con cuántas veces se repite cada uno; prueba en `tests/test_monitorear.py`) y escribe el reporte en el resumen de la ejecución, `salidas/monitoreo/reporte_monitoreo.md` y `.json`. Termina en 0 aunque haya alerta, y en 1 solo si falta la línea base.

## Grupo F · Orquestación

14. **Workflow.** Crear `.github/workflows/pipeline.yml`:
    - disparadores `pull_request` (rama `main`), `workflow_dispatch` (input `lote`: `lote_01`/`lote_02`) y `schedule` (`0 13 * * 1`),
    - un paso inicial que resuelve qué archivo de lote usar,
    - 5 jobs en cadena (`1-calidad` → `2-entrenar` → `3-desplegar-gate` → `4-puntuar` → `5-monitorear`) con `needs`, Python 3.11, caché de `pip`, `timeout-minutes: 10` y `permissions: contents: read`,
    - `pytest` como primer paso de `1-calidad`,
    - subida y descarga de artefactos entre jobs (`retention-days: 30`): `calidad`, `modelo`, `gate`, `lote-puntuado` y `reporte-monitoreo`.
15. **README.** Agregar al `README.md` una sección "Pipeline de la fase 1": qué hace cada script, en qué stage corre, cómo correrlo en local y cómo lanzar el pipeline con el lote 2.

## Grupo G · Cierre

16. **Primera corrida.** Hacer push, abrir el Pull Request hacia `main` y comprobar que los 5 jobs terminan en verde con el lote 1.
17. **Lote 2.** Lanzar `workflow_dispatch` con `lote = lote_02` y comprobar que aparece la alerta.
18. **Checks obligatorios.** En el ruleset de `main`, marcar los 5 jobs como *required status checks*.
19. **Validación.** Recorrer `validacion.md`, marcar cada casilla y adjuntar al PR el enlace a la ejecución del lote 2.
