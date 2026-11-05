"""Pruebas end-to-end para HU-01: registrar empleado."""

import re
import uuid


def correo_unico(local: str, dominio: str = "empresa.com") -> str:
    """Genera un correo único para que cada prueba sea repetible sin choques."""
    return f"{local}.{uuid.uuid4().hex[:8]}@{dominio}"


def registrar_empleado(page, url_web, datos):
    """Completa y envía el formulario de registro con los datos dados."""
    page.goto(url_web)
    page.get_by_test_id("empleado-nombre").fill(datos["nombre"])
    page.get_by_test_id("empleado-correo").fill(datos["correo"])
    page.get_by_test_id("empleado-puesto").fill(datos["puesto"])
    page.get_by_test_id("empleado-departamento").select_option(datos["departamento"])
    page.get_by_test_id("empleado-fecha-ingreso").fill(datos["fecha_ingreso"])
    page.get_by_test_id("empleado-guardar").click()


def test_cp_02_registro_exitoso(page, url_web):
    """CP-02: Registro exitoso de un nuevo empleado."""
    datos = {
        "nombre": "Ana Pérez",
        "correo": correo_unico("Ana.Perez"),
        "puesto": "Analista de RH",
        "departamento": "Recursos Humanos",
        "fecha_ingreso": "2024-01-15",
    }

    registrar_empleado(page, url_web, datos)

    mensaje = page.get_by_test_id("mensaje-exito")
    mensaje.wait_for()
    assert re.fullmatch(r"Empleado EMP-\d{4} registrado correctamente", mensaje.text_content())


def test_cp_04_correo_ya_registrado(page, url_web):
    """CP-04: Rechazo por correo ya registrado (regla 1)."""
    correo = correo_unico("Carlos.Ruiz")
    datos = {
        "nombre": "Carlos Ruiz Gómez",
        "correo": correo,
        "puesto": "Supervisor",
        "departamento": "Operaciones",
        "fecha_ingreso": "2024-02-01",
    }

    registrar_empleado(page, url_web, datos)
    page.get_by_test_id("mensaje-exito").wait_for()

    datos_duplicados = {**datos, "correo": correo.upper()}
    registrar_empleado(page, url_web, datos_duplicados)

    mensaje = page.get_by_test_id("mensaje-error")
    mensaje.wait_for()
    assert mensaje.text_content() == "El correo ya está registrado"


def test_cp_06_correo_no_corporativo(page, url_web):
    """CP-06: Rechazo por correo que no es corporativo (regla 2)."""
    datos = {
        "nombre": "Luis Gómez",
        "correo": correo_unico("luis.gomez", dominio="gmail.com"),
        "puesto": "Vendedor",
        "departamento": "Ventas",
        "fecha_ingreso": "2024-02-01",
    }

    registrar_empleado(page, url_web, datos)

    mensaje = page.get_by_test_id("mensaje-error")
    mensaje.wait_for()
    assert mensaje.text_content() == "Usa el correo corporativo @empresa.com"


def test_cp_08_nombre_muy_corto(page, url_web):
    """CP-08: Rechazo por nombre con menos de 2 caracteres (regla 3)."""
    datos = {
        "nombre": "A",
        "correo": correo_unico("a.valido"),
        "puesto": "Analista",
        "departamento": "Finanzas",
        "fecha_ingreso": "2024-02-01",
    }

    registrar_empleado(page, url_web, datos)

    mensaje = page.get_by_test_id("mensaje-error")
    mensaje.wait_for()
    assert mensaje.text_content() == "El nombre debe tener entre 2 y 80 caracteres"


def test_cp_10_fecha_ingreso_futura(page, url_web):
    """CP-10: Rechazo por fecha de ingreso futura (regla 4)."""
    datos = {
        "nombre": "Mario Díaz",
        "correo": correo_unico("mario.diaz"),
        "puesto": "Técnico",
        "departamento": "Tecnología",
        "fecha_ingreso": "2099-01-01",
    }

    registrar_empleado(page, url_web, datos)

    mensaje = page.get_by_test_id("mensaje-error")
    mensaje.wait_for()
    assert mensaje.text_content() == "La fecha de ingreso no puede ser futura"
