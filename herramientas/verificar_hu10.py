"""Revisión independiente de HU-10 contra la API desplegada (no forma parte de la fábrica).

Crea empleados nuevos y prueba cada regla de contexto/reglas_vacaciones.md y
contexto/convenciones_vacaciones.md, comparando códigos y mensajes letra por letra.
Solo usa la API: no lee ni modifica nada de app/ ni de salida/.

Uso:  python verificar_hu10.py
"""
import uuid

import httpx

API = "http://localhost:8000/api"
resultados: list[tuple[bool, str]] = []


def empleado(fecha_ingreso: str) -> int:
    """Crea un empleado nuevo con la fecha de ingreso indicada y devuelve su id."""
    r = httpx.post(f"{API}/empleados", json={
        "nombre": "Prueba Vacaciones", "correo": f"vac-{uuid.uuid4().hex[:10]}@empresa.com",
        "puesto": "Analista", "departamento": "Tecnología", "fecha_ingreso": fecha_ingreso})
    assert r.status_code == 201, f"No se pudo crear el empleado: {r.status_code} {r.text}"
    return r.json()["id"]


def solicitar(emp: int, inicio: str, fin: str) -> httpx.Response:
    return httpx.post(f"{API}/empleados/{emp}/vacaciones", json={"fecha_inicio": inicio, "fecha_fin": fin})


def revisar(nombre: str, r: httpx.Response, codigo: int, detail: str | None = None, **campos) -> None:
    """Compara código, mensaje exacto y campos de la respuesta; guarda el resultado."""
    cuerpo = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    problemas = []
    if r.status_code != codigo:
        problemas.append(f"código {r.status_code}, se esperaba {codigo}")
    if detail is not None and cuerpo.get("detail") != detail:
        problemas.append(f"detail {cuerpo.get('detail')!r}, se esperaba {detail!r}")
    for campo, valor in campos.items():
        if cuerpo.get(campo) != valor:
            problemas.append(f"{campo}={cuerpo.get(campo)!r}, se esperaba {valor!r}")
    resultados.append((not problemas, nombre + ("" if not problemas else " -> " + "; ".join(problemas))))


ANTIGUO = "2020-01-15"   # ingreso con antigüedad de sobra

# --- Errores en el orden de la tabla -------------------------------------
revisar("404 empleado inexistente", solicitar(999999, "2026-07-06", "2026-07-10"), 404, "Empleado no encontrado")
revisar("404 en el GET de saldo", httpx.get(f"{API}/empleados/999999/vacaciones?anio=2026"), 404,
        "Empleado no encontrado")

baja = empleado(ANTIGUO)
r = httpx.post(f"{API}/empleados/{baja}/baja", json={"fecha_baja": "2026-06-30"})
if r.status_code >= 400:
    resultados.append((False, f"No se pudo dar de baja para preparar el caso 409: {r.status_code} {r.text}"))
revisar("409 empleado dado de baja", solicitar(baja, "2026-07-06", "2026-07-10"), 409,
        "No se pueden solicitar vacaciones para un empleado dado de baja")
revisar("409 gana a fechas invertidas (orden)", solicitar(baja, "2026-07-10", "2026-07-06"), 409,
        "No se pueden solicitar vacaciones para un empleado dado de baja")

e = empleado(ANTIGUO)
revisar("400 fin antes de inicio", solicitar(e, "2026-07-10", "2026-07-06"), 400,
        "La fecha de fin no puede ser anterior a la fecha de inicio")
revisar("400 fin antes de inicio gana a cruce de año (orden)", solicitar(e, "2027-01-05", "2026-12-28"), 400,
        "La fecha de fin no puede ser anterior a la fecha de inicio")
revisar("400 cruza de año", solicitar(e, "2026-12-28", "2027-01-08"), 400,
        "Las vacaciones deben estar dentro de un mismo año calendario")
revisar("400 año fuera de la tabla (2028)", solicitar(e, "2028-07-03", "2028-07-07"), 400,
        "Solo se pueden solicitar vacaciones en 2026 y 2027")
revisar("400 año fuera de la tabla (2025)", solicitar(e, "2025-07-07", "2025-07-11"), 400,
        "Solo se pueden solicitar vacaciones en 2026 y 2027")

nuevo = empleado("2026-06-01")
revisar("400 año fuera gana a antigüedad (orden)", solicitar(nuevo, "2028-07-03", "2028-07-07"), 400,
        "Solo se pueden solicitar vacaciones en 2026 y 2027")

# --- Regla 1 · Antigüedad -------------------------------------------------
dic = empleado("2025-12-21")
revisar("400 antigüedad: le faltan días", solicitar(dic, "2026-12-18", "2026-12-18"), 400,
        "Se requiere al menos un año de antigüedad a la fecha de inicio")
revisar("400 antigüedad gana a sin días hábiles (orden)", solicitar(dic, "2026-12-19", "2026-12-20"), 400,
        "Se requiere al menos un año de antigüedad a la fecha de inicio")
revisar("201 antigüedad exacta el día del aniversario", solicitar(dic, "2026-12-21", "2026-12-31"), 201,
        dias_habiles=8, dias_restantes=4)
bisiesto = empleado("2024-02-29")
revisar("201 ingreso 29 de febrero (sin error 500)", solicitar(bisiesto, "2026-03-02", "2026-03-06"), 201,
        dias_habiles=5, dias_restantes=7)

# --- Regla 3 · Días hábiles -----------------------------------------------
e3 = empleado(ANTIGUO)
revisar("400 solo fin de semana", solicitar(e3, "2026-07-11", "2026-07-12"), 400, "El periodo no incluye días hábiles")
revisar("400 solo un festivo (16 mar 2026)", solicitar(e3, "2026-03-16", "2026-03-16"), 400,
        "El periodo no incluye días hábiles")
revisar("400 festivo en sábado + domingo (1-2 may 2027)", solicitar(e3, "2027-05-01", "2027-05-02"), 400,
        "El periodo no incluye días hábiles")
revisar("201 semana con festivo (14-18 sep 2026 = 4)", solicitar(e3, "2026-09-14", "2026-09-18"), 201,
        dias_habiles=4, dias_restantes=8)
revisar("201 festivo de 2027 (15-19 mar 2027 = 4)", solicitar(e3, "2027-03-15", "2027-03-19"), 201,
        dias_habiles=4, dias_restantes=8)

# --- Regla 2 · Tope anual -------------------------------------------------
e2 = empleado(ANTIGUO)
r = solicitar(e2, "2026-07-06", "2026-07-10")
revisar("201 primera solicitud: 5 días, quedan 7", r, 201, dias_habiles=5, dias_restantes=7)
claves = set(r.json()) if r.status_code == 201 else set()
esperadas = {"id", "empleado_id", "fecha_inicio", "fecha_fin", "dias_habiles", "dias_restantes"}
resultados.append((esperadas <= claves, f"201 trae los campos de la convención (faltan: {sorted(esperadas - claves)})"))
revisar("400 se pasa por uno: quedan 7", solicitar(e2, "2026-07-13", "2026-07-22"), 400,
        "La solicitud excede los días disponibles: quedan 7 días hábiles")
revisar("201 usar exactamente lo que queda: 7, quedan 0", solicitar(e2, "2026-07-13", "2026-07-21"), 201,
        dias_habiles=7, dias_restantes=0)
revisar("400 sin días: quedan 0", solicitar(e2, "2026-08-03", "2026-08-03"), 400,
        "La solicitud excede los días disponibles: quedan 0 días hábiles")
revisar("201 el tope es por año: 2027 empieza en 12", solicitar(e2, "2027-07-05", "2027-07-05"), 201,
        dias_habiles=1, dias_restantes=11)

e1 = empleado(ANTIGUO)
solicitar(e1, "2026-08-03", "2026-08-13")                      # 9 días -> quedan 3
revisar("400 con N = 1 sigue diciendo 'días hábiles'",
        (solicitar(e1, "2026-08-17", "2026-08-18"), solicitar(e1, "2026-08-19", "2026-08-25"))[1], 400,
        "La solicitud excede los días disponibles: quedan 1 días hábiles")

# --- Saldo (GET) ----------------------------------------------------------
r = httpx.get(f"{API}/empleados/{e2}/vacaciones?anio=2026")
revisar("GET saldo 2026", r, 200, empleado_id=e2, anio=2026, dias_usados=12, dias_disponibles=0)
if r.status_code == 200:
    resultados.append((len(r.json().get("solicitudes", [])) == 2, "GET lista las 2 solicitudes de 2026"))
r = httpx.get(f"{API}/empleados/{e2}/vacaciones")
revisar("GET sin anio usa el año en curso (2026)", r, 200, anio=2026, dias_usados=12)

# --- Formato inválido -----------------------------------------------------
revisar("422 formato de fecha inválido", solicitar(e3, "06/07/2026", "2026-07-10"), 422)

# --- Resumen --------------------------------------------------------------
for ok, texto in resultados:
    print(("OK    " if ok else "FALLA ") + texto)
fallas = sum(not ok for ok, _ in resultados)
print(f"\n{len(resultados) - fallas} de {len(resultados)} comprobaciones pasan" + (f" · {fallas} FALLAN" if fallas else ""))
