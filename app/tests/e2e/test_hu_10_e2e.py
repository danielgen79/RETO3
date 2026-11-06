"""Pruebas end-to-end para HU-10: solicitar y consultar vacaciones."""

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
    """Crea un empleado activo directamente por la API para preparar el directorio."""
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


def solicitar_vacaciones(url_api, id_empleado, fecha_inicio, fecha_fin):
    """Envía una solicitud de vacaciones por la API para preparar un saldo previo."""
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{id_empleado}/vacaciones",
        json={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin},
    )
    assert respuesta.status_code == 201
    return respuesta.json()


def id_de(page, numero_empleado):
    """Obtiene el id interno (usado en los data-testid) del empleado dado su número."""
    celda = page.locator('[data-testid^="numero-empleado-"]', has_text=numero_empleado)
    celda.wait_for()
    return celda.get_attribute("data-testid").replace("numero-empleado-", "")


def abrir_formulario_vacaciones(page, url_web, numero_empleado):
    """Navega al directorio y abre el formulario de vacaciones del empleado dado."""
    page.goto(url_web)
    id_empleado = id_de(page, numero_empleado)
    page.get_by_test_id(f"vacaciones-abrir-{id_empleado}").click()
    return id_empleado


def enviar_solicitud(page, fecha_inicio, fecha_fin):
    """Llena el formulario de vacaciones ya abierto y lo envía."""
    page.get_by_test_id("vacaciones-fecha-inicio").fill(fecha_inicio)
    page.get_by_test_id("vacaciones-fecha-fin").fill(fecha_fin)
    page.get_by_test_id("vacaciones-enviar").click()


def test_cp_02_solicitud_valida_descuenta_dias_habiles(page, url_web, url_api):
    """CP-02: Registrar una solicitud válida descuenta los días hábiles y calcula el saldo restante."""
    correo = correo_unico("laura.gomez")
    creado = registrar_empleado(url_api, "Laura Gómez", correo, "2020-01-01")

    abrir_formulario_vacaciones(page, url_web, creado["numero_empleado"])
    enviar_solicitud(page, "2026-07-06", "2026-07-10")

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    mensaje.wait_for()
    assert (
        mensaje.text_content()
        == "Solicitud registrada: 5 días hábiles. Te quedan 7 días hábiles en 2026."
    )


def test_cp_05_periodo_solo_fin_de_semana_se_rechaza(page, url_web, url_api):
    """CP-05: Un periodo compuesto solo por fin de semana no tiene días hábiles y se rechaza."""
    correo = correo_unico("sofia.ruiz")
    creado = registrar_empleado(url_api, "Sofía Ruiz", correo, "2020-01-01")

    abrir_formulario_vacaciones(page, url_web, creado["numero_empleado"])
    enviar_solicitud(page, "2026-07-11", "2026-07-12")

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    mensaje.wait_for()
    assert mensaje.text_content() == "El periodo no incluye días hábiles"


def test_cp_08_pasarse_un_dia_del_saldo_se_rechaza(page, url_web, url_api):
    """CP-08: Pasarse por un día del saldo disponible se rechaza."""
    correo = correo_unico("elena.rios")
    creado = registrar_empleado(url_api, "Elena Ríos", correo, "2020-01-01")
    solicitar_vacaciones(url_api, creado["id"], "2026-01-05", "2026-01-08")

    abrir_formulario_vacaciones(page, url_web, creado["numero_empleado"])
    enviar_solicitud(page, "2026-08-10", "2026-08-20")

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    mensaje.wait_for()
    assert (
        mensaje.text_content()
        == "La solicitud excede los días disponibles: quedan 8 días hábiles"
    )


def test_cp_12_menos_de_un_anio_de_antiguedad_se_rechaza(page, url_web, url_api):
    """CP-12: Menos de un año de antigüedad se rechaza."""
    correo = correo_unico("ivan.molina")
    creado = registrar_empleado(url_api, "Iván Molina", correo, "2025-12-21")

    abrir_formulario_vacaciones(page, url_web, creado["numero_empleado"])
    enviar_solicitud(page, "2026-12-18", "2026-12-18")

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    mensaje.wait_for()
    assert (
        mensaje.text_content()
        == "Se requiere al menos un año de antigüedad a la fecha de inicio"
    )


def test_cp_14_fecha_fin_anterior_a_inicio_se_rechaza(page, url_web, url_api):
    """CP-14: Una fecha de fin anterior a la de inicio se rechaza."""
    correo = correo_unico("paula.jimenez")
    creado = registrar_empleado(url_api, "Paula Jiménez", correo, "2020-01-01")

    abrir_formulario_vacaciones(page, url_web, creado["numero_empleado"])
    enviar_solicitud(page, "2026-07-10", "2026-07-05")

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    mensaje.wait_for()
    assert (
        mensaje.text_content()
        == "La fecha de fin no puede ser anterior a la fecha de inicio"
    )


def test_cp_16_periodo_cruza_de_anio_se_rechaza(page, url_web, url_api):
    """CP-16: Un periodo que cruza de un año a otro se rechaza."""
    correo = correo_unico("hugo.navarro")
    creado = registrar_empleado(url_api, "Hugo Navarro", correo, "2020-01-01")

    abrir_formulario_vacaciones(page, url_web, creado["numero_empleado"])
    enviar_solicitud(page, "2026-12-28", "2027-01-08")

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    mensaje.wait_for()
    assert (
        mensaje.text_content() == "Las vacaciones deben estar dentro de un mismo año calendario"
    )


def test_cp_18_anio_fuera_de_rango_soportado_se_rechaza(page, url_web, url_api):
    """CP-18: Un año fuera del rango soportado se rechaza."""
    correo = correo_unico("rosa.campos")
    creado = registrar_empleado(url_api, "Rosa Campos", correo, "2020-01-01")

    abrir_formulario_vacaciones(page, url_web, creado["numero_empleado"])
    enviar_solicitud(page, "2028-01-10", "2028-01-14")

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    mensaje.wait_for()
    assert mensaje.text_content() == "Solo se pueden solicitar vacaciones en 2026 y 2027"


def test_cp_21_no_hay_boton_de_vacaciones_para_empleado_de_baja(page, url_web, url_api):
    """CP-21: Un empleado dado de baja no puede solicitar vacaciones.

    El botón vacaciones-abrir-{empleado_id} solo se renderiza para empleados con
    estado "activo" (DirectorioEmpleados.jsx lo omite para un empleado dado de
    baja), así que el flujo descrito en el caso (abrir el formulario y enviarlo)
    no se puede reproducir desde la pantalla. La regla ya está cubierta a nivel
    API en CP-20; aquí se verifica que la interfaz oculta correctamente la
    opción de solicitar vacaciones una vez que el empleado está de baja.
    """
    correo = correo_unico("tomas.leon")
    creado = registrar_empleado(url_api, "Tomás León", correo, "2020-01-01")
    dar_de_baja(url_api, creado["id"])

    page.goto(url_web)
    id_empleado = id_de(page, creado["numero_empleado"])
    estado = page.get_by_test_id(f"estado-empleado-{id_empleado}")
    estado.filter(has_text="Baja").wait_for()
    assert page.get_by_test_id(f"vacaciones-abrir-{id_empleado}").count() == 0


def test_cp_23_consultar_saldo_del_anio(page, url_web, url_api):
    """CP-23: Consultar el saldo del año refleja los días usados y disponibles."""
    correo = correo_unico("beatriz.ortiz")
    creado = registrar_empleado(url_api, "Beatriz Ortiz", correo, "2020-01-01")
    solicitar_vacaciones(url_api, creado["id"], "2026-07-06", "2026-07-10")

    abrir_formulario_vacaciones(page, url_web, creado["numero_empleado"])

    disponibles = page.get_by_test_id("vacaciones-disponibles")
    disponibles.wait_for()
    assert disponibles.text_content() == "7"
