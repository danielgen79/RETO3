"""Pruebas de API para HU-02: ver el directorio de empleados."""

import uuid

import httpx


def correo_unico(local: str, dominio: str = "empresa.com") -> str:
    """Genera un correo único para que cada prueba sea repetible sin choques."""
    return f"{local}.{uuid.uuid4().hex[:8]}@{dominio}"


def registrar_empleado(
    url_api,
    nombre,
    correo,
    puesto="Analista",
    departamento="Tecnología",
    fecha_ingreso="2024-01-15",
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


def dar_baja(url_api, id_empleado, fecha_baja="2024-06-01"):
    """Da de baja a un empleado por la API para preparar la precondición de un caso."""
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{id_empleado}/baja",
        json={"fecha_baja": fecha_baja},
    )
    assert respuesta.status_code == 200
    return respuesta.json()


def test_cp_01_listado_completo(url_api):
    """CP-01: Ver el listado completo del directorio."""
    activo_1 = registrar_empleado(
        url_api,
        "Ana Pérez",
        correo_unico("Ana.Perez"),
        puesto="Analista de RH",
        departamento="Recursos Humanos",
    )
    creado_b = registrar_empleado(
        url_api,
        "Luis Gómez",
        correo_unico("Luis.Gomez"),
        puesto="Vendedor",
        departamento="Ventas",
    )
    de_baja = dar_baja(url_api, creado_b["id"])
    activo_2 = registrar_empleado(
        url_api,
        "María López",
        correo_unico("Maria.Lopez"),
        puesto="Contadora",
        departamento="Finanzas",
    )

    respuesta = httpx.get(f"{url_api}/api/empleados")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert isinstance(cuerpo, list)

    por_numero = {e["numero_empleado"]: e for e in cuerpo}
    for esperado, estado_esperado in (
        (activo_1, "activo"),
        (de_baja, "baja"),
        (activo_2, "activo"),
    ):
        encontrado = por_numero[esperado["numero_empleado"]]
        assert encontrado["estado"] == estado_esperado
        for campo in ("numero_empleado", "nombre", "puesto", "departamento", "estado"):
            assert campo in encontrado


def test_cp_03_busqueda_por_nombre(url_api):
    """CP-03: Buscar por nombre sin distinguir mayúsculas de minúsculas."""
    correo = correo_unico("Ana.Perez")
    creado = registrar_empleado(
        url_api, "Ana Pérez", correo, puesto="Analista de RH", departamento="Recursos Humanos"
    )

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"busqueda": "ana"})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    coincidencias = [e for e in cuerpo if e["numero_empleado"] == creado["numero_empleado"]]
    assert len(coincidencias) == 1
    assert coincidencias[0]["nombre"] == "Ana Pérez"
    assert all("ana" in e["nombre"].lower() or "ana" in e["correo"].lower() for e in cuerpo)


def test_cp_05_busqueda_por_correo(url_api):
    """CP-05: Buscar por correo sin distinguir mayúsculas de minúsculas."""
    correo = correo_unico("ana.perez")
    creado = registrar_empleado(
        url_api, "Ana Pérez", correo, puesto="Analista de RH", departamento="Recursos Humanos"
    )

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"busqueda": correo.upper()})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo) == 1
    assert cuerpo[0]["numero_empleado"] == creado["numero_empleado"]
    assert cuerpo[0]["correo"] == correo.lower()


def test_cp_07_filtrar_por_departamento(url_api):
    """CP-07: Filtrar por un departamento válido."""
    correo = correo_unico("Luis.Gomez")
    creado = registrar_empleado(
        url_api, "Luis Gómez", correo, puesto="Vendedor", departamento="Ventas"
    )

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"departamento": "Ventas"})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert any(e["numero_empleado"] == creado["numero_empleado"] for e in cuerpo)
    assert all(e["departamento"] == "Ventas" for e in cuerpo)


def test_cp_09_empleado_de_baja_sigue_en_listado(url_api):
    """CP-09: Un empleado dado de baja sigue apareciendo en el directorio."""
    correo = correo_unico("Luis.Gomez")
    creado = registrar_empleado(
        url_api, "Luis Gómez", correo, puesto="Vendedor", departamento="Ventas"
    )
    dar_baja(url_api, creado["id"])

    respuesta = httpx.get(f"{url_api}/api/empleados")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    coincidencia = next(e for e in cuerpo if e["numero_empleado"] == creado["numero_empleado"])
    assert coincidencia["estado"] == "baja"


def test_cp_11_busqueda_sin_coincidencias(url_api):
    """CP-11: Buscar un término que no coincide con ningún empleado."""
    registrar_empleado(url_api, "Pedro Ramírez", correo_unico("pedro.ramirez"))

    respuesta = httpx.get(
        f"{url_api}/api/empleados", params={"busqueda": "Zzz_no_existe"}
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == []
