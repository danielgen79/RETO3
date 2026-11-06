"""Herramienta determinista para contar días hábiles con la tabla de festivos del contexto.

Los agentes no cuentan días hábiles de memoria: un LLM puede olvidar un festivo
(en el intento 2 de HU-10 el analista contó 4 días del 2 al 5 de febrero de 2026,
olvidando el Día de la Constitución). Esta herramienta cuenta con código.
"""
import re
from datetime import date, timedelta

from agentes.base import RAIZ, Herramienta

FUENTE = RAIZ / "contexto" / "reglas_vacaciones.md"


def festivos() -> set[date]:
    """Lee las fechas AAAA-MM-DD de la tabla de la sección «Festivos oficiales»."""
    texto = FUENTE.read_text(encoding="utf-8")
    if "## Festivos oficiales" not in texto:
        return set()
    seccion = texto.split("## Festivos oficiales", 1)[1].split("\n## ", 1)[0]
    filas = "\n".join(l for l in seccion.splitlines() if l.lstrip().startswith("|"))
    return {date.fromisoformat(f) for f in re.findall(r"\d{4}-\d{2}-\d{2}", filas)}


def contar_dias_habiles(fecha_inicio: str, fecha_fin: str) -> str:
    """Cuenta lunes a viernes que no son festivos, incluyendo inicio y fin."""
    inicio, fin = date.fromisoformat(fecha_inicio), date.fromisoformat(fecha_fin)
    if fin < inicio:
        return f"La fecha de fin {fecha_fin} es anterior a la de inicio {fecha_inicio}: el periodo no es válido."
    tabla = festivos()
    habiles, festivos_en_periodo, dia = 0, [], inicio
    while dia <= fin:
        if dia in tabla:
            festivos_en_periodo.append(dia.isoformat())
        elif dia.weekday() < 5:
            habiles += 1
        dia += timedelta(days=1)
    nota = f" Festivos dentro del periodo: {', '.join(festivos_en_periodo)}." if festivos_en_periodo else ""
    return f"{habiles} días hábiles del {fecha_inicio} al {fecha_fin} (incluye ambas fechas).{nota}"


def herramienta_dias_habiles() -> list[Herramienta]:
    """Devuelve la herramienta si el contexto tiene tabla de festivos; si no, una lista vacía."""
    if not FUENTE.exists() or not festivos():
        return []
    texto = {"type": "string"}
    return [Herramienta(
        "contar_dias_habiles",
        "Cuenta con código los días hábiles (lunes a viernes que no son festivos oficiales) entre dos "
        "fechas AAAA-MM-DD, incluyendo ambas. Úsala SIEMPRE que un escenario o caso dependa de cuántos "
        "días hábiles tiene un periodo o cuántos quedan; nunca los cuentes de memoria. "
        "Ejemplo: fecha_inicio='2026-02-02', fecha_fin='2026-02-05'.",
        {"fecha_inicio": texto, "fecha_fin": texto}, contar_dias_habiles)]
