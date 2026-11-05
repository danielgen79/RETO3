"""Pruebas de API para HU-03: editar y dar de baja a un empleado."""

import uuid

import httpx

MENSAJE_DEPARTAMENTO_INVALIDO = (
    "El departamento debe ser uno de: "
    "Tecnología, Ventas, Finanzas, Recursos Humanos, Operaciones"
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


def test_cp_01_editar_puesto_y_departamento(url_api):
    """CP-01: Editar puesto y departamento de un empleado activo."""
    correo = correo_unico("Laura.Gomez")
    creado = registrar_empleado(url_api, "Laura Gómez", correo)

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{creado['id']}",
        json={"puesto": "Analista Senior", "departamento": "Tecnología"},
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["numero_empleado"] == creado["numero_empleado"]
    assert cuerpo["correo"] == correo.lower()
    assert cuerpo["puesto"] == "Analista Senior"
    assert cuerpo["departamento"] == "Tecnología"


def test_cp_03_dar_de_baja_empleado_activo(url_api):
    """CP-03: Dar de baja a un empleado activo."""
    correo = correo_unico("Laura.Gomez")
    creado = registrar_empleado(url_api, "Laura Gómez", correo, fecha_ingreso="2022-05-10")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{creado['id']}/baja",
        json={"fecha_baja": "2024-03-01"},
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "baja"
    assert cuerpo["fecha_baja"] == "2024-03-01"

    listado = httpx.get(f"{url_api}/api/empleados")
    assert any(
        e["numero_empleado"] == creado["numero_empleado"] for e in listado.json()
    )


def test_cp_05_no_editar_empleado_de_baja(url_api):
    """CP-05: No se puede editar a un empleado dado de baja."""
    correo = correo_unico("Marco.Diaz")
    creado = registrar_empleado(url_api, "Marco Díaz", correo, fecha_ingreso="2022-05-10")
    dar_de_baja(url_api, creado["id"])

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{creado['id']}", json={"puesto": "Analista Senior"}
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "No se puede editar a un empleado dado de baja"


def test_cp_07_puesto_demasiado_corto(url_api):
    """CP-07: Error al editar con un puesto demasiado corto."""
    correo = correo_unico("Laura.Gomez")
    creado = registrar_empleado(url_api, "Laura Gómez", correo)

    respuesta = httpx.put(f"{url_api}/api/empleados/{creado['id']}", json={"puesto": "A"})

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == "El puesto debe tener entre 2 y 60 caracteres"


def test_cp_09_departamento_no_existe(url_api):
    """CP-09: Error al editar con un departamento que no existe en el catálogo."""
    correo = correo_unico("Laura.Gomez")
    creado = registrar_empleado(url_api, "Laura Gómez", correo)

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{creado['id']}", json={"departamento": "Marketing"}
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == MENSAJE_DEPARTAMENTO_INVALIDO


def test_cp_11_fecha_baja_anterior_a_ingreso(url_api):
    """CP-11: Error al dar de baja con una fecha de baja anterior a la fecha de ingreso."""
    correo = correo_unico("Laura.Gomez")
    creado = registrar_empleado(url_api, "Laura Gómez", correo, fecha_ingreso="2022-05-10")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{creado['id']}/baja",
        json={"fecha_baja": "2022-01-01"},
    )

    assert respuesta.status_code == 422
    assert (
        respuesta.json()["detail"]
        == "La fecha de baja no puede ser anterior a la fecha de ingreso"
    )
