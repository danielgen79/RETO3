"""Esquemas Pydantic v2 para el recurso vacaciones."""

from datetime import date

from pydantic import BaseModel, ConfigDict


class VacacionesCrear(BaseModel):
    fecha_inicio: date
    fecha_fin: date


class VacacionesSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    empleado_id: int
    fecha_inicio: date
    fecha_fin: date
    dias_habiles: int
    dias_restantes: int


class SolicitudResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha_inicio: date
    fecha_fin: date
    dias_habiles: int


class SaldoAnioSalida(BaseModel):
    empleado_id: int
    anio: int
    dias_usados: int
    dias_disponibles: int
    solicitudes: list[SolicitudResumen]
