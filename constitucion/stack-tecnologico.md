# Stack tecnológico · Cómo se opera el modelo

Este documento fija **cómo** se entrena, publica, monitorea y gobierna el modelo. Cada feature spec en `specs/` tiene que respetarlo; si una fase necesita contradecirlo, primero se cambia la constitución por Pull Request.

## Modelo

- **Qué es:** scikit-learn, **TF-IDF + regresión logística**, con **dos modelos independientes**: uno para `sentimiento` y otro para `tema` (lo eligió el equipo en `negocio/input-negocio.md` y no se cambia aquí).
- **Cómo se entrena:** dentro del pipeline, nunca en una laptop. Con `data/train/comentarios_entrenamiento.csv` y los parámetros guardados en un archivo de configuración versionado en Git (por ejemplo `config/modelo.yaml`), con semilla fija para que dos corridas con el mismo commit den el mismo modelo.
- **El golden set** (`data/eval/golden_set.csv`) **nunca** se usa para entrenar. Es solo el examen.
- **Dónde se guarda el artefacto:** cada corrida guarda los dos modelos (`.joblib`) y un `metadata.json` como **artefacto de la ejecución de GitHub Actions**. El `metadata.json` contiene: versión, commit, fecha, hash del archivo de entrenamiento, parámetros y resultado del golden set.
- **Cómo se versiona:** `modelo_version = AAAA.MM.DD-<sha corto del commit>` (por ejemplo `2026.10.23-216cd61`). La misma versión aparece en el artefacto, en el reporte y en cada fila puntuada.

## Orquestación: GitHub Actions

Sin secrets, sin servicios pagados y sin servidores encendidos. Un workflow con **un job por stage**, en este orden:

| # | Stage | Qué hace | Si algo sale mal |
|---|---|---|---|
| 1 | **Calidad del lote** | Valida el CSV del lote: columnas esperadas, tipos, comentarios vacíos o muy cortos, calificación faltante, duplicados. Las filas malas se **excluyen y se cuentan**, no se corrigen a mano. | 🛑 **Detiene** si el archivo no se puede usar (falta una columna, está vacío, no se puede leer). ⚠️ **Avisa** si se excluye más del 20% de las filas. |
| 2 | **Entrenar** | Entrena sentimiento y tema con `data/train/`. | 🛑 **Detiene** si falla. |
| 3 | **Desplegar (gate)** | Evalúa los dos modelos contra el golden set. | 🛑 **Detiene** si sentimiento < 85% o tema < 80% de acierto. El modelo no se publica. |
| 4 | **Puntuar** | Predice el lote limpio, enmascara datos personales, marca sospechosos y guarda la versión del modelo en cada fila. | 🛑 **Detiene** si falla. |
| 5 | **Monitorear** | Compara el lote contra la línea base y publica el reporte. | ⚠️ **Solo avisa.** La deriva no pone el pipeline en rojo. |

**Regla general:** se detiene lo que hace que el resultado no sea confiable (dato inservible, modelo que no aprueba el examen). La deriva **avisa**, porque es información para decidir un reentrenamiento, no un error del pipeline. Así se evita que Valeria y el equipo reciban un pipeline rojo cada vez que cambia el lote.

### Cuándo corre

| Disparador | Lote que usa | Para qué |
|---|---|---|
| **Pull Request hacia `main`** | Lote 1 (`comentarios_lote_01.csv`) | Ningún cambio de código, parámetros o datos llega a `main` sin el pipeline en verde. |
| **Manual (`workflow_dispatch`)** con input `lote` (`lote_01` o `lote_02`) | El elegido | Probar un lote concreto, por ejemplo para ver la alerta con el lote 2. |
| **Programado** cada lunes 08:00 hora de Lima (`cron: "0 13 * * 1"`) | El lote más reciente de `data/source/` | Monitoreo semanal, antes de la revisión de Valeria. |

## Versionamiento y ramas

- **`main` está protegida:** solo entra por Pull Request y con los checks del pipeline en verde. No hay push directo.
- **Una rama por fase o cambio** (por ejemplo `fase-1-desplegar-monitorear`). La spec, el código y la configuración viajan juntos en el mismo PR.
- Código, parámetros, línea base y specs viven en **Git**. Los modelos entrenados y los lotes puntuados viven como **artefactos** de la ejecución, no en Git.

## Las 4 preguntas de operación

### Desplegar · ¿Cómo sale a producción?
Un modelo "sale" cuando aprueba el **gate**: sentimiento ≥ 85% y tema ≥ 80% de acierto en el golden set. El acierto aparece en el resumen de la ejecución. Si no aprueba, no se puntúa ningún lote con ese modelo.

### Monitorear · ¿Cómo sé que sigue bien?
- **Línea base:** las métricas del **lote 1** puntuado con el modelo publicado, guardadas en Git en `monitoreo/linea_base.json`. Se actualiza solo por Pull Request (por ejemplo, cuando se publica un modelo nuevo).
- **Métricas por lote:**
  - % de comentarios con **baja confianza** (probabilidad máxima < 0.5), por separado en sentimiento y en tema.
  - % de **palabras no vistas** al entrenar.
  - Distribución de sentimiento y de tema.
  - % de comentarios **sospechosos**.
  - % de filas excluidas por calidad.
- **Umbral de alerta:** el % de baja confianza (en sentimiento **o** en tema) sube **más de 10 puntos** sobre la línea base. Como señal de apoyo, también alerta si el % de palabras no vistas sube más de 10 puntos.
- **Por qué no el % de negativos:** en el lote 2 casi no cambia (36% → 35%), aunque el modelo duda mucho más. Mirarlo solo daría una falsa tranquilidad.
- **Dónde se ve:** una tabla "lote vs línea base" en el **resumen de la ejecución** (`GITHUB_STEP_SUMMARY`), una **advertencia** (`::warning::`) visible en el PR y en la ejecución, y el reporte completo (`.md` y `.json`) como **artefacto**.
- **Temas nuevos (lo que pide Martín):** el reporte lista los comentarios de baja confianza en tema y los que tienen más palabras no vistas, para que Producto vea de qué se está hablando. El catálogo de temas no cambia en la fase 1.

### Reentrenar · ¿Cuándo se actualiza?
- **Señal:** una alerta de deriva, o la llegada de nuevos comentarios etiquetados por personas (por ejemplo, los que revisa el equipo de Valeria o los temas nuevos que defina Producto).
- **Datos:** `data/train/` más los nuevos comentarios etiquetados. Nunca el golden set y nunca predicciones del propio modelo como si fueran etiquetas.
- La alerta **propone** reentrenar (lo que pide Lucía), pero **no publica** nada por sí sola. Se construye en la fase 2.

### Aprobar y revertir · ¿Quién decide y cómo vuelvo?
- **Retador vs actual:** el modelo nuevo (retador) solo reemplaza al actual si **aprueba el gate y no es peor que el actual** en el golden set, en sentimiento ni en tema.
- **Aprobación humana (lo que pide Patricia):** además, una persona lo aprueba en GitHub mediante un **environment `produccion` con required reviewers**. Sin esa aprobación, el job de publicación espera.
- **Revertir en minutos:** cada modelo publicado se guarda como **GitHub Release** con su `modelo_version` (los artefactos de Actions vencen; las releases no). Revertir es volver a publicar la versión anterior, sin reentrenar. Se construye en la fase 2.

## Gobierno

- **Trazabilidad:** cada fila puntuada lleva `modelo_version`, `run_id` (la ejecución de GitHub Actions) y `fecha_puntuacion`.
- **Datos personales:** antes de guardar el lote puntuado, el texto se **enmascara** (teléfonos, correos, números de documento y nombres después de "me llamo" o "soy" se reemplazan por `[TELEFONO]`, `[CORREO]`, etc.). Los reportes nunca muestran datos personales sin enmascarar.
- **Sospechosos explicables:** cada comentario marcado guarda su **motivo** (por ejemplo `5★ con texto negativo`), la confianza del modelo y las palabras que más pesaron en la predicción.
- **Revisión humana:** el modelo marca y una persona decide. Ninguna salida del modelo cambia por sí sola un ranking o sanciona a nadie.
- **Cambios:** todo cambio a código, parámetros, umbrales o línea base pasa por Pull Request.

## Costo y tiempo

- **Costo cero:** repo público, runners `ubuntu-latest` gratuitos, sin APIs pagadas ni secrets.
- **Rápido:** la meta es que la corrida completa tarde **menos de 5 minutos**. Cada job tiene `timeout-minutes: 10` y se usa la caché de `pip`.
- **Solo lo nuevo:** cada corrida procesa un solo lote (los comentarios de esa semana) y quita duplicados por `comentario_id`. Si se corre dos veces el mismo lote con el mismo modelo, el resultado es idéntico (idempotente).
- **Retención:** los artefactos de cada ejecución se guardan 30 días; los modelos publicados, como releases.

## Alternativas equivalentes

| Herramienta | Uso | Alternativa si cambiamos |
|---|---|---|
| scikit-learn (TF-IDF + regresión logística) | Modelo | Un modelo de Hugging Face (por ejemplo, BETO para español) o las funciones de IA de la plataforma de datos |
| GitHub Actions | Orquestación y CI | GitLab CI, Azure DevOps Pipelines, Airflow o Databricks Workflows |
| Artefactos de Actions + GitHub Releases | Registro de modelos | MLflow Model Registry o un bucket S3/GCS versionado |
| `monitoreo/linea_base.json` + resumen de la ejecución | Monitoreo | Evidently AI, WhyLabs o Databricks Lakehouse Monitoring |
| Environment con required reviewers | Aprobación humana | Aprobación manual en GitLab o etapas de aprobación de MLflow |
| Rama protegida + Pull Request | Gobierno de cambios | Merge requests protegidos en GitLab, Azure Repos |

Las 4 preguntas de operación y esta constitución serían las mismas con cualquiera de estas alternativas.
