# Misión · Modelo de comentarios de PideYa

## Para qué existe

Cada semana, PideYa recibe comentarios de clientes con una calificación de 1 a 5. El modelo le pone a cada comentario un **sentimiento** (positivo, negativo, neutral) y un **tema** (comida, entrega, precio, app, otro), para que dos equipos tomen decisiones:

| Quién | Qué decisión toma con el modelo |
|---|---|
| **Valeria · Calidad de Restaurantes** | Cada lunes revisa los **comentarios sospechosos** (5★ con texto negativo o 1★ con texto positivo) y decide si la calificación es falsa o un error del cliente, porque afecta el ranking del restaurante. |
| **Martín · Producto** | Mira la distribución de **temas** para decidir qué mejorar, y necesita enterarse cuando aparecen temas que el modelo no conoce. |

Además, la salida del modelo es **dato productivo**: Gobierno de Datos (Patricia) necesita saber qué versión la produjo, e Ingeniería (Lucía) necesita que todo se pueda repetir desde Git.

## Qué queda dentro

- **Operar** el modelo que eligió el equipo (scikit-learn: TF-IDF + regresión logística), no reemplazarlo.
- Entrenarlo, evaluarlo, publicarlo, puntuar los lotes semanales y monitorearlos en un pipeline automático (GitHub Actions).
- Marcar los comentarios sospechosos con su **motivo**, para que Valeria sepa por qué se marcó cada uno.
- Detectar la **deriva**: avisar cuando un lote se aleja de lo que el modelo conoce (otro idioma, temas nuevos, más dudas del modelo).
- Más adelante (fase 2): reentrenar, aprobar el modelo nuevo y volver al anterior.

## Qué queda fuera

- Buscar o inventar un modelo "mejor", o usar LLMs o APIs pagadas.
- Agregar temas nuevos durante la fase 1. Los temas que no conoce el modelo se **vigilan y reportan**, pero el catálogo se mantiene igual para no romper la comparación con los meses anteriores. Agregar un tema es una decisión de Producto que entra por reentrenamiento (fase 2).
- Corregir a mano los lotes. Las reglas de calidad del pipeline deciden qué hacer con cada problema.
- Sancionar automáticamente a un restaurante o a un cliente. El modelo **marca**; una persona decide.

## Cómo sabremos que funciona

| | KPI | Meta inicial |
|---|---|---|
| **De negocio** | **Precisión de los sospechosos**: % de comentarios marcados que el equipo de Valeria confirma como reales (calificación falsa o equivocada). Mide cuántas falsas alarmas le llegan. | ≥ 70% confirmados |
| **Del modelo** | **Acierto (accuracy) en el golden set** (`data/eval/golden_set.csv`), calculado en cada corrida. | Sentimiento ≥ 85% · Tema ≥ 80% |

Indicadores de apoyo que se reportan en cada lote: % de comentarios con baja confianza, % de palabras no vistas al entrenar, distribución de sentimiento y tema, cantidad de sospechosos.
