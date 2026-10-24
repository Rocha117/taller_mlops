import pytest

from enmascarar import enmascarar


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("Escríbanme a ana.perez@gmail.com por favor", "Escríbanme a [CORREO] por favor"),
        ("Mi número es 987654321", "Mi número es [TELEFONO]"),
        ("Llamen al +51 987 654 321 urgente", "Llamen al [TELEFONO] urgente"),
        ("Celular 987-654-321.", "Celular [TELEFONO]."),
        ("Mi DNI es 45678912", "Mi DNI es [DOCUMENTO]"),
        ("Hola, soy Carla Pérez y el pedido llegó frío", "Hola, soy [NOMBRE] y el pedido llegó frío"),
        ("Me llamo Luis y nadie me respondió", "Me llamo [NOMBRE] y nadie me respondió"),
        ("Entreguen en Av. Arequipa 1234, piso 2", "Entreguen en [DIRECCION], piso 2"),
        ("Vivo en Jr. Junín 455", "Vivo en [DIRECCION]"),
    ],
)
def test_enmascara_datos_personales(texto, esperado):
    assert enmascarar(texto) == esperado


@pytest.mark.parametrize(
    "texto",
    [
        "La app guarda mis direcciones y pedí en un minuto desde la app.",
        "Soy cliente frecuente y siempre llega bien.",
        "Llegó en 20 minutos y el repartidor fue muy amable. 10/10.",
        "Pedí reembolso y después de 10 días sigo esperando.",
        "",
    ],
)
def test_no_toca_texto_sin_datos_personales(texto):
    assert enmascarar(texto) == texto


def test_es_idempotente():
    texto = "soy Ana, mi cel 987654321 y correo a@b.pe"
    assert enmascarar(enmascarar(texto)) == enmascarar(texto)
