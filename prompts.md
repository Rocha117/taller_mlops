# Guía de prompts del taller SDD para MLOps

Los Prompts 1 y 2 **no vienen listos**. Hay un esqueleto por cada parte de SDD: el marco ya está escrito, y los espacios `[ ... ]` los completas tú con tu grupo, respondiendo las preguntas guía. El Prompt 3 sí viene completo: construye lo que tu spec dice.

> Tip: si no sabes qué poner en un espacio, vuelve a [`negocio/input-negocio.md`](negocio/input-negocio.md) y a los datos de `data/`. La respuesta está ahí, o en una tensión entre dos stakeholders que tienes que resolver.

---

## Prompt 1 · Constitución

> Se usa **una sola vez**. La constitución responde tres preguntas: **Misión** (¿para qué?), **Stack tecnológico** (¿cómo encaja con la tecnología?) y **Roadmap** (¿qué está planificado?).

### Preguntas guía

**Misión** (`constitucion/mision.md`)
- ¿Qué decisión de negocio cambia gracias a este modelo? ¿Quién la toma?
- ¿Qué queda **dentro** y qué queda **fuera**? (Pista: ¿vamos a inventar un modelo mejor o a operar el que eligió el equipo?)
- ¿Cómo sabremos que funciona? Piensa en **un KPI de negocio** y en **un KPI del modelo**.

**Stack tecnológico** (`constitucion/stack-tecnologico.md`)
- El modelo ya está elegido en el input del negocio. ¿Qué dice la constitución sobre cómo se entrena, dónde se guarda el artefacto y cómo se versiona?
- ¿Qué stages tiene el pipeline y en qué orden? ¿Qué stage **detiene** el pipeline y cuál solo **avisa**?
- Las 4 preguntas de operación: ¿cómo se **despliega**, cómo se **monitorea**, cuándo se **reentrena** y quién **aprueba o revierte**?
- ¿Qué riesgos trae usar la salida de un modelo como dato productivo? ¿Qué controles ponemos (versión en cada fila, datos personales, revisión humana)?
- ¿Cómo cuidamos el costo y el tiempo de cada corrida?
- Si mañana cambiamos de modelo u orquestador, ¿cuál sería la alternativa?

**Roadmap** (`constitucion/roadmap.md`)
- ¿Qué tiene que existir primero para poder operar el modelo con seguridad?
- ¿Qué viene después, cuando ya está en producción?
- Son **dos** fases. ¿Cuál cubre desplegar y monitorear, y cuál reentrenar, aprobar y revertir?

### Esqueleto del prompt

```text
Actúa como arquitecto/a de datos y ML de nuestro equipo. Vamos a operar en
producción el modelo de PideYa, que [ qué hace el modelo con cada
comentario ].

Lee negocio/input-negocio.md (stakeholders y modelo elegido) y revisa
data/train/, data/eval/ y data/source/.

Crea la constitución del proyecto en constitucion/, en español, con tres
archivos:

1. constitucion/mision.md
   - [ para qué existe el modelo y para quién ]
   - [ qué queda dentro y qué queda fuera ]
   - [ KPI de negocio y KPI del modelo ]

2. constitucion/stack-tecnologico.md
   - Modelo: el elegido en negocio/input-negocio.md. [ cómo se entrena,
     dónde se guarda el artefacto y cómo se versiona ]
   - Orquestación: GitHub Actions, sin secrets ni servicios pagados.
     [ stages del pipeline, en orden; cuáles detienen y cuáles avisan ]
   - Versionamiento y ramas: [ ... ]
   - Desplegar: [ ... ]
   - Monitorear: [ ... ]
   - Reentrenar: [ ... ]
   - Aprobar y revertir: [ ... ]
   - Gobierno: [ ... ]
   - Costo: [ ... ]
   - Para cada herramienta, una alternativa equivalente.

3. constitucion/roadmap.md
   - [ fase 1: objetivo, qué entrega ]
   - [ fase 2: objetivo, qué entrega y de qué depende ]

Reglas:
- ANTES de escribir cualquier archivo, hazme todas las preguntas que
  necesites, agrupadas en Misión, Stack tecnológico y Roadmap. Espera mis
  respuestas.
- No escribas código. Solo la constitución.
- No cambies el modelo elegido en negocio/input-negocio.md.
- Si dos stakeholders piden cosas que chocan, pregúntame en vez de suponer.
- Al terminar, muéstrame un resumen de cada archivo para que yo lo apruebe.
```

**Para discutir en grupo antes de pegarlo:** ¿qué tensiones encuentras entre Lucía y Patricia (reentrenar automático vs aprobación humana), entre Martín y la comparación con los meses anteriores, y entre Valeria y las falsas alarmas? ¿Cómo las resuelve tu constitución?

✅ **Resultado esperado:** tres archivos en `constitucion/` que tu grupo revisó y aprobó.

---

## Prompt 2 · Feature Spec

> Se usa **una vez por cada fase** del roadmap. En clase hacemos la **fase 1**. La feature spec responde: **Scope + Requirements** (¿qué construye y qué restricciones importan?), **Plan** (¿en qué tareas se divide?) y **Validation** (¿cómo sabemos que está listo?).

### Preguntas guía

**Requerimientos** (`requerimientos.md`)
- ¿Qué construye esta fase y qué **no**?
- ¿Qué entra a cada stage y qué sale? ¿Qué columnas necesitas para saber **qué versión** del modelo puntuó cada fila?
- ¿Qué hacemos **antes** de puntuar con un comentario vacío, uno de 2 letras, uno sin calificación o uno duplicado?
- ¿Cómo se evalúa el modelo contra el golden set? ¿Qué métrica y qué umbral para sentimiento y para tema?
- ¿Qué cuenta como **comentario sospechoso** y qué motivo se guarda?
- ¿Qué compara el monitoreo entre el lote y la línea base? ¿Qué número enciende la alerta?
- ¿Qué pasa con los datos personales que vienen en el texto?

**Plan** (`plan.md`)
- ¿En qué orden se construye? ¿Qué archivo toca cada tarea?

**Validación** (`validacion.md`)
- ¿Qué número exacto debería dar cada criterio con el **lote 1**?
- ¿Qué criterio debería **encender una alerta** con el **lote 2**? ¿Por qué?
- ¿Qué bloquea el merge y qué solo genera una advertencia?

### Esqueleto del prompt

```text
Lee constitucion/roadmap.md y toma la siguiente fase que aún no tenga carpeta
en specs/. Crea una rama de git para esa fase (nunca trabajes en main).

Crea specs/AAAA-MM-DD-nombre-de-la-fase/ con tres archivos en español:

1. requerimientos.md
   - Scope: [ ... ]
   - Stages del pipeline, con entrada y salida de cada uno: [ ... ]
   - Reglas de datos antes de puntuar: [ ... ]
   - Gate de despliegue (métrica y umbral): [ ... ]
   - Comentarios sospechosos: [ ... ]
   - Monitoreo (qué se compara y qué enciende la alerta): [ ... ]
   - Restricciones (datos personales, costo, idempotencia, trazabilidad): [ ... ]
   - Decisiones tomadas y su motivo.

2. plan.md
   - Tareas pequeñas y numeradas, cada una con el archivo que crea o modifica.

3. validacion.md
   - Criterios medibles como casillas [ ], con cómo se comprueban (en qué
     stage, con qué archivo o reporte) y el resultado esperado con el lote 1.
   - [ el criterio que debe alertar con el lote 2 ]
   - [ qué bloquea el merge y qué solo advierte ]

Usa como guía la constitución. Si esta fase la contradice, avísame.

Reglas:
- ANTES de escribir cualquier archivo, hazme todas las preguntas que
  necesites, agrupadas en Scope, Requerimientos y Validación. Espera mis
  respuestas.
- No escribas código. Solo la spec de esta fase.
- Al terminar, muéstrame un resumen de los tres archivos para que yo lo apruebe.
```

**Para discutir en grupo antes de pegarlo:** si mañana llega el lote 2 a producción, ¿tu spec lo detecta? Si la respuesta es "no sé", todavía falta algo.

✅ **Resultado esperado:** `specs/AAAA-MM-DD-<fase>/` con `requerimientos.md`, `plan.md` y `validacion.md`, en su propia rama.

---

## Prompt 3 · Construir desde la spec

> Se usa **después de aprobar** la feature spec. Este sí viene completo; cambia la fecha y el nombre de la fase por los tuyos.

```text
Implementa el plan de specs/AAAA-MM-DD-nombre-de-la-fase/plan.md, una tarea a
la vez, respetando requerimientos.md y constitucion/stack-tecnologico.md.

- El modelo es el elegido en negocio/input-negocio.md. Escríbelo en Python y
  deja las dependencias en requirements.txt con versiones fijas.
- El pipeline corre en GitHub Actions en cada Pull Request hacia main, con un
  job por stage, sin secrets ni servicios pagados.
- Guarda el modelo entrenado y los reportes como artefactos de la ejecución.
- Documenta en el README qué hace cada script y en qué stage corre.
- Después de cada grupo de tareas, dime qué archivos cambiaste.
- Si una tarea no se puede hacer como dice la spec, detente y pregúntame; no
  cambies la spec por tu cuenta.
- Trabaja solo en la rama de esta fase. Prepara el Pull Request hacia main,
  pero no hagas merge: el merge se hace cuando el pipeline está en verde.
- Al final, recorre validacion.md y dime qué criterios puedo comprobar ahora
  y cómo, incluido cómo correr el pipeline con el lote 2.
```

✅ **Resultado esperado:** el pipeline en verde con el lote 1 y la alerta visible con el lote 2.
