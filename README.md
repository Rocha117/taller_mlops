# Taller SDD para MLOps: del modelo en una laptop a un modelo operado

Taller práctico de **Spec-Driven Development (SDD)** aplicado a MLOps. El ciclo de vida del modelo ya lo vieron. Aquí trabajamos lo que viene **después**: cómo se opera un modelo. Primero escribimos **qué** tiene que cumplir el modelo en producción y **cómo sabremos que sigue bien**. Después, tu asistente de IA construye el pipeline desde esa spec.

El caso es **PideYa**, una app de delivery que usa un modelo para ponerle sentimiento y tema a los comentarios de sus clientes.

```
Desplegar  →  Monitorear  →  Reentrenar  →  Aprobar y revertir
```

> **Idea clave:** no te cases con ninguna herramienta. Usamos scikit-learn y GitHub Actions porque son gratis y corren en minutos, pero la spec de operación sería la misma con otro modelo u otro orquestador. Lo que se queda contigo es el método.

---

## ¿Qué vas a construir?

1. **La constitución** del proyecto (`constitucion/`): la misión del modelo, el stack tecnológico y el roadmap de operación.
2. **La feature spec de la fase 1**: requerimientos, plan y validación.
3. **El pipeline de la fase 1**, que tu asistente construye a partir de la spec y que corre en **GitHub Actions**: entrena el modelo, lo evalúa, puntúa el lote y lo monitorea. Nada llega a `main` sin que el pipeline esté en verde.
4. **De tarea, la fase 2**: reentrenar, aprobar y revertir.

## El pipeline que vas a especificar

No te lo damos hecho: lo describes en la spec y tu asistente lo construye. Esta es la forma que pide el negocio:

```
Fase 1 · en clase
rama de la fase ──► Pull Request ──────────────────────────────► merge a main
                     │                                          (solo en verde)
 1. Calidad del lote   valida el CSV antes de usarlo
 2. Entrenar           entrena sentimiento y tema con data/train/
 3. Desplegar (gate)   evalúa contra el golden set; si no llega al umbral, falla
 4. Puntuar            predice el lote y guarda la versión del modelo en cada fila
 5. Monitorear         compara el lote con la línea base, deja un reporte y avisa si hay deriva

 Además: correr a mano eligiendo el lote (lote 1 o lote 2) y, si tu spec lo pide, cada semana

Fase 2 · de tarea
 6. Reentrenar         entrena un modelo retador con datos nuevos
 7. Aprobar            el retador reemplaza al actual solo si gana y una persona aprueba
 8. Revertir           vuelve a publicar la versión anterior del modelo
```

## Las cuatro preguntas que tu spec tiene que responder

Son las mismas de la lámina "Operar un modelo: 4 preguntas":

| Pregunta | Pista para tu spec |
|---|---|
| **Desplegar** · ¿Cómo sale a producción? | ¿Qué examen tiene que aprobar un modelo antes de salir? Mira `data/eval/` |
| **Monitorear** · ¿Cómo sé que sigue bien? | ¿Qué cambió entre el lote 1 y el lote 2? ¿Qué número te lo hubiera avisado? |
| **Reentrenar** · ¿Cuándo se actualiza? | ¿Qué señal dispara un reentrenamiento? ¿Con qué datos? |
| **Aprobar y revertir** · ¿Quién decide y cómo vuelvo? | ¿Quién firma el cambio? ¿Qué necesitas guardar para volver atrás en minutos? |

## Las dos partes de SDD

| Parte | Pregunta que responde | Archivo |
|---|---|---|
| **Constitución** · Misión | ¿Para qué existe este modelo? ¿Para quién? ¿Qué KPI mueve? | `constitucion/mision.md` |
| **Constitución** · Stack tecnológico | ¿Cómo encaja con la tecnología? Gobierno, costo y restricciones | `constitucion/stack-tecnologico.md` |
| **Constitución** · Roadmap | ¿Qué fases de operación están planificadas y en qué orden? | `constitucion/roadmap.md` |
| **Feature Spec** · Scope + Requirements | ¿Qué construye esta fase? ¿Qué restricciones importan? | `specs/AAAA-MM-DD-fase/requerimientos.md` |
| **Feature Spec** · Plan | ¿En qué tareas se divide? | `specs/AAAA-MM-DD-fase/plan.md` |
| **Feature Spec** · Validation | ¿Cómo sabemos que ya está listo? | `specs/AAAA-MM-DD-fase/validacion.md` |

---

## Requisitos previos

- Una cuenta de **GitHub**. No necesitas Databricks, ni API keys, ni secrets: todo corre gratis en GitHub Actions.
- **Cualquier asistente de IA** que pueda leer y escribir archivos en tu repo, por ejemplo Claude Code, GitHub Copilot, Cursor o Gemini CLI.
- Git instalado en tu computadora (o usa GitHub Codespaces). Python 3 es opcional, solo si quieres probar en local.

## Estructura del repo

```
.
├── README.md                            ← este archivo
├── prompts.md                           ← guía para armar tus prompts + prompt para construir
├── constitucion/                        ← vacío al inicio; base de conocimiento del proyecto
├── negocio/
│   └── input-negocio.md                 ← lo que pidieron los stakeholders y el modelo elegido
├── data/
│   ├── train/
│   │   └── comentarios_entrenamiento.csv ← 300 comentarios etiquetados para entrenar
│   ├── eval/
│   │   └── golden_set.csv               ← 40 comentarios etiquetados: el examen del modelo
│   └── source/
│       ├── comentarios_lote_01.csv      ← lote de septiembre: la "foto normal"
│       └── comentarios_lote_02.csv      ← lote de octubre: llegó después
└── specs/                               ← vacío al inicio; una carpeta por cada feature
```

No hay código del modelo ni del pipeline al comenzar. **El código sale de la spec**, no al revés.

---

## Paso a paso

### 1. Crea tu copia del repo

Haz **fork** de este repositorio y clónalo:

```bash
git clone https://github.com/<tu-usuario>/<nombre-del-repo>.git
cd <nombre-del-repo>
```

En tu fork, entra a la pestaña **Actions** y pulsa **I understand my workflows, go ahead and enable them** (en los forks vienen apagadas).

✅ Checkpoint: ves `README.md`, `prompts.md`, `constitucion/`, `negocio/`, `data/` y `specs/`, y Actions está habilitado.

### 2. Protege la rama `main`

1. En tu fork: **Settings → Branches → Add branch ruleset** (o *Add rule*), aplicado a `main`.
2. Activa **Require a pull request before merging** y deja **desmarcada** la casilla **Require approvals** (GitHub no te deja aprobar tu propio PR). Si trabajas en pareja, puedes pedir 1 aprobación.
3. Activa **Require status checks to pass**. Los checks aparecen después de la primera ejecución del pipeline; vuelve a este paso para marcarlos.

> En cuentas gratuitas, la protección de ramas funciona en repos **públicos**. Mantén tu fork público.

✅ Checkpoint: un `git push` directo a `main` es rechazado.

### 3. Mira el dato antes de escribir nada

Abre los lotes, el golden set y el set de entrenamiento. Compara el lote 1 con el lote 2: ¿de qué se queja la gente en octubre que no aparecía en el entrenamiento? ¿En qué idioma escriben? ¿Cuántos comentarios tienen 5 estrellas y texto negativo?

✅ Checkpoint: tienes anotadas al menos dos diferencias entre los lotes. Las vas a usar en la constitución.

### 4. Escribe la constitución (Parte 1)

1. Lee [`negocio/input-negocio.md`](negocio/input-negocio.md): lo que pidieron Calidad de Restaurantes, Producto, Ingeniería, Gobierno y FinOps, y el modelo que eligió el equipo. Completa en clase "Lo que completamos en clase".
2. Con tu grupo, responde las preguntas guía del **Prompt 1 · Constitución** de [`prompts.md`](prompts.md), completa los espacios `[ ... ]` del esqueleto y pégalo en tu asistente.
3. El asistente **te hará preguntas antes de escribir**. Respóndelas como dueño del modelo.
4. Revisa los tres archivos que crea. **Tú apruebas la spec, no el asistente.**

✅ Checkpoint: existen `constitucion/mision.md`, `constitucion/stack-tecnologico.md` y `constitucion/roadmap.md`, y el roadmap tiene 2 fases que, juntas, cubren las 4 preguntas de operación.

```bash
git add constitucion/
git commit -m "docs: constitución del modelo de comentarios"
git push
```

### 5. Escribe la feature spec de la fase 1 (Parte 2)

1. Con tu grupo, responde las preguntas guía del **Prompt 2 · Feature Spec** de [`prompts.md`](prompts.md), completa el esqueleto y pégalo.
2. El asistente toma la **fase 1** del roadmap, crea una rama y te pregunta por el detalle.
3. Revisa `requerimientos.md`, `plan.md` y `validacion.md`. Pregúntate: *si mañana el lote 2 llega a producción, ¿esta spec me avisa?*

✅ Checkpoint: existe `specs/AAAA-MM-DD-<fase>/` con los tres archivos, en la rama de la fase.

### 6. Construye desde la spec

Usa el **Prompt 3 · Construir** de [`prompts.md`](prompts.md). Tu asistente escribe el código del modelo (Python con scikit-learn) y el workflow de GitHub Actions, **siguiendo tu spec**. Sube los cambios y abre un Pull Request hacia `main`:

```bash
git add .
git commit -m "feat: pipeline del modelo según spec"
git push -u origin <nombre-de-la-rama>
```

✅ Checkpoint: en el Pull Request ves los stages del pipeline (calidad, entrenar, desplegar, puntuar, monitorear) y todos terminan en **verde** con el lote 1.

### 7. Valida contra la spec

1. Recorre `validacion.md`: el gate muestra el acierto en el golden set, el lote puntuado guarda la versión del modelo y el reporte de monitoreo existe.
2. Corre el pipeline con el **lote 2** (como lo hayas definido en la spec: un input del workflow, otro archivo, etc.). El monitoreo tiene que **encender la alerta** que definiste.
3. Si todo cumple, haz merge a `main`. Si no, **corrige la spec o el código**, pero no "lo dejes pasar".

✅ Checkpoint: cada criterio de `validacion.md` está marcado y la alerta del lote 2 se ve en el reporte del pipeline.

### 8. De tarea: la fase 2

Vuelve al paso 5 con la fase 2 del roadmap: reentrenar, aprobar y revertir. Pista para la aprobación humana: en GitHub, un **environment** con *required reviewers* (Settings → Environments) hace que un job espere a que una persona lo apruebe. Es gratis en repos públicos.

---

## El resultado que entregas

Un **Pull Request en tu fork**, con:

- [ ] `constitucion/` (3 archivos) y `specs/<fase-1>/` (3 archivos).
- [ ] El código del modelo y el workflow, construidos desde la spec.
- [ ] El pipeline en **verde** con el lote 1.
- [ ] Evidencia de la alerta con el lote 2 (captura o enlace a la ejecución).

## El dato

**Entrenamiento** (`data/train/`): `comentario_id`, `calificacion`, `comentario`, `sentimiento` (positivo, negativo, neutral) y `tema` (comida, entrega, precio, app, otro).

**Golden set** (`data/eval/`): las mismas columnas, como `sentimiento_esperado` y `tema_esperado`. No se usa para entrenar: es el examen que todo modelo tiene que aprobar antes de publicarse.

**Lotes** (`data/source/`): `comentario_id`, `pedido_id`, `restaurante_id`, `cliente_id`, `calificacion` (1 a 5), `comentario`, `fecha`. No traen etiquetas. Traen a propósito problemas de calidad (comentarios vacíos o muy cortos, pedidos sin calificación, duplicados) y algunos comentarios que contradicen su calificación. El lote 2 trae además **cambios que el modelo no vio al entrenar**. No los corrijas a mano: que tu spec diga qué hacer con ellos.

## Preguntas frecuentes

**¿Por qué scikit-learn y no un LLM?** Porque se entrena en segundos, corre gratis en GitHub Actions y se puede explicar. El equipo de PideYa ya tomó esa decisión (ver [`negocio/input-negocio.md`](negocio/input-negocio.md)). Las 4 preguntas de operación serían las mismas con cualquier otro modelo.

**¿Cuánto cuesta?** Nada. GitHub Actions es gratis en repos públicos y el pipeline tarda pocos minutos.

**¿Qué pasa si el asistente escribe código antes de que apruebe la spec?** Detenlo y recuérdale la regla del prompt: primero preguntas, después spec, después código.

**¿Puedo editar la spec a mano?** Sí, y es buena práctica. La spec es tuya.

## Créditos

Taller del Módulo de Operaciones (DataOps / MLOps / FinOps), UTEC Posgrado. Continúa el taller [taller_sdd_dataops](https://github.com/RosaTorres44/taller_sdd_dataops).
