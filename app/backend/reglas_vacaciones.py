"""Reglas de negocio para el cálculo de vacaciones (HU-10)."""

from datetime import date, timedelta

from festivos import FESTIVOS


def calcular_dias_habiles(fecha_inicio: date, fecha_fin: date) -> int:
    festivos_anio = FESTIVOS.get(fecha_inicio.year, set())
    dias = 0
    actual = fecha_inicio
    while actual <= fecha_fin:
        if actual.weekday() < 5 and actual not in festivos_anio:
            dias += 1
        actual += timedelta(days=1)
    return dias


def _un_anio_despues(fecha: date) -> date:
    try:
        return fecha.replace(year=fecha.year + 1)
    except ValueError:
        # 29 de febrero en año no bisiesto: el aniversario cae el 1 de marzo.
        return date(fecha.year + 1, 3, 1)


def cumple_antiguedad(fecha_ingreso: date, fecha_inicio: date) -> bool:
    return fecha_inicio >= _un_anio_despues(fecha_ingreso)
