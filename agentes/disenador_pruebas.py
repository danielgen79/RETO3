"""Sesión 1 · Agente 2, diseñador de pruebas: criterios de aceptación -> casos de prueba.

Uso:  python -m agentes.disenador_pruebas salida/HU-01/criterios.feature
"""
import json
import re
import sys
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ValidationError

from agentes.analista import escenarios, mensajes_exactos
from agentes.base import RAIZ, Herramienta, ejecutar_agente, herramientas_archivos, rel
from agentes.calendario import herramienta_dias_habiles


class CasoPrueba(BaseModel):
    id: str                          # CP-01, CP-02...
    escenario: str                   # nombre exacto del escenario Gherkin que cubre
    nivel: Literal["api", "e2e"]     # api: se prueba con HTTP; e2e: se prueba en el navegador
    precondiciones: list[str]
    pasos: list[str]
    datos: dict[str, str]
    resultado_esperado: str


class PlanPruebas(BaseModel):
    historia: str
    casos: list[CasoPrueba]


SISTEMA = """Eres diseñador de pruebas de software. A partir de criterios de aceptación en Gherkin
escribes casos de prueba que luego otra persona automatizará.

Cómo trabajas:
1. Lee {criterios} y contexto/convenciones_app.md (ahí están la API y los data-testid de la pantalla).
2. Para cada escenario escribe al menos un caso de nivel "api". Si el escenario involucra la pantalla,
   escribe además uno de nivel "e2e" cuyos pasos mencionen los data-testid que se usan.
3. Usa datos concretos. Para correos usa el dominio corporativo empresa.com.
4. Los ids de empleado los asigna el sistema al crearlo: en rutas y data-testid escribe la plantilla
   tal como viene en las convenciones (por ejemplo fila-empleado-{{id}} o
   /api/empleados/{{empleado_id}}/vacaciones) y aclara que se usa el id del empleado creado en la
   precondición. Nunca uses un número de empleado de ejemplo (como EMP-0007) en rutas ni data-testid.
5. Cada caso crea su propio empleado en las precondiciones, con la fecha_ingreso que el caso necesita,
   para que los casos no dependan entre sí ni del orden en que se ejecutan.
6. En "resultado_esperado" escribe el código de respuesta y el mensaje exacto, letra por letra,
   tal como aparece en los criterios (con el número concreto donde el mensaje lleva un número).
   Comprueba con la herramienta contar_dias_habiles cada periodo que uses y cada número de días
   hábiles esperado; nunca los cuentes de memoria. Si un número de los criterios no coincide con la
   herramienta, usa el de la herramienta y dilo en "precondiciones".
7. Guarda los casos llamando a la herramienta guardar_casos (no escribas el JSON a mano),
   EN LOTES DE MÁXIMO 5 CASOS POR LLAMADA: cada llamada agrega sus casos a los ya guardados, y un
   caso con un id que ya existe reemplaza al anterior. Escribe pasos y precondiciones breves.
   - "nivel" solo puede ser "api" o "e2e".
   - En "datos" TODOS los valores son texto: "201", no 201; para un campo vacío usa "", nunca null.
   - En "escenario" copia el nombre del escenario EXACTAMENTE como aparece después de "Escenario:".
   - Si guardar_casos devuelve un error, corrige lo que indica y vuelve a llamarla.
8. Responde al final con una sola línea: cuántos casos escribiste."""


def validar_plan(texto: str, gherkin: str, mensajes: list[str] | None = None) -> list[str]:
    """Evaluador determinista: JSON válido, cada escenario cubierto y, si se pasan `mensajes`,
    cada mensaje exacto presente en algún caso (un « N » acepta un número concreto)."""
    try:
        plan = PlanPruebas.model_validate_json(texto)
    except ValidationError as e:
        return [f"El JSON no cumple el esquema: {e.errors()[:3]}"]
    cubiertos = {c.escenario.strip() for c in plan.casos}
    problemas = [f"Escenario sin casos: {e}" for e in escenarios(gherkin) if e not in cubiertos]
    ids = [c.id for c in plan.casos]
    if len(ids) != len(set(ids)):
        problemas.append("Hay ids de caso repetidos.")
    contenido = "\n".join(c.resultado_esperado + "\n" + "\n".join(c.pasos) + "\n" + "\n".join(c.datos.values())
                          for c in plan.casos)
    for mensaje in mensajes or []:
        patron = r" (?:N|\d+) ".join(re.escape(parte) for parte in mensaje.split(" N "))
        if not re.search(patron, contenido):
            problemas.append(f"Ningún caso verifica el mensaje exacto, letra por letra: «{mensaje}».")
    if re.search(r"[-/]EMP-\d", contenido):              # p. ej. fila-empleado-EMP-0007 o /api/empleados/EMP-0007
        problemas.append("Usa la plantilla con {id} del empleado creado, no un número de empleado de ejemplo.")
    return problemas


def herramienta_guardar_casos(destino: Path) -> Herramienta:
    """El contrato viaja en el esquema de la herramienta: el modelo llena campos, no escribe JSON a mano."""
    def guardar_casos(historia: str, casos: list) -> str:
        try:
            plan = PlanPruebas.model_validate({"historia": historia, "casos": casos})
        except ValidationError as e:  # el error regresa al modelo como texto, corto y accionable
            raise ValueError("Los casos no cumplen el esquema: " + "; ".join(
                f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors()[:5]))
        # Se guarda por lotes: los casos nuevos se suman a los anteriores y un id repetido reemplaza al viejo.
        # Así una historia con muchos escenarios no obliga a escribir todo en una sola respuesta (max_tokens).
        por_id = {}
        if destino.exists():
            por_id = {c.id: c for c in PlanPruebas.model_validate_json(destino.read_text(encoding="utf-8")).casos}
        por_id.update({c.id: c for c in plan.casos})
        total = PlanPruebas(historia=historia, casos=list(por_id.values()))
        destino.write_text(total.model_dump_json(indent=2), encoding="utf-8")
        return f"Guardados {len(plan.casos)} casos; el archivo {rel(destino)} tiene {len(total.casos)} en total"
    return Herramienta(
        "guardar_casos",
        "Guarda un lote de hasta 5 casos en casos_prueba.json (se suman a los ya guardados; un id repetido "
        "reemplaza al anterior) y lo valida; si hay errores, los devuelve para que corrijas. Ejemplo: historia='HU-01', casos=[{'id': 'CP-01', 'escenario': 'Alta exitosa', 'nivel': 'api', "
        "'precondiciones': [], 'pasos': ['...'], 'datos': {'correo': 'ana@empresa.com'}, 'resultado_esperado': '...'}].",
        {"historia": {"type": "string"},
         "casos": {"type": "array", "items": CasoPrueba.model_json_schema()}},
        guardar_casos)


def disenar_casos(criterios: Path, max_intentos: int = 3) -> Path:
    carpeta = criterios.parent
    destino = carpeta / "casos_prueba.json"
    mensajes = mensajes_exactos(carpeta.name)              # carpeta.name es la historia, por ejemplo HU-10
    lectura = [h for h in herramientas_archivos(lectura=[RAIZ / "contexto", carpeta], escritura=carpeta)
               if h.nombre != "escribir_archivo"]          # solo se escribe a través de guardar_casos
    herramientas = lectura + herramienta_dias_habiles() + [herramienta_guardar_casos(destino)]
    sistema = SISTEMA.format(criterios=rel(criterios))
    gherkin = criterios.read_text(encoding="utf-8")
    tarea = f"Diseña los casos de prueba para {rel(criterios)}."
    destino.unlink(missing_ok=True)                        # cada ejecución empieza sin casos viejos
    for intento in range(1, max_intentos + 1):
        print(f"Diseñador de pruebas · intento {intento}")
        ejecutar_agente(sistema, herramientas, tarea, max_pasos=25, nombre="disenador")   # varios lotes
        problemas = validar_plan(destino.read_text(encoding="utf-8"), gherkin, mensajes) if destino.exists() \
            else [f"No se escribió {rel(destino)}."]
        if not problemas:
            return destino
        print("  Validador de casos:\n  - " + "\n  - ".join(problemas))
        tarea += "\n\nTu versión anterior tiene estos problemas; corrígelos:\n- " + "\n- ".join(problemas)
    raise ValueError("Casos inválidos tras varios intentos:\n- " + "\n- ".join(problemas))


if __name__ == "__main__":
    ruta = disenar_casos(Path(sys.argv[1]).resolve())
    plan = PlanPruebas.model_validate_json(ruta.read_text(encoding="utf-8"))
    print(f"\nListo: {rel(ruta)} · {len(plan.casos)} casos "
          f"({sum(c.nivel == 'api' for c in plan.casos)} api, {sum(c.nivel == 'e2e' for c in plan.casos)} e2e)")
