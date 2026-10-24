# Fase 1 · Desplegar y monitorear · Validación

Cada criterio dice dónde se comprueba y qué resultado se espera. Los valores "≈" salen de una prueba exploratoria con los parámetros de `config/modelo.yaml`; se aceptan diferencias de ±3 puntos porcentuales por detalles de tokenización, siempre que la conclusión (alerta sí / no) se mantenga.

## Evidencia (2026-10-24)

| Corrida | Evento | Resultado |
|---|---|---|
| [40055836663](https://github.com/Rocha117/taller_mlops/actions/runs/40055836663) | Pull Request #1 · lote 1 | 5 jobs en verde · `✅ Sin deriva` |
| [40055854203](https://github.com/Rocha117/taller_mlops/actions/runs/40055854203) | `workflow_dispatch` · lote 2 | 5 jobs en verde · `🔔 ALERTA DE DERIVA` en 3 métricas |
| [40056605584](https://github.com/Rocha117/taller_mlops/actions/runs/40056605584) | Pull Request #1 · lote 1 · con el top 10 agrupado (`7e449c4`) | 5 jobs en verde · `✅ Sin deriva` |
| [40056603411](https://github.com/Rocha117/taller_mlops/actions/runs/40056603411) | `workflow_dispatch` · lote 2 · con el top 10 agrupado (`7e449c4`) | 5 jobs en verde · `🔔 ALERTA DE DERIVA` en 3 métricas · top 10 con inglés, reembolsos, soporte y propinas |

Los criterios marcados se comprobaron con los artefactos descargados de esas corridas (`calidad`, `gate`, `lote-puntuado`, `reporte-monitoreo`) y con las anotaciones del job `5-monitorear`.

## Con el lote 1 (Pull Request hacia `main`)

### Pipeline
- [x] El PR muestra los 5 jobs: `1-calidad`, `2-entrenar`, `3-desplegar-gate`, `4-puntuar` y `5-monitorear`. **Esperado:** todos en verde.
- [x] La corrida completa tarda menos de 5 minutos. **Dónde:** duración total de la ejecución en la pestaña Actions. *(≈ 2 minutos)*
- [x] `pytest` pasa en `1-calidad`. **Dónde:** log del job. *(20 pruebas)*

### Calidad del lote (`1-calidad`, artefacto `calidad` → `calidad.json`)
- [x] Filas leídas: **89**.
- [x] Excluidas: **3**: 1 `duplicado` (`c1_0004`), 1 `comentario_vacio` (`c1_0901`) y 1 `comentario_muy_corto` (`c1_0903`, "ok"). % excluido: **3.4%**, sin advertencia (< 20%).
- [x] Sin calificación: **1** (`c1_0902`): se puntúa.
- [x] Filas válidas: **86**.

### Gate (`3-desplegar-gate`, resumen de la ejecución y `gate.json`)
- [x] El acierto de sentimiento en el golden set aparece en el resumen. **Esperado:** ≥ 0.85 (en la prueba: 1.00). *(Resultado: 1.00)*
- [x] El acierto de tema aparece en el resumen. **Esperado:** ≥ 0.80 (en la prueba: 1.00). *(Resultado: 1.00)*
- [ ] **Prueba negativa:** subir temporalmente el umbral de tema a `1.01` en `config/modelo.yaml` hace que `3-desplegar-gate` falle y que `4-puntuar` y `5-monitorear` no corran. Después se revierte. *(Pendiente)*

### Lote puntuado (`4-puntuar`, artefacto `lote-puntuado` → `lote_01_puntuado.csv`)
- [x] **86** filas, sin `comentario_id` repetidos.
- [x] Tiene todas las columnas de `requerimientos.md`. `modelo_version`, `run_id` y `fecha_puntuacion` no están vacías en ninguna fila, y `run_id` coincide con el número de la ejecución. *(`run_id = 40055836663`)*
- [x] Sospechosos: **5**: 3 con `5_estrellas_texto_negativo` y 2 con `1_estrella_texto_positivo`, cada uno con `palabras_clave`.
- [x] `c1_0902` tiene `es_sospechoso = false` y `motivo_sospecha = sin_calificacion`.
- [x] Ningún comentario contiene un correo, un teléfono o un documento sin enmascarar (lo cubren las pruebas de `tests/test_enmascarar.py`).
- [ ] **Reproducible:** volver a correr el mismo commit da las mismas predicciones y la misma `modelo_version`. *(Parcial: las predicciones, confianzas y palabras clave del lote 2 son idénticas entre la corrida local y la de GitHub. Falta un "Re-run all jobs" del mismo commit para confirmar que la `modelo_version` se repite.)*

### Monitoreo (`5-monitorear`, resumen de la ejecución y artefacto `reporte-monitoreo`)
- [x] `monitoreo/linea_base.json` existe en el PR y fue calculado con el lote 1.
- [x] El resumen muestra la tabla métrica / línea base / lote / diferencia / umbral / estado.
- [x] Valores esperados: baja confianza en sentimiento **≈ 4.7%**, en tema **≈ 15.1%**, palabras no vistas **≈ 1.6%**, sospechosos **≈ 5.8%**, negativos **≈ 36%**. *(Resultado: 4.7 · 15.1 · 1.6 · 5.8 · 36.0)*
- [x] Todas las diferencias contra la línea base son **0** y el encabezado dice **`✅ Sin deriva`**.
- [x] El reporte lista los 10 **textos distintos** con menor confianza en tema (con cuántas veces se repite cada uno) y los 5 sospechosos. *(Corrida 40056605584)*

## Con el lote 2 (`workflow_dispatch`, `lote = lote_02`): debe alertar

- [x] Calidad: **87** leídas, **2** excluidas (1 `duplicado` `c2_0006`, 1 `comentario_vacio` `c2_0901`), **85** válidas.
- [x] El gate pasa igual que con el lote 1 (no depende del lote).
- [x] 🔔 **La alerta se enciende.** Métricas esperadas contra la línea base:

| Métrica | Línea base (lote 1) | Lote 2 | Diferencia | ¿Cruza +10? |
|---|---|---|---|---|
| Baja confianza en sentimiento | ≈ 4.7% | ≈ 22.4% | ≈ +17.7 | 🔔 Sí |
| Baja confianza en tema | ≈ 15.1% | ≈ 40.0% | ≈ +24.9 | 🔔 Sí |
| Palabras no vistas | ≈ 1.6% | ≈ 19.2% | ≈ +17.6 | 🔔 Sí |
| Sospechosos (solo se reporta) | ≈ 5.8% | ≈ 10.6% | ≈ +4.8 | — |
| Negativos (solo se reporta) | ≈ 36% | ≈ 35% | ≈ −1 | — |

*(Resultado en GitHub: 22.4 (+17.7) · 40.0 (+24.9) · 19.2 (+17.6) · 10.6 (+4.8) · 35.3 (−0.7))*

- [x] Aparece una anotación `::warning::` por cada métrica que cruza el umbral, y el encabezado del resumen dice **`🔔 ALERTA DE DERIVA`**. *(3 anotaciones)*
- [x] **El job `5-monitorear` termina en verde**: la alerta avisa, no bloquea.
- [x] Entre los 10 textos distintos con menor confianza en tema aparecen los temas que el modelo no conoce: inglés ("Delivery took forever…"), reembolsos, soporte y propinas. *(Corrida 40056603411: aparecen los cuatro, además del sarcasmo "las mejores papas aguadas". En la primera corrida (40055854203) el top no agrupaba textos repetidos y solo mostraba reembolsos y soporte; por eso se cambió el reporte.)*
- [x] Sospechosos: **≈ 9**, incluidos los comentarios de reembolso con 1★ leídos como positivos. Son las falsas alarmas que explica la deriva. *(9, de los cuales 4 son de reembolso)*

**Por qué debe alertar:** el lote 2 trae comentarios en inglés y temas que no están en el entrenamiento (16 sobre reembolsos, soporte o propinas). El modelo no los inventa: los asigna a otro tema con poca confianza. Eso se ve en la baja confianza y en las palabras no vistas, no en el % de negativos.

## Qué bloquea el merge y qué solo advierte

| Bloquea el merge (job en rojo) | Solo advierte (job en verde + `::warning::`) |
|---|---|
| El lote no existe, no se puede leer, está vacío o le falta una columna (`1-calidad`) | Más del 20% de filas excluidas (`1-calidad`) |
| Falla `pytest` (`1-calidad`) | Alerta de deriva: +10 puntos en baja confianza o palabras no vistas (`5-monitorear`) |
| Falla el entrenamiento (`2-entrenar`) | |
| Sentimiento < 0.85 o tema < 0.80 en el golden set (`3-desplegar-gate`) | |
| Falla la puntuación (`4-puntuar`) | |
| Falta `monitoreo/linea_base.json` (`5-monitorear`) | |

- [x] Los 5 jobs están marcados como *required status checks* en el ruleset de `main`. *(Ruleset `proteger-main`, activo)*
- [x] Al PR se adjunta el enlace a la ejecución del lote 2 (o una captura) con la alerta visible.
