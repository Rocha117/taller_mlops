# PideYa · Comentarios con IA · Input del negocio

> Esto es lo que nos dijeron las personas interesadas (stakeholders) en reuniones con el equipo de datos. Es **la entrada** de la constitución: el asistente de IA lo lee antes de escribir la constitución (`constitucion/`). No es una spec: tiene vacíos y algunas tensiones entre áreas, y la spec tiene que resolverlas.

## El contexto

PideYa es una app de delivery de comida. Al terminar cada pedido, el cliente pone una **calificación** (1 a 5) y puede dejar un **comentario**. Hace un mes el equipo de datos probó un modelo de IA que le pone a cada comentario un **sentimiento** (positivo, negativo, neutral) y un **tema** (comida, entrega, precio, app, otro). Funcionó en la demo. Ahora el negocio quiere usarlo **todas las semanas**, y ahí empiezan las preguntas de operación: ¿quién se entera si el modelo empieza a equivocarse?, ¿qué pasa si cambiamos el prompt o el modelo?, ¿cómo volvemos atrás?

## Lo que nos pidieron

- **Valeria, de Calidad de Restaurantes**, revisa cada lunes los comentarios sospechosos: **5 estrellas con texto negativo** o 1 estrella con texto positivo. Pueden ser calificaciones falsas o clientes que se equivocaron de estrella, y afectan el ranking de los restaurantes. Su equipo es pequeño: si el modelo le marca muchas falsas alarmas, pierden la mañana. Quiere saber **por qué** se marcó cada comentario.
- **Martín, de Producto**, mira el tema de los comentarios para decidir qué mejorar. Últimamente ve que crece mucho el tema **"otro"** y sospecha que la gente está hablando de algo que el modelo no conoce. Quiere poder **agregar temas nuevos**, pero sin romper la comparación con los meses anteriores.
- **Lucía, de Ingeniería de Datos y ML**, quiere que el prompt, la lista de temas y la versión del modelo vivan **en Git**, no escritos a mano en un notebook. Cualquier cambio entra por Pull Request y, antes del merge, se **evalúa contra comentarios etiquetados por personas** (`data/eval/golden_set.csv`). El modelo **no se inventa**: se elige de la lista de modelos que el equipo ya revisó (ver abajo), y la elección se justifica. No quiere quedar amarrada a un proveedor. Le gustaría que el ajuste fuera automático cuando el modelo empeora.
- **Patricia, de Gobierno de Datos y Seguridad**, recuerda que la salida de la IA se guarda como **dato productivo**: de cada fila quiere saber qué **versión del modelo y del prompt** la produjo y en qué ejecución. Los comentarios a veces traen nombres, teléfonos o direcciones. Ningún cambio de versión pasa a producción sin que **una persona lo apruebe**, y si la nueva versión sale mal, quiere **volver a la anterior** en minutos, no en días.
- **Jorge, de Plataforma / FinOps**, avisa que cada llamada al modelo **cuesta**. Pide procesar solo los comentarios **nuevos** de cada semana, con un tope por lote, y saber cuánto cuesta cada corrida.

## Modelos que el equipo ya revisó

Lucía dejó esta lista corta. Cada grupo elige **uno** para operar (y uno de respaldo) y explica por qué. Fíjense qué resuelve cada uno: algunos solo dan sentimiento y necesitan otro modelo para el tema.

| Opción | Tipo | Sentimiento | Tema | A tener en cuenta |
|---|---|---|---|---|
| **AI Functions de Databricks** (`ai_analyze_sentiment`, `ai_classify`) | Función SQL de la plataforma | Sí | Sí, con la lista de temas como parámetro | Es lo que usa el capstone. Consume la cuota del workspace. `ai_analyze_sentiment` también puede devolver `mixed`: decidan qué hacer con ese valor. |
| **`pysentimiento/robertuito-sentiment-analysis`** (Hugging Face) | Modelo open source entrenado en español | Sí (POS, NEG, NEU) | No: necesita otro modelo para el tema | Gratis y se puede correr local. Pensado para español; revisen cómo le va con el inglés del lote 2. |
| **`cardiffnlp/twitter-xlm-roberta-base-sentiment`** (Hugging Face) | Modelo open source multilingüe | Sí (positive, negative, neutral) | No | Maneja español e inglés. Entrenado con tuits: revisen el sarcasmo. |
| **`MoritzLaurer/mDeBERTa-v3-base-mnli-xnli`** (Hugging Face) | Clasificador zero-shot multilingüe | No | Sí, con la lista de temas como etiquetas | Complemento de las dos opciones anteriores para el tema. |
| **LLM por API** (por ejemplo Claude, GPT o Gemini) | Modelo general con prompt | Sí | Sí | El más flexible, pero el resultado depende del prompt y de la versión del modelo: ambos se versionan. Tiene costo por llamada. |

## Lo que sabemos del dato

- Fuente: un lote semanal en `data/source/` con las columnas `comentario_id`, `pedido_id`, `restaurante_id`, `cliente_id`, `calificacion`, `comentario`, `fecha`.
- `comentarios_lote_01.csv` es septiembre: la "foto normal" con la que se probó el modelo.
- `comentarios_lote_02.csv` es octubre: llegó después. Nadie lo revisó todavía.
- `data/eval/golden_set.csv` son 35 comentarios que dos personas etiquetaron a mano con su sentimiento y su tema esperados.
- Problemas conocidos: comentarios vacíos o demasiado cortos, pedidos sin calificación y registros duplicados.

## Lo que completamos en clase

- ¿Qué % de acuerdo con el golden set necesita una versión para pasar a producción?: ______
- ¿Qué cambio en un lote nos tiene que alertar (por ejemplo, el % de "otro" o la distribución de sentimiento)?: ______
- Cuando el modelo empeora, ¿se reajusta solo o lo aprueba una persona? ¿Quién?: ______
- ¿Cuántos comentarios como máximo procesamos por lote?: ______
- ¿Qué modelo de la lista operamos y cuál queda de respaldo? ¿Por qué?: ______
