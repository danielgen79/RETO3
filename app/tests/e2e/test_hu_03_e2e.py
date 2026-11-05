"""Pruebas end-to-end para HU-03: editar y dar de baja a un empleado."""

import uuid

import httpx
import pytest

RAZON_DEPARTAMENTO_SELECT = (
    "El campo empleado-departamento es un <select> limitado a los departamentos del "
    "catálogo; no admite escribir ni seleccionar un valor que no esté en la lista, así "
    "que este caso no se puede reproducir desde la interfaz. Reportar al equipo de desarrollo."
)


def correo_unico(local: str, dominio: str = "empresa.com") -> str:
    """Genera un correo único para que cada prueba sea repetible sin choques."""
    return f"{local}.{uuid.uuid4().hex[:8]}@{dominio}"


def registrar_empleado(
    url_api,
    nombre,
    correo,
    puesto="Analista Jr",
    departamento="Ventas",
    fecha_ingreso="2022-05-10",
):
    """Crea un empleado directamente por la API para preparar el directorio."""
    datos = {
        "nombre": nombre,
        "correo": correo,
        "puesto": puesto,
        "departamento": departamento,
        "fecha_ingreso": fecha_ingreso,
    }
    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)
    assert respuesta.status_code == 201
    return respuesta.json()


def dar_de_baja(url_api, id_empleado, fecha_baja="2024-03-01"):
    """Da de baja a un empleado por la API para preparar una precondición."""
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{id_empleado}/baja", json={"fecha_baja": fecha_baja}
    )
    assert respuesta.status_code == 200
    return respuesta.json()


def id_de(page, numero_empleado):
    """Obtiene el id interno (usado en los data-testid) del empleado dado su número."""
    celda = page.locator('[data-testid^="numero-empleado-"]', has_text=numero_empleado)
    celda.wait_for()
    return celda.get_attribute("data-testid").replace("numero-empleado-", "")


def fila_de(page, numero_empleado):
    """Ubica la fila del directorio correspondiente a un número de empleado."""
    return page.get_by_test_id(f"fila-empleado-{id_de(page, numero_empleado)}")


def test_cp_02_editar_puesto_y_departamento(page, url_web, url_api):
    """CP-02: Editar puesto y departamento de un empleado activo."""
    correo = correo_unico("Laura.Gomez")
    creado = registrar_empleado(url_api, "Laura Gómez", correo)

    page.goto(url_web)
    id_empleado = id_de(page, creado["numero_empleado"])
    page.get_by_test_id(f"editar-empleado-{id_empleado}").click()
    page.get_by_test_id("empleado-puesto").fill("Analista Senior")
    page.get_by_test_id("empleado-departamento").select_option("Tecnología")
    page.get_by_test_id("empleado-guardar").click()

    page.get_by_test_id("mensaje-exito").wait_for()
    fila = page.get_by_test_id(f"fila-empleado-{id_empleado}")
    fila.filter(has_text="Analista Senior").filter(has_text="Tecnología").wait_for()


def test_cp_04_dar_de_baja_empleado_activo(page, url_web, url_api):
    """CP-04: Dar de baja a un empleado activo."""
    correo = correo_unico("Laura.Gomez")
    creado = registrar_empleado(url_api, "Laura Gómez", correo, fecha_ingreso="2022-05-10")

    page.goto(url_web)
    id_empleado = id_de(page, creado["numero_empleado"])
    page.get_by_test_id(f"baja-empleado-{id_empleado}").click()
    page.get_by_test_id("empleado-fecha-baja").fill("2024-03-01")
    page.get_by_test_id("confirmar-baja").click()

    page.get_by_test_id("mensaje-exito").wait_for()
    estado = page.get_by_test_id(f"estado-empleado-{id_empleado}")
    estado.filter(has_text="Baja").wait_for()
    fila_de(page, creado["numero_empleado"]).wait_for()


def test_cp_06_no_editar_empleado_de_baja(page, url_web, url_api):
    """CP-06: No se puede editar a un empleado dado de baja."""
    correo = correo_unico("Marco.Diaz")
    creado = registrar_empleado(url_api, "Marco Díaz", correo, fecha_ingreso="2022-05-10")
    dar_de_baja(url_api, creado["id"])

    page.goto(url_web)
    id_empleado = id_de(page, creado["numero_empleado"])
    page.get_by_test_id(f"editar-empleado-{id_empleado}").click()
    page.get_by_test_id("empleado-puesto").fill("Analista Senior")
    page.get_by_test_id("empleado-guardar").click()

    mensaje = page.get_by_test_id("mensaje-error")
    mensaje.wait_for()
    assert mensaje.text_content() == "No se puede editar a un empleado dado de baja"


def test_cp_08_puesto_demasiado_corto(page, url_web, url_api):
    """CP-08: Error al editar con un puesto demasiado corto."""
    correo = correo_unico("Laura.Gomez")
    creado = registrar_empleado(url_api, "Laura Gómez", correo)

    page.goto(url_web)
    id_empleado = id_de(page, creado["numero_empleado"])
    page.get_by_test_id(f"editar-empleado-{id_empleado}").click()
    page.get_by_test_id("empleado-puesto").fill("A")
    page.get_by_test_id("empleado-guardar").click()

    mensaje = page.get_by_test_id("mensaje-error")
    mensaje.wait_for()
    assert mensaje.text_content() == "El puesto debe tener entre 2 y 60 caracteres"


@pytest.mark.skip(reason=RAZON_DEPARTAMENTO_SELECT)
def test_cp_10_departamento_no_existe(page, url_web, url_api):
    """CP-10: Error al editar con un departamento que no existe en el catálogo."""


def test_cp_12_fecha_baja_anterior_a_ingreso(page, url_web, url_api):
    """CP-12: Error al dar de baja con una fecha de baja anterior a la fecha de ingreso."""
    correo = correo_unico("Laura.Gomez")
    creado = registrar_empleado(url_api, "Laura Gómez", correo, fecha_ingreso="2022-05-10")

    page.goto(url_web)
    id_empleado = id_de(page, creado["numero_empleado"])
    page.get_by_test_id(f"baja-empleado-{id_empleado}").click()
    page.get_by_test_id("empleado-fecha-baja").fill("2022-01-01")
    page.get_by_test_id("confirmar-baja").click()

    mensaje = page.get_by_test_id("mensaje-error")
    mensaje.wait_for()
    assert (
        mensaje.text_content()
        == "La fecha de baja no puede ser anterior a la fecha de ingreso"
    )
