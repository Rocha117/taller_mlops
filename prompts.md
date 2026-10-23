# Guía de prompts del taller SDD para MLOps

Aquí **no hay prompts listos**. Hay un esqueleto por cada parte de SDD: el marco ya está escrito, y los espacios `[ ... ]` los completas tú con tu grupo, respondiendo las preguntas guía. Cuando tu prompt esté completo, lo pegas en tu asistente de IA, abierto dentro de la carpeta del repo.

> Tip: si no sabes qué poner en un espacio, vuelve a [`negocio/input-negocio.md`](negocio/input-negocio.md) y a los datos de `data/`. La respuesta está ahí, o en una tensión entre dos stakeholders que tienes que resolver.

---

## Prompt 1 · Constitución

> Se usa **una sola vez**. La constitución responde tres preguntas: **Misión** (¿para qué?), **Stack tecnológico** (¿cómo encaja con la tecnología?) y **Roadmap** (¿qué está planificado?).

### Preguntas guía

**Misión** (`constitucion/mision.md`)
- ¿Qué decisión de negocio cambia gracias a este modelo? ¿Quién la toma?
- ¿Qué queda **dentro** y qué queda **fuera**? (Pista: ¿el modelo lo vamos a entrenar o a operar?)
- ¿**Qué modelo** operamos? Elígelo de la lista "Modelos que el equipo ya revisó" en el input del negocio, con uno de respaldo, y di por qué. No vale inventar uno.
- ¿Cómo sabremos que funciona? Piensa en **un KPI de negocio** y en **un KPI del modelo**.

**Stack tecnológico** (`constitucion/stack-tecnologico.md`)
- ¿En qué plataforma corre el modelo que eligieron? ¿Cómo se resuelve el tema si el modelo solo da sentimiento? ¿Cuál es el respaldo si mañana cambiamos?
- ¿Qué tiene que vivir en Git para que un cambio de modelo se pueda revisar?
- Las 4 preguntas de operación: ¿cómo se **despliega**, cómo se **monitorea**, cuándo se **reajusta** y quién **aprueba o revierte**?
- ¿Qué riesgos trae guardar la salida de una IA como dato productivo? ¿Qué controles ponemos?
- ¿Cómo cuidamos el costo?

**Roadmap** (`constitucion/roadmap.md`)
- ¿Qué tiene que existir primero para poder operar el modelo con seguridad?
- ¿Qué viene después, cuando ya está en producción?
- ¿Cuántas fases? (En clase trabajamos con **dos**.)

### Esqueleto del prompt

```text
Actúa como arquitecto/a de datos y ML de nuestro equipo. Vamos a operar en
producción el modelo de IA de PideYa, que [ qué hace el modelo con cada
comentario ].

Lee negocio/input-negocio.md y revisa data/source/ y data/eval/golden_set.csv.

Crea la constitución del proyecto en constitucion/, en español, con tres
archivos:

1. constitucion/mision.md
   - [ para qué existe el modelo y para quién ]
   - [ qué queda dentro y qué queda fuera ]
   - [ modelo elegido de la lista de negocio/input-negocio.md, respaldo y por qué ]
   - [ KPI de negocio y KPI del modelo ]

2. constitucion/stack-tecnologico.md
   - [ plataforma donde corre el modelo elegido y cómo se obtiene el tema ]
   - [ qué se versiona en Git y qué guarda cada fila de salida ]
   - Desplegar: [ ... ]
   - Monitorear: [ ... ]
   - Reajustar: [ ... ]
   - Aprobar y revertir: [ ... ]
   - Gobierno de IA: [ ... ]
   - Costo: [ ... ]

3. constitucion/roadmap.md
   - [ fase 1: objetivo y qué entrega ]
   - [ fase 2: objetivo, qué entrega y de qué depende ]

Reglas:
- ANTES de escribir cualquier archivo, hazme todas las preguntas que
  necesites, agrupadas en Misión, Stack tecnológico y Roadmap. Espera mis
  respuestas.
- No escribas código. Solo la constitución.
- Usa solo modelos de la lista de negocio/input-negocio.md. No propongas otros.
- Si dos stakeholders piden cosas que chocan, pregúntame en vez de suponer.
- Al terminar, muéstrame un resumen de cada archivo para que yo lo apruebe.
```

**Para discutir en grupo antes de pegarlo:** ¿qué tensiones encuentras entre Lucía y Patricia, entre Martín y la comparación con los meses anteriores, y entre Valeria y Jorge? ¿Cómo las resuelve tu constitución?

✅ **Resultado esperado:** tres archivos en `constitucion/` que tu grupo revisó y aprobó.

---

## Prompt 2 · Feature Spec

> Se usa **una vez por cada fase** del roadmap. En clase hacemos la **fase 1**. La feature spec responde: **Scope + Requirements** (¿qué construye y qué restricciones importan?), **Plan** (¿en qué tareas se divide?) y **Validation** (¿cómo sabemos que está listo?).

### Preguntas guía

**Requerimientos** (`requerimientos.md`)
- ¿Qué construye esta fase y qué **no**?
- ¿Qué entra al modelo y qué sale? ¿Qué columnas necesitas para saber **qué versión** produjo cada fila?
- ¿Qué hacemos **antes** de llamar al modelo con un comentario vacío, uno de 2 letras, uno sin calificación o uno duplicado?
- ¿Cómo se evalúa una versión contra el golden set? ¿Qué métrica y qué umbral?
- ¿Qué cuenta como **comentario sospechoso** y qué motivo se guarda?
- ¿Qué pasa con los datos personales que vienen en el texto?

**Plan** (`plan.md`)
- ¿En qué orden se construye? ¿Qué archivo toca cada tarea?

**Validación** (`validacion.md`)
- ¿Qué número exacto debería dar cada criterio con el **lote 1**?
- ¿Qué criterio debería **encender una alerta** con el **lote 2**? ¿Por qué?
- ¿Qué bloquea el despliegue y qué solo genera una advertencia?

### Esqueleto del prompt

```text
Lee constitucion/roadmap.md y toma la siguiente fase que aún no tenga carpeta
en specs/. Crea una rama de git para esa fase (nunca trabajes en main).

Crea specs/AAAA-MM-DD-nombre-de-la-fase/ con tres archivos en español:

1. requerimientos.md
   - Scope: [ ... ]
   - Contrato de entrada y de salida: [ ... ]
   - Reglas de datos antes del modelo: [ ... ]
   - Gate de despliegue: [ ... ]
   - Comentarios sospechosos: [ ... ]
   - Restricciones (datos personales, costo, idempotencia): [ ... ]
   - Decisiones tomadas y su motivo.

2. plan.md
   - Tareas pequeñas y numeradas, cada una con el archivo que crea o modifica.

3. validacion.md
   - Criterios medibles como casillas [ ], con cómo se comprueban y el
     resultado esperado con el lote 1.
   - [ el criterio que debe alertar con el lote 2 ]
   - [ qué bloquea y qué solo advierte ]

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
