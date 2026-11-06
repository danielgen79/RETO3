"""Esquemas Pydantic v2 para el recurso de vacaciones.

Solo declaran tipos: un formato de fecha inválido cae en el 422 automático de
FastAPI, y las reglas de negocio se evalúan en la ruta, en el orden exacto
que define `convenciones_vacaciones.md`.
"""

from datetime import date

from pydantic import BaseModel, ConfigDict


class VacacionCrear(BaseModel):
    fecha_inicio: date
    fecha_fin: date


class VacacionSalida(BaseModel):
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


class SaldoVacaciones(BaseModel):
    empleado_id: int
    anio: int
    dias_usados: int
    dias_disponibles: int
    solicitudes: list[SolicitudResumen]
