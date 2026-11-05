"""Pruebas end-to-end para HU-02: ver el directorio de empleados."""

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


def dar_baja(url_api, id_empleado, fecha_baja="2024-06-01"):
    """Da de baja a un empleado por la API para preparar la precondición de un caso."""
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{id_empleado}/baja",
        json={"fecha_baja": fecha_baja},
    )
    assert respuesta.status_code == 200
    return respuesta.json()


def fila_de(page, numero_empleado):
    """Ubica la fila del directorio correspondiente a un número de empleado."""
    celda = page.locator('[data-testid^="numero-empleado-"]', has_text=numero_empleado)
    celda.wait_for()
    id_fila = celda.get_attribute("data-testid").replace("numero-empleado-", "")
    return page.get_by_test_id(f"fila-empleado-{id_fila}")


def test_cp_02_listado_completo(page, url_web, url_api):
    """CP-02: Ver el listado completo del directorio."""
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

    page.goto(url_web)
    page.get_by_test_id("tabla-empleados").wait_for()

    for esperado, estado_esperado in (
        (activo_1, "Activo"),
        (de_baja, "Baja"),
        (activo_2, "Activo"),
    ):
        fila = page.get_by_test_id(f"fila-empleado-{esperado['id']}")
        fila.wait_for()
        assert (
            page.get_by_test_id(f"numero-empleado-{esperado['id']}").text_content()
            == esperado["numero_empleado"]
        )
        assert (
            page.get_by_test_id(f"estado-empleado-{esperado['id']}").text_content()
            == estado_esperado
        )


def test_cp_04_busqueda_por_nombre(page, url_web, url_api):
    """CP-04: Buscar por nombre sin distinguir mayúsculas de minúsculas."""
    correo = correo_unico("Ana.Perez")
    creado = registrar_empleado(
        url_api, "Ana Pérez", correo, puesto="Analista de RH", departamento="Recursos Humanos"
    )

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill("ana")

    fila_de(page, creado["numero_empleado"]).wait_for()


def test_cp_06_busqueda_por_correo(page, url_web, url_api):
    """CP-06: Buscar por correo sin distinguir mayúsculas de minúsculas."""
    correo = correo_unico("ana.perez")
    creado = registrar_empleado(
        url_api, "Ana Pérez", correo, puesto="Analista de RH", departamento="Recursos Humanos"
    )

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(correo.upper())

    tabla = page.get_by_test_id("tabla-empleados")
    filas = tabla.locator('[data-testid^="fila-empleado-"]')
    fila_de(page, creado["numero_empleado"]).wait_for()
    assert filas.count() == 1


def test_cp_08_filtrar_por_departamento(page, url_web, url_api):
    """CP-08: Filtrar por un departamento válido."""
    correo = correo_unico("Luis.Gomez")
    creado = registrar_empleado(
        url_api, "Luis Gómez", correo, puesto="Vendedor", departamento="Ventas"
    )

    page.goto(url_web)
    page.get_by_test_id("filtro-departamento").select_option("Ventas")

    fila_de(page, creado["numero_empleado"]).wait_for()


def test_cp_10_empleado_de_baja_sigue_en_directorio(page, url_web, url_api):
    """CP-10: Un empleado dado de baja sigue apareciendo en el directorio."""
    creado = registrar_empleado(
        url_api, "Luis Gómez", correo_unico("Luis.Gomez"), puesto="Vendedor", departamento="Ventas"
    )
    de_baja = dar_baja(url_api, creado["id"])

    page.goto(url_web)

    fila = page.get_by_test_id(f"fila-empleado-{de_baja['id']}")
    fila.wait_for()
    assert page.get_by_test_id(f"estado-empleado-{de_baja['id']}").text_content() == "Baja"


def test_cp_12_busqueda_sin_resultados(page, url_web):
    """CP-12: Buscar un término que no coincide con ningún empleado."""
    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(f"Zzz_no_existe_{uuid.uuid4().hex[:8]}")

    mensaje = page.get_by_test_id("sin-resultados")
    mensaje.wait_for()
    assert mensaje.text_content() == "No se encontraron empleados que coincidan con la búsqueda."
