"""Enmascarado de datos personales en el texto de los comentarios.

Se aplica antes de guardar cualquier archivo con comentarios, para que ningún
artefacto del pipeline contenga el texto original.
"""
from __future__ import annotations

import re

MAYUS = "A-ZÁÉÍÓÚÑ"
MINUS = "a-záéíóúñü"

# El orden importa: primero correo y teléfono, después documento (8 dígitos).
PATRONES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), "[CORREO]"),
    (re.compile(r"(?<![\d+])(?:\+?51[\s-]?)?9\d{2}[\s-]?\d{3}[\s-]?\d{3}(?!\d)"), "[TELEFONO]"),
    (re.compile(r"(?<!\d)\d{8}(?!\d)"), "[DOCUMENTO]"),
    (
        re.compile(
            rf"\b((?i:me llamo|mi nombre es|soy))\s+[{MAYUS}][{MINUS}]+(?:\s+[{MAYUS}][{MINUS}]+)*"
        ),
        r"\1 [NOMBRE]",
    ),
    (
        re.compile(r"\b(?:Av|Avenida|Jr|Jirón|Calle|Psje|Pasaje)\.?\s+[^,;]*?\d+"),
        "[DIRECCION]",
    ),
]


def enmascarar(texto: str) -> str:
    if not isinstance(texto, str) or not texto:
        return texto
    for patron, reemplazo in PATRONES:
        texto = patron.sub(reemplazo, texto)
    return texto
