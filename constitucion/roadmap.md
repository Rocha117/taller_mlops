# Roadmap de operación

Dos fases. Juntas responden las 4 preguntas de operación: **desplegar, monitorear, reentrenar y aprobar/revertir**. Cada fase tiene su propia feature spec en `specs/AAAA-MM-DD-<fase>/`, su rama y su Pull Request.

## Fase 1 · Desplegar y monitorear (en clase)

**Objetivo:** que el modelo deje de vivir en una laptop. Se entrena, se examina, puntúa el lote semanal y avisa cuando el lote se aleja de lo que conoce, todo dentro del pipeline y sin intervención manual.

**Responde:** Desplegar · Monitorear.

**Entrega:**
- Código del modelo en Python (scikit-learn) con dependencias fijas en `requirements.txt` y parámetros versionados en Git.
- Workflow de GitHub Actions con 5 jobs: **calidad del lote → entrenar → desplegar (gate) → puntuar → monitorear**.
- Disparadores: en cada Pull Request hacia `main`, manual eligiendo el lote (`lote_01` / `lote_02`) y programado cada lunes.
- Gate con el golden set: sentimiento ≥ 85% y tema ≥ 80%; si no llega, el pipeline se detiene.
- Lote puntuado con `modelo_version`, `run_id` y `fecha_puntuacion` en cada fila, texto enmascarado y sospechosos con su motivo.
- Línea base del lote 1 en `monitoreo/linea_base.json` y reporte de monitoreo en el resumen de la ejecución y como artefacto.
- Alerta de deriva (solo avisa) cuando el % de baja confianza sube más de 10 puntos.

**Listo cuando:** el pipeline está en **verde con el lote 1**, la **alerta se enciende con el lote 2** y el PR se puede hacer merge a `main`.

**Depende de:** nada; es la base.

## Fase 2 · Reentrenar, aprobar y revertir (tarea)

**Objetivo:** que el modelo se pueda actualizar sin miedo: un modelo nuevo solo entra si es mejor y una persona lo aprueba, y si sale mal se vuelve al anterior en minutos.

**Responde:** Reentrenar · Aprobar y revertir.

**Entrega:**
- Stage **Reentrenar**: entrena un modelo **retador** con `data/train/` más nuevos comentarios etiquetados por personas, disparado a mano o a partir de una alerta de deriva.
- Stage **Aprobar**: compara retador vs actual en el golden set; el retador solo pasa si aprueba el gate y no es peor que el actual. Luego espera la aprobación de una persona en el environment `produccion` (required reviewers).
- Publicación del modelo aprobado como **GitHub Release** con su `modelo_version`, y actualización de la línea base por Pull Request.
- Stage **Revertir**: vuelve a publicar la versión anterior desde su release, sin reentrenar.
- Camino para incorporar temas nuevos (lo que pide Martín) mediante datos etiquetados y reentrenamiento, manteniendo comparables los temas existentes.

**Listo cuando:** se puede reentrenar con datos nuevos, el reemplazo espera la aprobación humana y se puede revertir a la versión anterior.

**Depende de:** la fase 1 (pipeline, gate, versionado del modelo, línea base y alerta de deriva).
