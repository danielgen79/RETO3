"""Cálculos de negocio para vacaciones: días hábiles y antigüedad."""

from datetime import date, timedelta


def contar_dias_habiles(fecha_inicio: date, fecha_fin: date, festivos: list[date]) -> int:
    festivos_set = set(festivos)
    dias = 0
    actual = fecha_inicio
    while actual <= fecha_fin:
        if actual.weekday() < 5 and actual not in festivos_set:
            dias += 1
        actual += timedelta(days=1)
    return dias


def cumple_antiguedad(fecha_ingreso: date, fecha_inicio: date) -> bool:
    try:
        aniversario = date(fecha_ingreso.year + 1, fecha_ingreso.month, fecha_ingreso.day)
    except ValueError:
        aniversario = date(fecha_ingreso.year + 1, 3, 1)
    return fecha_inicio >= aniversario
