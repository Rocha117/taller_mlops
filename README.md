# Taller SDD para MLOps: especificar cómo se opera un modelo

Taller práctico de **Spec-Driven Development (SDD)** aplicado a MLOps. El ciclo de vida del modelo (entrenar, registrar, champion/challenger) ya lo vieron. Aquí trabajamos lo que viene **después**: cómo se opera un modelo que ya está en producción. Antes de pedirle código a un asistente de IA, escribimos **qué** tiene que cumplir el modelo en producción y **cómo sabremos que sigue bien**.

El caso es **PideYa**, una app de delivery que usa IA para ponerle sentimiento y tema a los comentarios de sus clientes.

```
Desplegar  →  Monitorear  →  Reajustar  →  Aprobar y revertir
```

> **Idea clave:** no te cases con ninguna herramienta. Eliges el modelo de una lista corta (de la plataforma de datos, open source o por API) y la spec de operación es la misma con cualquiera. Lo que se queda contigo es el método.

---

## ¿Qué vas a construir hoy?

1. **La constitución** del proyecto (`constitucion/`): la misión del modelo, el stack tecnológico y el roadmap de operación.
2. **Una feature spec** de la primera fase del roadmap: requerimientos, plan y validación.

No vas a entrenar un modelo ni a escribir el pipeline en clase. **El código sale de la spec**, no al revés.

## Las cuatro preguntas que tu spec tiene que responder

Son las mismas de la lámina "Operar un modelo: 4 preguntas":

| Pregunta | Pista para tu spec |
|---|---|
| **Desplegar** · ¿Cómo sale a producción? | ¿Qué examen tiene que aprobar una versión antes de salir? Mira `data/eval/` |
| **Monitorear** · ¿Cómo sé que sigue bien? | ¿Qué cambió entre el lote 1 y el lote 2? ¿Qué número te lo hubiera avisado? |
| **Reajustar** · ¿Cuándo se actualiza? | ¿Qué señal dispara un cambio? ¿Qué se puede cambiar en un modelo que no entrenas tú? |
| **Aprobar y revertir** · ¿Quién decide y cómo vuelvo? | ¿Quién firma el cambio? ¿Qué necesitas guardar para volver atrás en minutos? |

## Las dos partes de SDD

| Parte | Pregunta que responde | Archivo |
|---|---|---|
| **Constitución** · Misión | ¿Para qué existe este modelo? ¿Para quién? ¿Qué KPI mueve? | `constitucion/mision.md` |
| **Constitución** · Stack tecnológico | ¿Cómo encaja con la tecnología? Gobierno de IA, costo y restricciones | `constitucion/stack-tecnologico.md` |
| **Constitución** · Roadmap | ¿Qué fases de operación están planificadas y en qué orden? | `constitucion/roadmap.md` |
| **Feature Spec** · Scope + Requirements | ¿Qué construye esta fase? ¿Qué restricciones importan? | `specs/AAAA-MM-DD-fase/requerimientos.md` |
| **Feature Spec** · Plan | ¿En qué tareas se divide? | `specs/AAAA-MM-DD-fase/plan.md` |
| **Feature Spec** · Validation | ¿Cómo sabemos que ya está listo? | `specs/AAAA-MM-DD-fase/validacion.md` |

---

## Requisitos previos

- Una cuenta de **GitHub**.
- **Cualquier asistente de IA** que pueda leer y escribir archivos en tu repo, por ejemplo Claude Code, GitHub Copilot, Cursor o Gemini CLI.
- Git instalado en tu computadora (o usa GitHub Codespaces).

## Estructura del repo

```
.
├── README.md                        ← este archivo
├── prompts.md                       ← guía para armar tus prompts (preguntas + esqueleto)
├── constitucion/                    ← vacío al inicio; base de conocimiento del proyecto
├── negocio/
│   └── input-negocio.md             ← lo que pidieron los stakeholders
├── data/
│   ├── source/
│   │   ├── comentarios_lote_01.csv  ← lote de septiembre: la "foto normal"
│   │   └── comentarios_lote_02.csv  ← lote de octubre: llegó después
│   └── eval/
│       └── golden_set.csv           ← 35 comentarios etiquetados por personas
└── specs/                           ← vacío al inicio; una carpeta por cada feature
```

---

## Paso a paso

### 1. Crea tu copia del repo

Haz **fork** de este repositorio y clónalo:

```bash
git clone https://github.com/<tu-usuario>/<nombre-del-repo>.git
cd <nombre-del-repo>
```

✅ Checkpoint: ves `README.md`, `prompts.md`, `constitucion/`, `negocio/`, `data/` y `specs/`.

### 2. Mira el dato antes de escribir nada

Abre los dos lotes y el golden set (en tu editor o en una hoja de cálculo). Compara el lote 1 con el lote 2: ¿de qué se queja la gente en octubre que no aparecía en septiembre? ¿En qué idioma escriben? ¿Cuántos comentarios tienen 5 estrellas y texto negativo?

✅ Checkpoint: tienes anotadas al menos dos diferencias entre los lotes. Las vas a usar en la constitución.

### 3. Escribe la constitución (Parte 1)

1. Lee [`negocio/input-negocio.md`](negocio/input-negocio.md): es lo que pidieron Calidad de Restaurantes, Producto, Ingeniería, Gobierno y FinOps. Completa en clase la sección "Lo que completamos en clase".
2. Abre tu asistente de IA dentro de la carpeta del repo.
3. Con tu grupo, responde las preguntas guía del **Prompt 1 · Constitución** de [`prompts.md`](prompts.md), completa los espacios `[ ... ]` del esqueleto y pégalo.
4. El asistente **te hará preguntas antes de escribir**. Respóndelas pensando como el dueño del modelo desde el punto de vista del negocio.
5. Revisa los tres archivos que crea en `constitucion/`. **Tú apruebas la spec, no el asistente.**

✅ Checkpoint: existen `constitucion/mision.md`, `constitucion/stack-tecnologico.md` y `constitucion/roadmap.md`, y el stack responde las 4 preguntas de operación.

```bash
git add constitucion/
git commit -m "docs: constitución del modelo de comentarios"
git push
```

### 4. Escribe la feature spec de la fase 1 (Parte 2)

1. Con tu grupo, responde las preguntas guía del **Prompt 2 · Feature Spec** de [`prompts.md`](prompts.md), completa el esqueleto y pégalo.
2. El asistente toma la **fase 1** del roadmap, crea una rama y te pregunta por el detalle.
3. Revisa `requerimientos.md`, `plan.md` y `validacion.md`. Pregúntate: *si mañana el lote 2 llega a producción, ¿esta spec me avisa?*

✅ Checkpoint: existe `specs/AAAA-MM-DD-<fase>/` con los tres archivos, en su propia rama, con un Pull Request abierto hacia `main` para que tu compañero/a revise la spec.

---

## El dato

**Lotes** (`data/source/`): `comentario_id`, `pedido_id`, `restaurante_id`, `cliente_id`, `calificacion` (1 a 5), `comentario`, `fecha`. Traen a propósito problemas de calidad (comentarios vacíos o muy cortos, pedidos sin calificación, duplicados) y algunos comentarios que contradicen su calificación. El lote 2 trae además **cambios que el modelo no ha visto**. No los corrijas a mano: que tu spec diga qué hacer con ellos.

**Golden set** (`data/eval/golden_set.csv`): `comentario_id`, `calificacion`, `comentario`, `sentimiento_esperado` (positivo, negativo, neutral) y `tema_esperado` (comida, entrega, precio, app, otro). Es el "examen" que toda versión del modelo tiene que aprobar antes de salir a producción.

## Preguntas frecuentes

**¿Qué modelo uso?** Uno de la lista "Modelos que el equipo ya revisó" de [`negocio/input-negocio.md`](negocio/input-negocio.md); no lo inventes. Elegirlo y justificarlo es parte del alcance de tu constitución. Si cambias de modelo, cambia `constitucion/stack-tecnologico.md`, pero las 4 preguntas de operación siguen siendo las mismas.

**¿Por qué "reajustar" y no "reentrenar"?** Con un LLM normalmente no reentrenas: cambias el prompt, la lista de temas o la versión del modelo. Para operarlo es lo mismo: es una nueva versión que tiene que pasar el golden set y ser aprobada.

**¿Qué pasa si el asistente escribe código antes de que apruebe la spec?** Detenlo y recuérdale la regla del prompt: primero preguntas, después spec, después código.

## Créditos

Taller del Módulo de Operaciones (DataOps / MLOps / FinOps), UTEC Posgrado. Continúa el taller [taller_sdd_dataops](https://github.com/RosaTorres44/taller_sdd_dataops).
