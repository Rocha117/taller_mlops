# Fase 1 · Desplegar y monitorear · Validación

Cada criterio dice dónde se comprueba y qué resultado se espera. Los valores "≈" salen de una prueba exploratoria con los parámetros de `config/modelo.yaml`; se aceptan diferencias de ±3 puntos porcentuales por detalles de tokenización, siempre que la conclusión (alerta sí / no) se mantenga.

## Con el lote 1 (Pull Request hacia `main`)

### Pipeline
- [ ] El PR muestra los 5 jobs: `1-calidad`, `2-entrenar`, `3-desplegar-gate`, `4-puntuar` y `5-monitorear`. **Esperado:** todos en verde.
- [ ] La corrida completa tarda menos de 5 minutos. **Dónde:** duración total de la ejecución en la pestaña Actions.
- [ ] `pytest` pasa en `1-calidad`. **Dónde:** log del job.

### Calidad del lote (`1-calidad`, artefacto `calidad` → `calidad.json`)
- [ ] Filas leídas: **89**.
- [ ] Excluidas: **3**: 1 `duplicado` (`c1_0004`), 1 `comentario_vacio` (`c1_0901`) y 1 `comentario_muy_corto` (`c1_0903`, "ok"). % excluido: **3.4%**, sin advertencia (< 20%).
- [ ] Sin calificación: **1** (`c1_0902`): se puntúa.
- [ ] Filas válidas: **86**.

### Gate (`3-desplegar-gate`, resumen de la ejecución y `gate.json`)
- [ ] El acierto de sentimiento en el golden set aparece en el resumen. **Esperado:** ≥ 0.85 (en la prueba: 1.00).
- [ ] El acierto de tema aparece en el resumen. **Esperado:** ≥ 0.80 (en la prueba: 1.00).
- [ ] **Prueba negativa:** subir temporalmente el umbral de tema a `1.01` en `config/modelo.yaml` hace que `3-desplegar-gate` falle y que `4-puntuar` y `5-monitorear` no corran. Después se revierte.

### Lote puntuado (`4-puntuar`, artefacto `lote-puntuado` → `lote_01_puntuado.csv`)
- [ ] **86** filas, sin `comentario_id` repetidos.
- [ ] Tiene todas las columnas de `requerimientos.md`. `modelo_version`, `run_id` y `fecha_puntuacion` no están vacías en ninguna fila, y `run_id` coincide con el número de la ejecución.
- [ ] Sospechosos: **5**: 3 con `5_estrellas_texto_negativo` y 2 con `1_estrella_texto_positivo`, cada uno con `palabras_clave`.
- [ ] `c1_0902` tiene `es_sospechoso = false` y `motivo_sospecha = sin_calificacion`.
- [ ] Ningún comentario contiene un correo, un teléfono o un documento sin enmascarar (lo cubren las pruebas de `tests/test_enmascarar.py`).
- [ ] **Reproducible:** volver a correr el mismo commit da las mismas predicciones y la misma `modelo_version`.

### Monitoreo (`5-monitorear`, resumen de la ejecución y artefacto `reporte-monitoreo`)
- [ ] `monitoreo/linea_base.json` existe en el PR y fue calculado con el lote 1.
- [ ] El resumen muestra la tabla métrica / línea base / lote / diferencia / umbral / estado.
- [ ] Valores esperados: baja confianza en sentimiento **≈ 4.7%**, en tema **≈ 15.1%**, palabras no vistas **≈ 1.6%**, sospechosos **≈ 5.8%**, negativos **≈ 36%**.
- [ ] Todas las diferencias contra la línea base son **0** y el encabezado dice **`✅ Sin deriva`**.
- [ ] El reporte lista los 10 comentarios con menor confianza en tema y los 5 sospechosos.

## Con el lote 2 (`workflow_dispatch`, `lote = lote_02`): debe alertar

- [ ] Calidad: **87** leídas, **2** excluidas (1 `duplicado` `c2_0006`, 1 `comentario_vacio` `c2_0901`), **85** válidas.
- [ ] El gate pasa igual que con el lote 1 (no depende del lote).
- [ ] 🔔 **La alerta se enciende.** Métricas esperadas contra la línea base:

| Métrica | Línea base (lote 1) | Lote 2 | Diferencia | ¿Cruza +10? |
|---|---|---|---|---|
| Baja confianza en sentimiento | ≈ 4.7% | ≈ 22.4% | ≈ +17.7 | 🔔 Sí |
| Baja confianza en tema | ≈ 15.1% | ≈ 40.0% | ≈ +24.9 | 🔔 Sí |
| Palabras no vistas | ≈ 1.6% | ≈ 19.2% | ≈ +17.6 | 🔔 Sí |
| Sospechosos (solo se reporta) | ≈ 5.8% | ≈ 10.6% | ≈ +4.8 | — |
| Negativos (solo se reporta) | ≈ 36% | ≈ 35% | ≈ −1 | — |

- [ ] Aparece una anotación `::warning::` por cada métrica que cruza el umbral, y el encabezado del resumen dice **`🔔 ALERTA DE DERIVA`**.
- [ ] **El job `5-monitorear` termina en verde**: la alerta avisa, no bloquea.
- [ ] Entre los comentarios con menor confianza en tema aparecen los temas que el modelo no conoce: inglés ("Delivery took forever…"), reembolsos, soporte y propinas.
- [ ] Sospechosos: **≈ 9**, incluidos los comentarios de reembolso con 1★ leídos como positivos. Son las falsas alarmas que explica la deriva.

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

- [ ] Los 5 jobs están marcados como *required status checks* en el ruleset de `main`.
- [ ] Al PR se adjunta el enlace a la ejecución del lote 2 (o una captura) con la alerta visible.
