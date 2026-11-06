"""Pruebas de API para HU-10: solicitar y consultar vacaciones."""

import uuid

import httpx

ID_EMPLEADO_INEXISTENTE = 999_999_999


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
    """Crea un empleado activo por la API para preparar los datos de una prueba."""
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
    """Envía una solicitud de vacaciones por la API."""
    return httpx.post(
        f"{url_api}/api/empleados/{id_empleado}/vacaciones",
        json={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin},
    )


def test_cp_01_solicitud_valida_descuenta_dias_habiles(url_api):
    """CP-01: Registrar una solicitud válida descuenta los días hábiles y calcula el saldo restante."""
    correo = correo_unico("laura.gomez")
    creado = registrar_empleado(url_api, "Laura Gómez", correo, "2020-01-01")

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-07-06", "2026-07-10")

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 5
    assert cuerpo["dias_restantes"] == 7


def test_cp_03_fin_de_semana_y_festivos_no_se_descuentan(url_api):
    """CP-03: Los sábados, domingos y festivos dentro del periodo no se descuentan."""
    correo = correo_unico("marco.diaz")
    creado = registrar_empleado(url_api, "Marco Díaz", correo, "2020-01-01")

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-12-21", "2026-12-31")

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 8
    assert cuerpo["dias_restantes"] == 4


def test_cp_04_periodo_solo_fin_de_semana_se_rechaza(url_api):
    """CP-04: Un periodo compuesto solo por fin de semana no tiene días hábiles y se rechaza."""
    correo = correo_unico("sofia.ruiz")
    creado = registrar_empleado(url_api, "Sofía Ruiz", correo, "2020-01-01")

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-07-11", "2026-07-12")

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "El periodo no incluye días hábiles"


def test_cp_06_usar_exactamente_los_dias_restantes_se_acepta(url_api):
    """CP-06: Usar exactamente los días que quedan en el año se acepta."""
    correo = correo_unico("carlos.vega")
    creado = registrar_empleado(url_api, "Carlos Vega", correo, "2020-01-01")
    previa = solicitar_vacaciones(url_api, creado["id"], "2026-01-05", "2026-01-09")
    assert previa.status_code == 201
    assert previa.json()["dias_habiles"] == 5

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-07-13", "2026-07-21")

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 7
    assert cuerpo["dias_restantes"] == 0


def test_cp_07_pasarse_un_dia_del_saldo_se_rechaza(url_api):
    """CP-07: Pasarse por un día del saldo disponible se rechaza."""
    correo = correo_unico("elena.rios")
    creado = registrar_empleado(url_api, "Elena Ríos", correo, "2020-01-01")
    previa = solicitar_vacaciones(url_api, creado["id"], "2026-01-05", "2026-01-08")
    assert previa.status_code == 201
    assert previa.json()["dias_habiles"] == 4

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-08-10", "2026-08-20")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "La solicitud excede los días disponibles: quedan 8 días hábiles"
    )


def test_cp_09_tope_anual_agotado_rechaza_cualquier_solicitud(url_api):
    """CP-09: Con el tope anual agotado se rechaza cualquier solicitud nueva."""
    correo = correo_unico("diego.pena")
    creado = registrar_empleado(url_api, "Diego Peña", correo, "2020-01-01")
    previa = solicitar_vacaciones(url_api, creado["id"], "2026-01-05", "2026-01-20")
    assert previa.status_code == 201
    assert previa.json()["dias_habiles"] == 12

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-03-02", "2026-03-02")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "La solicitud excede los días disponibles: quedan 0 días hábiles"
    )


def test_cp_10_exactamente_un_anio_de_antiguedad_se_acepta(url_api):
    """CP-10: Cumplir exactamente un año de antigüedad el día de inicio se acepta."""
    correo = correo_unico("natalia.soto")
    creado = registrar_empleado(url_api, "Natalia Soto", correo, "2025-12-21")

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-12-21", "2026-12-21")

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 1
    assert cuerpo["dias_restantes"] == 11


def test_cp_11_menos_de_un_anio_de_antiguedad_se_rechaza(url_api):
    """CP-11: Menos de un año de antigüedad se rechaza."""
    correo = correo_unico("ivan.molina")
    creado = registrar_empleado(url_api, "Iván Molina", correo, "2025-12-21")

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-12-18", "2026-12-18")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "Se requiere al menos un año de antigüedad a la fecha de inicio"
    )


def test_cp_13_fecha_fin_anterior_a_inicio_se_rechaza(url_api):
    """CP-13: Una fecha de fin anterior a la de inicio se rechaza."""
    correo = correo_unico("paula.jimenez")
    creado = registrar_empleado(url_api, "Paula Jiménez", correo, "2020-01-01")

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-07-10", "2026-07-05")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "La fecha de fin no puede ser anterior a la fecha de inicio"
    )


def test_cp_15_periodo_cruza_de_anio_se_rechaza(url_api):
    """CP-15: Un periodo que cruza de un año a otro se rechaza."""
    correo = correo_unico("hugo.navarro")
    creado = registrar_empleado(url_api, "Hugo Navarro", correo, "2020-01-01")

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-12-28", "2027-01-08")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "Las vacaciones deben estar dentro de un mismo año calendario"
    )


def test_cp_17_anio_fuera_de_rango_soportado_se_rechaza(url_api):
    """CP-17: Un año fuera del rango soportado se rechaza."""
    correo = correo_unico("rosa.campos")
    creado = registrar_empleado(url_api, "Rosa Campos", correo, "2020-01-01")

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2028-01-10", "2028-01-14")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"] == "Solo se pueden solicitar vacaciones en 2026 y 2027"
    )


def test_cp_19_empleado_inexistente_se_rechaza(url_api):
    """CP-19: Un empleado que no existe se rechaza."""
    respuesta = solicitar_vacaciones(
        url_api, ID_EMPLEADO_INEXISTENTE, "2026-07-06", "2026-07-10"
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Empleado no encontrado"


def test_cp_20_empleado_de_baja_no_puede_solicitar(url_api):
    """CP-20: Un empleado dado de baja no puede solicitar vacaciones."""
    correo = correo_unico("tomas.leon")
    creado = registrar_empleado(url_api, "Tomás León", correo, "2020-01-01")
    dar_de_baja(url_api, creado["id"])

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-07-06", "2026-07-10")

    assert respuesta.status_code == 409
    assert (
        respuesta.json()["detail"]
        == "No se pueden solicitar vacaciones para un empleado dado de baja"
    )


def test_cp_22_consultar_saldo_del_anio(url_api):
    """CP-22: Consultar el saldo del año refleja los días usados y disponibles."""
    correo = correo_unico("beatriz.ortiz")
    creado = registrar_empleado(url_api, "Beatriz Ortiz", correo, "2020-01-01")
    previa = solicitar_vacaciones(url_api, creado["id"], "2026-07-06", "2026-07-10")
    assert previa.status_code == 201

    respuesta = httpx.get(
        f"{url_api}/api/empleados/{creado['id']}/vacaciones", params={"anio": 2026}
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["dias_usados"] == 5
    assert cuerpo["dias_disponibles"] == 7
    assert len(cuerpo["solicitudes"]) == 1
