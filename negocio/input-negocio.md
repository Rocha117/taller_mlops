# PideYa · Comentarios con IA · Input del negocio

> Esto es lo que nos dijeron las personas interesadas (stakeholders) en reuniones con el equipo de datos. Es **la entrada** de la constitución: el asistente de IA lo lee antes de escribir la constitución (`constitucion/`). No es una spec: tiene vacíos y algunas tensiones entre áreas, y la spec tiene que resolverlas.

## El contexto

PideYa es una app de delivery de comida. Al terminar cada pedido, el cliente pone una **calificación** (1 a 5) y puede dejar un **comentario**. Hace un mes alguien del equipo entrenó en su laptop un modelo que le pone a cada comentario un **sentimiento** (positivo, negativo, neutral) y un **tema** (comida, entrega, precio, app, otro). Funcionó en la demo, pero vive en un notebook que solo esa persona sabe correr. Ahora el negocio quiere usarlo **todas las semanas**, y ahí empiezan las preguntas de operación: ¿quién lo entrena?, ¿quién se entera si empieza a equivocarse?, ¿qué pasa si lo reentrenamos y sale peor?, ¿cómo volvemos atrás?

## Lo que nos pidieron

- **Valeria, de Calidad de Restaurantes**, revisa cada lunes los comentarios sospechosos: **5 estrellas con texto negativo** o 1 estrella con texto positivo. Pueden ser calificaciones falsas o clientes que se equivocaron de estrella, y afectan el ranking de los restaurantes. Su equipo es pequeño: si el modelo le marca muchas falsas alarmas, pierden la mañana. Quiere saber **por qué** se marcó cada comentario.
- **Martín, de Producto**, mira el tema de los comentarios para decidir qué mejorar. Sospecha que la gente empezó a hablar de cosas que el modelo no conoce y que esos comentarios terminan **mal clasificados sin que nadie lo note**. Quiere poder agregar temas nuevos, pero sin romper la comparación con los meses anteriores.
- **Lucía, de Ingeniería de Datos y ML**, quiere que el modelo se **entrene en el pipeline**, no en la laptop de nadie: código y parámetros en **Git**, y cada cambio por Pull Request. Antes del merge, el modelo se **evalúa contra comentarios etiquetados por personas** (`data/eval/golden_set.csv`) y, si no llega al umbral, no se publica. Cada modelo entrenado se guarda como artefacto con su versión. Le gustaría que el reentrenamiento fuera automático cuando el modelo empeora.
- **Patricia, de Gobierno de Datos y Seguridad**, recuerda que la salida del modelo se usa como **dato productivo**: de cada comentario puntuado quiere saber qué **versión del modelo** lo produjo y en qué ejecución. Los comentarios a veces traen nombres, teléfonos o direcciones. Ningún modelo nuevo reemplaza al actual sin que **una persona lo apruebe**, y si sale mal, quiere **volver al anterior** en minutos, no en días.
- **Jorge, de Plataforma / FinOps**, no quiere sorpresas de costo: nada de APIs pagadas ni servidores encendidos. El pipeline tiene que correr gratis y en pocos minutos, y solo procesar los comentarios **nuevos** de cada semana.

## El modelo elegido

Lucía ya revisó las opciones (funciones de IA de la plataforma de datos, modelos open source de Hugging Face y LLM por API) y eligió para empezar uno **clásico y simple**:

**scikit-learn: TF-IDF + regresión logística**, un modelo para sentimiento y otro para tema, entrenados con `data/train/comentarios_entrenamiento.csv`.

| Por qué este | Qué hay que vigilar |
|---|---|
| **Costo cero**: corre en GitHub Actions, sin API ni secrets | Solo conoce las palabras que vio al entrenar |
| **Se entrena en segundos**: se puede reentrenar en cada corrida | No entiende sarcasmo ni idiomas que no vio |
| **Explicable**: se puede ver qué palabras pesaron en cada predicción (lo que pide Valeria) | Si un tema no está en el entrenamiento, **no lo inventa**: lo asigna a otro tema sin avisar |
| **Liviano**: el artefacto pesa unos KB y se versiona fácil | Necesita comentarios etiquetados para mejorar |

El modelo no se cambia en este taller. Si mañana se reemplaza por otro, las preguntas de operación son las mismas.

## Lo que sabemos del dato

- `data/train/comentarios_entrenamiento.csv`: 300 comentarios de agosto, etiquetados por personas (`sentimiento`, `tema`). Con esto se entrena.
- `data/eval/golden_set.csv`: 40 comentarios etiquetados que **no** están en el entrenamiento. Es el examen del modelo.
- `data/source/comentarios_lote_01.csv`: septiembre, la "foto normal". Sin etiquetas: es lo que el modelo tiene que puntuar.
- `data/source/comentarios_lote_02.csv`: octubre. Llegó después y nadie lo revisó todavía.
- Columnas de los lotes: `comentario_id`, `pedido_id`, `restaurante_id`, `cliente_id`, `calificacion`, `comentario`, `fecha`.
- Problemas conocidos: comentarios vacíos o demasiado cortos, pedidos sin calificación y registros duplicados.

## Lo que completamos en clase

- ¿Qué % de acierto en el golden set necesita un modelo para publicarse? ¿Igual para sentimiento y para tema?: ______
- ¿Qué cambio en un lote nos tiene que alertar? (por ejemplo, la confianza promedio del modelo, el % de negativos o el % de sospechosos): ______
- ¿Una alerta detiene el pipeline o solo avisa?: ______
- ¿Cuándo se reentrena y quién aprueba que el modelo nuevo reemplace al actual?: ______
