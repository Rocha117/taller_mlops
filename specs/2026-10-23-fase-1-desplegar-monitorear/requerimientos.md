# Fase 1 · Desplegar y monitorear · Requerimientos

> Fase 1 de `constitucion/roadmap.md`. Respeta `constitucion/stack-tecnologico.md`; si algo aquí la contradice, manda la constitución.

## Scope

**Esta fase construye** un pipeline en GitHub Actions que, sin intervención manual:
1. valida el lote de comentarios,
2. entrena los modelos de sentimiento y tema,
3. los examina contra el golden set y solo sigue si aprueban,
4. puntúa el lote con trazabilidad y datos personales enmascarados,
5. compara el lote con la línea base y avisa si hay deriva.

**Esta fase no construye:** reentrenamiento con datos nuevos, comparación retador vs actual, aprobación humana, publicación como GitHub Release, reversión ni temas nuevos. Todo eso es la fase 2.

## Stages del pipeline

Un job por stage, en cadena: cada uno empieza solo si el anterior terminó bien. Entre jobs, los archivos viajan como artefactos de la ejecución.

| # | Job | Entrada | Salida | Detiene / avisa |
|---|---|---|---|---|
| 1 | `1-calidad` | `data/source/<lote>.csv`, `config/modelo.yaml` | `lote_limpio.csv`, `excluidos.csv`, `calidad.json` | 🛑 Detiene si el archivo no existe, no se puede leer, está vacío o le falta una columna. ⚠️ Avisa si se excluye más del 20% de las filas. |
| 2 | `2-entrenar` | `data/train/comentarios_entrenamiento.csv`, `config/modelo.yaml` | `sentimiento.joblib`, `tema.joblib`, `metadata.json` | 🛑 Detiene si falla. |
| 3 | `3-desplegar-gate` | Modelos + `data/eval/golden_set.csv` | `gate.json` (acierto por modelo, umbral y resultado) | 🛑 Detiene si sentimiento < 85% o tema < 80%. |
| 4 | `4-puntuar` | `lote_limpio.csv` + modelos aprobados | `lote_XX_puntuado.csv` | 🛑 Detiene si falla. |
| 5 | `5-monitorear` | `lote_XX_puntuado.csv`, `calidad.json`, `monitoreo/linea_base.json`, vocabulario de entrenamiento | `reporte_monitoreo.md`, `reporte_monitoreo.json`, resumen de la ejecución | ⚠️ **Solo avisa.** 🛑 Falla solo si falta `monitoreo/linea_base.json`. |

## Reglas de datos antes de puntuar

Se aplican en este orden. Las filas excluidas se guardan en `excluidos.csv` con la columna `motivo_exclusion`; nunca se corrigen a mano.

| # | Caso | Regla | `motivo_exclusion` |
|---|---|---|---|
| 1 | Columnas | Deben existir `comentario_id, pedido_id, restaurante_id, cliente_id, calificacion, comentario, fecha`. Si falta alguna, el job falla. | — |
| 2 | `comentario_id` duplicado | Se queda la **primera** aparición; las demás se excluyen. | `duplicado` |
| 3 | Comentario vacío o solo espacios | Se excluye. | `comentario_vacio` |
| 4 | Comentario de **menos de 3 palabras** | Se excluye. | `comentario_muy_corto` |
| 5 | Calificación con valor fuera de 1 a 5 | Se excluye. | `calificacion_invalida` |
| 6 | Calificación vacía | **Se puntúa**, pero no puede ser sospechoso (`es_sospechoso = false`, `motivo_sospecha = "sin_calificacion"`). | — |
| 7 | Mismo texto con distinto `comentario_id` | **Se mantiene**: son pedidos y clientes distintos. | — |

`calidad.json` guarda: filas leídas, filas excluidas por motivo, filas sin calificación, filas válidas y % excluido.

## Datos personales

- Antes de puntuar, el texto se **enmascara** y el modelo predice sobre el texto ya enmascarado. Así, ningún artefacto guarda el texto original.
- Patrones mínimos:

| Dato | Ejemplo | Reemplazo |
|---|---|---|
| Correo | `ana.p@gmail.com` | `[CORREO]` |
| Teléfono (9 dígitos que empiezan con 9, con o sin `+51`, espacios o guiones) | `+51 987 654 321` | `[TELEFONO]` |
| Documento (8 dígitos sueltos) | `45678912` | `[DOCUMENTO]` |
| Nombre después de "me llamo", "mi nombre es" o "soy" seguido de palabra con mayúscula | `soy Carla Pérez` | `soy [NOMBRE]` |
| Dirección que empieza con "Av.", "Jr.", "Calle" o "Psje." | `Av. Arequipa 1234` | `[DIRECCION]` |

- Las reglas se prueban con casos sintéticos en `tests/`, porque los lotes actuales no traen datos personales.
- `cliente_id`, `pedido_id` y `restaurante_id` se mantienen: son identificadores internos, no datos personales en claro.

## Gate de despliegue

- **Métrica:** acierto (accuracy) en `data/eval/golden_set.csv`, comparando la predicción contra `sentimiento_esperado` y `tema_esperado`.
- **Umbrales:** sentimiento **≥ 0.85**, tema **≥ 0.80**. Viven en `config/modelo.yaml`.
- Si alguno no llega, el job termina con error y el pipeline se detiene: no se puntúa ningún lote.
- El acierto, el umbral y el resultado de cada modelo se muestran en el resumen de la ejecución y se guardan en `gate.json`. Se agrega también el F1 macro, solo como información.

## Lote puntuado

Archivo `lote_XX_puntuado.csv` (por ejemplo `lote_01_puntuado.csv`). Una fila por comentario válido, con:

| Columna | Contenido |
|---|---|
| `comentario_id, pedido_id, restaurante_id, cliente_id, calificacion, fecha` | Igual que en el lote |
| `comentario` | Texto **enmascarado** |
| `sentimiento`, `confianza_sentimiento` | Clase predicha y su probabilidad (0 a 1, 3 decimales) |
| `tema`, `confianza_tema` | Clase predicha y su probabilidad |
| `es_sospechoso` | `true` / `false` |
| `motivo_sospecha` | `5_estrellas_texto_negativo`, `1_estrella_texto_positivo`, `sin_calificacion` o vacío |
| `palabras_clave` | Las 3 palabras o bigramas que más pesaron hacia el sentimiento predicho, separados por `\|` |
| `modelo_version` | `AAAA.MM.DD-<sha7>`, con la fecha del commit (dos corridas del mismo commit dan la misma versión) |
| `run_id` | `GITHUB_RUN_ID` (en local: `local`) |
| `fecha_puntuacion` | Fecha y hora UTC de la corrida, en formato ISO 8601 |

## Comentarios sospechosos

- **Regla:** `calificacion == 5` y `sentimiento == negativo` → `5_estrellas_texto_negativo`; `calificacion == 1` y `sentimiento == positivo` → `1_estrella_texto_positivo`.
- **Sin mínimo de confianza.** En el lote 1 los 5 sospechosos son contradicciones reales; exigir confianza ≥ 0.6 dejaría fuera 3 de ellos. Las falsas alarmas que trae la deriva (por ejemplo, reembolsos leídos como positivos en el lote 2) se controlan vigilando el % de sospechosos en el monitoreo.
- Cada sospechoso guarda su motivo, la confianza y `palabras_clave`, para que Valeria sepa **por qué** se marcó.

## Disparadores del Action

| Disparador | Lote |
|---|---|
| `pull_request` hacia `main` | `comentarios_lote_01.csv` |
| `workflow_dispatch` con input `lote` (opciones `lote_01`, `lote_02`; por defecto `lote_01`) | `data/source/comentarios_<lote>.csv` |
| `schedule` cada lunes 13:00 UTC (08:00 Lima) | El último archivo de `data/source/` en orden alfabético (hoy, el lote 2) |

GitHub ejecuta el `schedule` solo desde `main`, así que la corrida semanal empieza después del merge.

## Monitoreo

- **Línea base:** `monitoreo/linea_base.json`, versionado en Git. Lo genera `src/linea_base.py` puntuando el lote 1 con el modelo de este commit. Guarda las métricas y la `modelo_version` con que se calcularon. Solo cambia por Pull Request.
- **Métricas del lote:**

| Métrica | Definición |
|---|---|
| `pct_baja_confianza_sentimiento` | % de filas con `confianza_sentimiento < 0.5` |
| `pct_baja_confianza_tema` | % de filas con `confianza_tema < 0.5` |
| `pct_palabras_no_vistas` | % de palabras del lote (en minúsculas y sin tildes) que no aparecen en el vocabulario de entrenamiento |
| `confianza_media_sentimiento`, `confianza_media_tema` | Promedio de la confianza |
| `distribucion_sentimiento`, `distribucion_tema` | % por clase |
| `pct_sospechosos` | % de filas con `es_sospechoso = true` |
| `pct_excluidos` | Viene de `calidad.json` |

- **Alerta:** se enciende si **cualquiera** de estas métricas sube **más de 10 puntos porcentuales** sobre la línea base: `pct_baja_confianza_sentimiento`, `pct_baja_confianza_tema` o `pct_palabras_no_vistas`. El umbral (10) vive en `config/modelo.yaml`. Las demás métricas se reportan, pero no disparan la alerta.
- **Cómo se ve la alerta:**
  - una anotación `::warning::` por cada métrica que cruzó el umbral (visible en el PR y en la ejecución),
  - el encabezado del resumen de la ejecución dice `🔔 ALERTA DE DERIVA` o `✅ Sin deriva`,
  - el job **termina en verde**: la alerta no bloquea.
- **Reporte** (resumen de la ejecución + `reporte_monitoreo.md` y `.json` como artefacto):
  - una tabla con métrica, línea base, lote, diferencia, umbral y estado,
  - la `modelo_version` del lote y la de la línea base,
  - los conteos de calidad,
  - para Producto, los 10 **textos distintos** (enmascarados) con menor `confianza_tema`: los textos repetidos se agrupan y se muestra cuántas veces aparece cada uno, el tema asignado, la confianza y un `comentario_id` de ejemplo,
  - para Calidad, la lista de sospechosos con su motivo.

## Restricciones

- **Costo:** runners `ubuntu-latest`, sin secrets, sin APIs, `permissions: contents: read`, caché de `pip`, `timeout-minutes: 10` por job. Meta: menos de 5 minutos en total.
- **Dependencias:** `requirements.txt` con versiones fijas. Python 3.11.
- **Reproducibilidad:** parámetros en `config/modelo.yaml` y `random_state = 42`. El mismo commit y el mismo lote dan las mismas predicciones y métricas; solo cambian `run_id` y `fecha_puntuacion`.
- **Idempotencia:** volver a correr un lote no duplica filas (se quitan duplicados por `comentario_id` y cada corrida genera su propio artefacto).
- **Trazabilidad:** `modelo_version`, `run_id` y `fecha_puntuacion` en cada fila; `metadata.json` con el commit, el hash SHA-256 del archivo de entrenamiento, los parámetros y el resultado del gate.
- **Retención:** artefactos por 30 días.
- **Ejecución local:** cada script se puede correr con `python src/<script>.py` para depurar, sin GitHub.

## Decisiones tomadas y su motivo

| Decisión | Motivo |
|---|---|
| Sin calificación → se puntúa, pero no es sospechoso | El texto es válido para sentimiento y tema; sin estrellas no hay contradicción posible. |
| Mismo texto con distinto ID → se mantiene | Son pedidos distintos; borrarlos subestimaría las quejas reales. |
| Sospechosos sin mínimo de confianza | En el lote 1 un mínimo de 0.6 perdería 3 de 5 sospechosos reales. Las falsas alarmas por deriva se vigilan aparte. |
| Alerta por baja confianza y palabras no vistas, no por % de negativos | Entre el lote 1 y el lote 2 el % de negativos casi no cambia (36% → 35%), pero la baja confianza en tema sube de 15% a 40%. |
| La deriva solo avisa | Es información para decidir un reentrenamiento (fase 2), no un error; un pipeline rojo cada semana generaría ruido. |
| El modelo predice sobre el texto enmascarado | Así el texto original no queda en ningún artefacto (pedido de Patricia). |
| Se reentrena en cada corrida | Tarda segundos y evita depender de un artefacto guardado; el registro de modelos llega en la fase 2. |
| Jobs en cadena (calidad primero) | Si el lote no sirve, no se gastan minutos entrenando. |
| `modelo_version` con la fecha del commit, no la de la corrida | Dos corridas del mismo código dan la misma versión. |
| El top 10 para Producto agrupa los textos repetidos | En la primera corrida del lote 2, 5 copias de un mismo texto de soporte ocupaban el top y escondían el inglés y las propinas (2026-10-24). |
