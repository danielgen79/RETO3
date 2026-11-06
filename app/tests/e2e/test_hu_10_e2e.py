"""Pruebas end-to-end para HU-10: solicitar vacaciones."""

import uuid

import httpx


def correo_unico(local: str, dominio: str = "empresa.com") -> str:
    """Genera un correo único para que cada prueba sea repetible sin choques."""
    return f"{local}.{uuid.uuid4().hex[:8]}@{dominio}"


def registrar_empleado(
    url_api,
    nombre,
    correo,
    fecha_ingreso,
    puesto="Analista Jr",
    departamento="Ventas",
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


def id_de(page, numero_empleado):
    """Obtiene el id interno (usado en los data-testid) del empleado dado su número."""
    celda = page.locator('[data-testid^="numero-empleado-"]', has_text=numero_empleado)
    celda.wait_for()
    return celda.get_attribute("data-testid").replace("numero-empleado-", "")


def test_cp_02_camino_feliz_registra_y_descuenta(page, url_web, url_api):
    """CP-02: Camino feliz - una solicitud válida se registra y descuenta los días hábiles."""
    creado = registrar_empleado(
        url_api, "Laura Gómez", correo_unico("Laura.Gomez"), "2023-01-10"
    )

    page.goto(url_web)
    id_empleado = id_de(page, creado["numero_empleado"])
    page.get_by_test_id(f"vacaciones-abrir-{id_empleado}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-07-06")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-07-10")
    page.get_by_test_id("vacaciones-enviar").click()

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    mensaje.wait_for()
    assert (
        mensaje.text_content()
        == "Solicitud registrada: 5 días hábiles. Te quedan 7 días hábiles en 2026."
    )


def test_cp_06_antiguedad_insuficiente(page, url_web, url_api):
    """CP-06: Error Regla 1 - antigüedad insuficiente, le faltan días para cumplir el año."""
    creado = registrar_empleado(
        url_api, "Marco Díaz", correo_unico("Marco.Diaz"), "2025-12-21"
    )

    page.goto(url_web)
    id_empleado = id_de(page, creado["numero_empleado"])
    page.get_by_test_id(f"vacaciones-abrir-{id_empleado}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-12-18")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-12-20")
    page.get_by_test_id("vacaciones-enviar").click()

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    mensaje.wait_for()
    assert (
        mensaje.text_content()
        == "Se requiere al menos un año de antigüedad a la fecha de inicio"
    )
