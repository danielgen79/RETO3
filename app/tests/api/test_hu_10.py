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
    puesto="Analista Jr",
    departamento="Ventas",
    fecha_ingreso="2022-05-10",
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
    """Envía una solicitud de vacaciones por la API."""
    return httpx.post(
        f"{url_api}/api/empleados/{id_empleado}/vacaciones",
        json={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin},
    )


def consumir_dias_habiles(url_api, id_empleado, periodos):
    """Registra las solicitudes de vacaciones necesarias para dejar días ya usados."""
    for fecha_inicio, fecha_fin in periodos:
        respuesta = solicitar_vacaciones(url_api, id_empleado, fecha_inicio, fecha_fin)
        assert respuesta.status_code == 201


def test_cp_01_camino_feliz_festivo_no_se_descuenta(url_api):
    """CP-01: Camino feliz - se registra una solicitud válida y un festivo dentro del periodo no se descuenta."""
    correo = correo_unico("Ana.Perez")
    creado = registrar_empleado(url_api, "Ana Pérez", correo, fecha_ingreso="2024-01-10")

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-12-21", "2026-12-31")

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 8
    assert cuerpo["dias_restantes"] == 4


def test_cp_03_limite_usa_exactamente_los_dias_que_quedan(url_api):
    """CP-03: Límite - se puede usar exactamente los días hábiles que quedan en el año."""
    correo = correo_unico("Luis.Ramirez")
    creado = registrar_empleado(url_api, "Luis Ramírez", correo, fecha_ingreso="2024-01-10")
    consumir_dias_habiles(url_api, creado["id"], [("2026-01-05", "2026-01-09")])

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-07-13", "2026-07-21")

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 7
    assert cuerpo["dias_restantes"] == 0


def test_cp_04_limite_un_anio_exacto_de_antiguedad(url_api):
    """CP-04: Límite - el empleado puede solicitar vacaciones el mismo día en que cumple exactamente un año de antigüedad."""
    correo = correo_unico("Diana.Lopez")
    creado = registrar_empleado(url_api, "Diana López", correo, fecha_ingreso="2025-12-21")

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-12-21", "2026-12-21")

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 1
    assert cuerpo["dias_restantes"] == 11


def test_cp_05_empleado_no_existe(url_api):
    """CP-05: Error - el empleado no existe."""
    respuesta = solicitar_vacaciones(url_api, 999, "2026-07-06", "2026-07-10")

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Empleado no encontrado"


def test_cp_06_empleado_dado_de_baja(url_api):
    """CP-06: Error - el empleado está dado de baja."""
    correo = correo_unico("Mario.Torres")
    creado = registrar_empleado(url_api, "Mario Torres", correo, fecha_ingreso="2024-01-10")
    dar_de_baja(url_api, creado["id"])

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-07-06", "2026-07-10")

    assert respuesta.status_code == 409
    assert (
        respuesta.json()["detail"]
        == "No se pueden solicitar vacaciones para un empleado dado de baja"
    )


def test_cp_07_fecha_fin_anterior_a_fecha_inicio(url_api):
    """CP-07: Error - la fecha de fin es anterior a la fecha de inicio."""
    correo = correo_unico("Sofia.Castro")
    creado = registrar_empleado(url_api, "Sofía Castro", correo, fecha_ingreso="2024-01-10")

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-07-10", "2026-07-05")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "La fecha de fin no puede ser anterior a la fecha de inicio"
    )


def test_cp_08_periodo_cruza_de_un_anio_a_otro(url_api):
    """CP-08: Error - el periodo cruza de un año a otro."""
    correo = correo_unico("Jorge.Mendez")
    creado = registrar_empleado(url_api, "Jorge Méndez", correo, fecha_ingreso="2024-01-10")

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-12-28", "2027-01-08")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "Las vacaciones deben estar dentro de un mismo año calendario"
    )


def test_cp_09_anio_no_esta_en_la_tabla_de_festivos(url_api):
    """CP-09: Error - el año solicitado no está en la tabla de festivos."""
    correo = correo_unico("Elena.Vargas")
    creado = registrar_empleado(url_api, "Elena Vargas", correo, fecha_ingreso="2024-01-10")

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2028-01-10", "2028-01-14")

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "Solo se pueden solicitar vacaciones en 2026 y 2027"


def test_cp_10_antiguedad_insuficiente_a_la_fecha_de_inicio(url_api):
    """CP-10: Error - antigüedad insuficiente a la fecha de inicio."""
    correo = correo_unico("Hugo.Navarro")
    creado = registrar_empleado(url_api, "Hugo Navarro", correo, fecha_ingreso="2025-12-21")

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-12-18", "2026-12-18")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "Se requiere al menos un año de antigüedad a la fecha de inicio"
    )


def test_cp_11_periodo_no_incluye_ningun_dia_habil(url_api):
    """CP-11: Error - el periodo no incluye ningún día hábil."""
    correo = correo_unico("Patricia.Rojas")
    creado = registrar_empleado(url_api, "Patricia Rojas", correo, fecha_ingreso="2024-01-10")

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-07-11", "2026-07-12")

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "El periodo no incluye días hábiles"


def test_cp_12_rebasa_los_dias_disponibles_por_un_dia(url_api):
    """CP-12: Error - la solicitud rebasa los días disponibles por un día."""
    correo = correo_unico("Ricardo.Flores")
    creado = registrar_empleado(url_api, "Ricardo Flores", correo, fecha_ingreso="2024-01-10")
    consumir_dias_habiles(url_api, creado["id"], [("2026-01-05", "2026-01-08")])

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-08-03", "2026-08-13")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "La solicitud excede los días disponibles: quedan 8 días hábiles"
    )


def test_cp_13_tope_anual_ya_agotado(url_api):
    """CP-13: Error - el tope anual ya está agotado."""
    correo = correo_unico("Veronica.Santos")
    creado = registrar_empleado(url_api, "Verónica Santos", correo, fecha_ingreso="2024-01-10")
    consumir_dias_habiles(
        url_api,
        creado["id"],
        [
            ("2026-01-05", "2026-01-09"),
            ("2026-01-12", "2026-01-16"),
            ("2026-01-19", "2026-01-20"),
        ],
    )

    respuesta = solicitar_vacaciones(url_api, creado["id"], "2026-09-14", "2026-09-18")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "La solicitud excede los días disponibles: quedan 0 días hábiles"
    )
