"""Cálculos de negocio para las solicitudes de vacaciones."""

from datetime import date, timedelta

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from festivos import es_dia_habil
from modelos import Vacacion


def contar_dias_habiles(inicio: date, fin: date) -> int:
    dias = 0
    actual = inicio
    while actual <= fin:
        if es_dia_habil(actual):
            dias += 1
        actual += timedelta(days=1)
    return dias


def cumple_antiguedad(fecha_ingreso: date, fecha_inicio: date) -> bool:
    anio_aniversario = fecha_ingreso.year + 1
    try:
        aniversario = date(anio_aniversario, fecha_ingreso.month, fecha_ingreso.day)
    except ValueError:
        # 29 de febrero sin bisiesto en el año destino: el aniversario cae el 1 de marzo.
        aniversario = date(anio_aniversario, 3, 1)
    return fecha_inicio >= aniversario


def dias_usados_en_anio(sesion: Session, empleado_id: int, anio: int) -> int:
    total = (
        sesion.query(func.sum(Vacacion.dias_habiles))
        .filter(
            Vacacion.empleado_id == empleado_id,
            extract("year", Vacacion.fecha_inicio) == anio,
        )
        .scalar()
    )
    return total or 0
