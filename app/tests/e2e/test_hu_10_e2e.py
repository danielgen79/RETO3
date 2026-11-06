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


def id_de(page, numero_empleado):
    """Obtiene el id interno (usado en los data-testid) del empleado dado su número."""
    celda = page.locator('[data-testid^="numero-empleado-"]', has_text=numero_empleado)
    celda.wait_for()
    return celda.get_attribute("data-testid").replace("numero-empleado-", "")


def test_cp_02_camino_feliz_festivo_no_se_descuenta(page, url_web, url_api):
    """CP-02: Camino feliz - se registra una solicitud válida y un festivo dentro del periodo no se descuenta."""
    correo = correo_unico("Carla.Reyes")
    creado = registrar_empleado(url_api, "Carla Reyes", correo, fecha_ingreso="2024-01-10")

    page.goto(url_web)
    id_empleado = id_de(page, creado["numero_empleado"])
    page.get_by_test_id(f"vacaciones-abrir-{id_empleado}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-12-21")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-12-31")
    page.get_by_test_id("vacaciones-enviar").click()

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    mensaje.wait_for()
    assert (
        mensaje.text_content()
        == "Solicitud registrada: 8 días hábiles. Te quedan 4 días hábiles en 2026."
    )
