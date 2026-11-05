"""Pruebas de API para HU-01: registrar empleado."""

import re
import uuid

import httpx


def correo_unico(local: str, dominio: str = "empresa.com") -> str:
    """Genera un correo único para que cada prueba sea repetible sin choques."""
    return f"{local}.{uuid.uuid4().hex[:8]}@{dominio}"


def test_cp_01_registro_exitoso(url_api):
    """CP-01: Registro exitoso de un nuevo empleado."""
    correo = correo_unico("Ana.Perez")
    datos = {
        "nombre": "Ana Pérez",
        "correo": correo,
        "puesto": "Analista de RH",
        "departamento": "Recursos Humanos",
        "fecha_ingreso": "2024-01-15",
    }

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert re.fullmatch(r"EMP-\d{4}", cuerpo["numero_empleado"])
    assert cuerpo["correo"] == correo.lower()
    assert cuerpo["estado"] == "activo"
    assert cuerpo["nombre"] == datos["nombre"]
    assert cuerpo["puesto"] == datos["puesto"]
    assert cuerpo["departamento"] == datos["departamento"]
    assert cuerpo["fecha_ingreso"] == datos["fecha_ingreso"]


def test_cp_03_correo_ya_registrado(url_api):
    """CP-03: Rechazo por correo ya registrado (regla 1)."""
    correo = correo_unico("Carlos.Ruiz")
    datos_iniciales = {
        "nombre": "Carlos Ruiz Gómez",
        "correo": correo,
        "puesto": "Supervisor",
        "departamento": "Operaciones",
        "fecha_ingreso": "2024-02-01",
    }
    primera = httpx.post(f"{url_api}/api/empleados", json=datos_iniciales)
    assert primera.status_code == 201

    datos_duplicados = {**datos_iniciales, "correo": correo.upper()}
    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos_duplicados)

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "El correo ya está registrado"


def test_cp_05_correo_no_corporativo(url_api):
    """CP-05: Rechazo por correo que no es corporativo (regla 2)."""
    datos = {
        "nombre": "Luis Gómez",
        "correo": correo_unico("luis.gomez", dominio="gmail.com"),
        "puesto": "Vendedor",
        "departamento": "Ventas",
        "fecha_ingreso": "2024-02-01",
    }

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == "Usa el correo corporativo @empresa.com"


def test_cp_07_nombre_muy_corto(url_api):
    """CP-07: Rechazo por nombre con menos de 2 caracteres (regla 3)."""
    datos = {
        "nombre": "A",
        "correo": correo_unico("a.valido"),
        "puesto": "Analista",
        "departamento": "Finanzas",
        "fecha_ingreso": "2024-02-01",
    }

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == "El nombre debe tener entre 2 y 80 caracteres"


def test_cp_09_fecha_ingreso_futura(url_api):
    """CP-09: Rechazo por fecha de ingreso futura (regla 4)."""
    datos = {
        "nombre": "Mario Díaz",
        "correo": correo_unico("mario.diaz"),
        "puesto": "Técnico",
        "departamento": "Tecnología",
        "fecha_ingreso": "2099-01-01",
    }

    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == "La fecha de ingreso no puede ser futura"
