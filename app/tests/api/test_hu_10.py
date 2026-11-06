"""Pruebas de API para HU-10: solicitar y consultar vacaciones."""

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
    """Crea un empleado por la API para preparar los datos de una prueba."""
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
    """Solicita vacaciones por la API."""
    return httpx.post(
        f"{url_api}/api/empleados/{id_empleado}/vacaciones",
        json={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin},
    )


def test_cp_01_camino_feliz_registra_y_descuenta(url_api):
    """CP-01: Camino feliz - una solicitud válida se registra y descuenta los días hábiles."""
    creado = registrar_empleado(
        url_api, "Laura Gómez", correo_unico("Laura.Gomez"), "2023-01-10"
    )

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-07-06", "2026-07-10")

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 5
    assert cuerpo["dias_restantes"] == 7


def test_cp_03_consultar_saldo_refleja_dias_usados(url_api):
    """CP-03: Camino feliz - consultar el saldo del año refleja los días usados."""
    creado = registrar_empleado(
        url_api, "Laura Gómez", correo_unico("Laura.Gomez"), "2023-01-10"
    )
    solicitud = solicitar_vacaciones(url_api, creado["id"], "2026-07-06", "2026-07-10")
    assert solicitud.status_code == 201

    respuesta = httpx.get(
        f"{url_api}/api/empleados/{creado['id']}/vacaciones", params={"anio": 2026}
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["dias_usados"] == 5
    assert cuerpo["dias_disponibles"] == 7
    assert len(cuerpo["solicitudes"]) == 1


def test_cp_04_antiguedad_justo_un_anio(url_api):
    """CP-04: Límite - el empleado puede solicitar justo el día en que cumple un año de antigüedad."""
    creado = registrar_empleado(
        url_api, "Marco Díaz", correo_unico("Marco.Diaz"), "2025-12-21"
    )

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-12-21", "2026-12-21")

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 1
    assert cuerpo["dias_restantes"] == 11


def test_cp_05_antiguedad_insuficiente(url_api):
    """CP-05: Error Regla 1 - antigüedad insuficiente, le faltan días para cumplir el año."""
    creado = registrar_empleado(
        url_api, "Marco Díaz", correo_unico("Marco.Diaz"), "2025-12-21"
    )

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-12-18", "2026-12-20")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "Se requiere al menos un año de antigüedad a la fecha de inicio"
    )


def test_cp_07_empleado_no_existe(url_api):
    """CP-07: Error - el empleado no existe."""
    respuesta = solicitar_vacaciones(url_api, 9999, "2026-07-06", "2026-07-10")

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Empleado no encontrado"


def test_cp_08_empleado_dado_de_baja(url_api):
    """CP-08: Error - el empleado está dado de baja."""
    creado = registrar_empleado(
        url_api, "Laura Gómez", correo_unico("Laura.Gomez"), "2023-01-10"
    )
    dar_de_baja(url_api, creado["id"])

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-07-06", "2026-07-10")

    assert respuesta.status_code == 409
    assert (
        respuesta.json()["detail"]
        == "No se pueden solicitar vacaciones para un empleado dado de baja"
    )


def test_cp_09_fecha_fin_anterior_a_inicio(url_api):
    """CP-09: Error - la fecha de fin es anterior a la fecha de inicio."""
    creado = registrar_empleado(
        url_api, "Laura Gómez", correo_unico("Laura.Gomez"), "2023-01-10"
    )

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-07-10", "2026-07-05")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "La fecha de fin no puede ser anterior a la fecha de inicio"
    )


def test_cp_10_periodo_cruza_de_anio(url_api):
    """CP-10: Error - el periodo cruza de un año calendario a otro."""
    creado = registrar_empleado(
        url_api, "Laura Gómez", correo_unico("Laura.Gomez"), "2023-01-10"
    )

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-12-28", "2027-01-08")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "Las vacaciones deben estar dentro de un mismo año calendario"
    )


def test_cp_11_anio_sin_tabla_de_festivos(url_api):
    """CP-11: Error - el año de la solicitud no está en la tabla de festivos."""
    creado = registrar_empleado(
        url_api, "Laura Gómez", correo_unico("Laura.Gomez"), "2023-01-10"
    )

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2025-07-06", "2025-07-10")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "Solo se pueden solicitar vacaciones en 2026 y 2027"
    )


def test_cp_12_fines_de_semana_y_festivos_no_se_descuentan(url_api):
    """CP-12: Los sábados, domingos y festivos dentro del periodo no se descuentan."""
    creado = registrar_empleado(
        url_api, "Laura Gómez", correo_unico("Laura.Gomez"), "2023-01-10"
    )

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-09-14", "2026-09-18")

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 4
    assert cuerpo["dias_restantes"] == 8


def test_cp_13_periodo_sin_dias_habiles(url_api):
    """CP-13: Error Regla 3 - un periodo sin ningún día hábil se rechaza."""
    creado = registrar_empleado(
        url_api, "Laura Gómez", correo_unico("Laura.Gomez"), "2023-01-10"
    )

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-07-11", "2026-07-12")

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "El periodo no incluye días hábiles"


def test_cp_14_usar_exactamente_lo_que_queda_del_tope(url_api):
    """CP-14: Límite - se puede usar exactamente lo que queda del tope anual."""
    creado = registrar_empleado(
        url_api, "Laura Gómez", correo_unico("Laura.Gomez"), "2023-01-10"
    )
    previa = solicitar_vacaciones(url_api, creado["id"], "2026-01-05", "2026-01-09")
    assert previa.status_code == 201
    assert previa.json()["dias_habiles"] == 5

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-07-13", "2026-07-21")

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 7
    assert cuerpo["dias_restantes"] == 0


def test_cp_15_rebasa_dias_disponibles(url_api):
    """CP-15: Error Regla 2 - la solicitud rebasa los días disponibles del año."""
    creado = registrar_empleado(
        url_api, "Laura Gómez", correo_unico("Laura.Gomez"), "2023-01-10"
    )
    previa = solicitar_vacaciones(url_api, creado["id"], "2026-02-02", "2026-02-05")
    assert previa.status_code == 201
    assert previa.json()["dias_habiles"] == 4

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-11-02", "2026-11-12")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "La solicitud excede los días disponibles: quedan 8 días hábiles"
    )


def test_cp_16_se_pasa_por_un_dia_habil_del_tope(url_api):
    """CP-16: Límite - la solicitud se pasa por un solo día hábil del tope disponible."""
    creado = registrar_empleado(
        url_api, "Laura Gómez", correo_unico("Laura.Gomez"), "2023-01-10"
    )
    previa_1 = solicitar_vacaciones(url_api, creado["id"], "2026-01-05", "2026-01-09")
    assert previa_1.status_code == 201
    assert previa_1.json()["dias_habiles"] == 5
    previa_2 = solicitar_vacaciones(url_api, creado["id"], "2026-01-12", "2026-01-19")
    assert previa_2.status_code == 201
    assert previa_2.json()["dias_habiles"] == 6

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-10-05", "2026-10-06")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "La solicitud excede los días disponibles: quedan 1 días hábiles"
    )


def test_cp_17_tope_anual_agotado(url_api):
    """CP-17: Límite - el tope anual ya está agotado y cualquier solicitud se rechaza."""
    creado = registrar_empleado(
        url_api, "Laura Gómez", correo_unico("Laura.Gomez"), "2023-01-10"
    )
    previa_1 = solicitar_vacaciones(url_api, creado["id"], "2026-01-05", "2026-01-09")
    assert previa_1.status_code == 201
    assert previa_1.json()["dias_habiles"] == 5
    previa_2 = solicitar_vacaciones(url_api, creado["id"], "2026-01-12", "2026-01-19")
    assert previa_2.status_code == 201
    assert previa_2.json()["dias_habiles"] == 6
    previa_3 = solicitar_vacaciones(url_api, creado["id"], "2026-01-20", "2026-01-20")
    assert previa_3.status_code == 201
    assert previa_3.json()["dias_habiles"] == 1

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-08-03", "2026-08-03")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "La solicitud excede los días disponibles: quedan 0 días hábiles"
    )
