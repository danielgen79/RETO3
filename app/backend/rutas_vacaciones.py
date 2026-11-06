"""Rutas del recurso /api/empleados/{id}/vacaciones."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import extract
from sqlalchemy.orm import Session

from database import obtener_db
from dias_habiles import contar_dias_habiles, cumple_antiguedad
from esquemas import SaldoVacaciones, VacacionesCrear, VacacionesSalida
from festivos import FESTIVOS
from modelos import Empleado, Vacaciones

router = APIRouter()

TOPE_ANUAL_DIAS_HABILES = 12


def obtener_empleado_o_404(db: Session, id: int) -> Empleado:
    empleado = db.query(Empleado).filter(Empleado.id == id).first()
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado


def calcular_dias_usados(db: Session, empleado_id: int, anio: int) -> int:
    solicitudes = (
        db.query(Vacaciones)
        .filter(
            Vacaciones.empleado_id == empleado_id,
            extract("year", Vacaciones.fecha_inicio) == anio,
        )
        .all()
    )
    return sum(solicitud.dias_habiles for solicitud in solicitudes)


@router.post(
    "/empleados/{empleado_id}/vacaciones",
    response_model=VacacionesSalida,
    status_code=201,
)
def solicitar_vacaciones(
    empleado_id: int, datos: VacacionesCrear, db: Session = Depends(obtener_db)
):
    empleado = obtener_empleado_o_404(db, empleado_id)

    if empleado.estado == "baja":
        raise HTTPException(
            status_code=409,
            detail="No se pueden solicitar vacaciones para un empleado dado de baja",
        )

    if datos.fecha_fin < datos.fecha_inicio:
        raise HTTPException(
            status_code=400,
            detail="La fecha de fin no puede ser anterior a la fecha de inicio",
        )

    if datos.fecha_inicio.year != datos.fecha_fin.year:
        raise HTTPException(
            status_code=400,
            detail="Las vacaciones deben estar dentro de un mismo año calendario",
        )

    anio = datos.fecha_inicio.year
    if anio not in FESTIVOS:
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden solicitar vacaciones en 2026 y 2027",
        )

    if not cumple_antiguedad(empleado.fecha_ingreso, datos.fecha_inicio):
        raise HTTPException(
            status_code=400,
            detail="Se requiere al menos un año de antigüedad a la fecha de inicio",
        )

    dias_habiles = contar_dias_habiles(datos.fecha_inicio, datos.fecha_fin, FESTIVOS[anio])
    if dias_habiles == 0:
        raise HTTPException(
            status_code=400,
            detail="El periodo no incluye días hábiles",
        )

    dias_usados = calcular_dias_usados(db, empleado_id, anio)
    dias_disponibles = TOPE_ANUAL_DIAS_HABILES - dias_usados
    if dias_habiles > dias_disponibles:
        raise HTTPException(
            status_code=400,
            detail=f"La solicitud excede los días disponibles: quedan {dias_disponibles} días hábiles",
        )

    solicitud = Vacaciones(
        empleado_id=empleado_id,
        fecha_inicio=datos.fecha_inicio,
        fecha_fin=datos.fecha_fin,
        dias_habiles=dias_habiles,
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)

    return VacacionesSalida(
        id=solicitud.id,
        empleado_id=solicitud.empleado_id,
        fecha_inicio=solicitud.fecha_inicio,
        fecha_fin=solicitud.fecha_fin,
        dias_habiles=solicitud.dias_habiles,
        dias_restantes=dias_disponibles - dias_habiles,
    )


@router.get(
    "/empleados/{empleado_id}/vacaciones",
    response_model=SaldoVacaciones,
)
def consultar_saldo_vacaciones(
    empleado_id: int, anio: int | None = None, db: Session = Depends(obtener_db)
):
    obtener_empleado_o_404(db, empleado_id)

    anio_consulta = anio if anio is not None else date.today().year
    solicitudes = (
        db.query(Vacaciones)
        .filter(
            Vacaciones.empleado_id == empleado_id,
            extract("year", Vacaciones.fecha_inicio) == anio_consulta,
        )
        .order_by(Vacaciones.fecha_inicio.asc())
        .all()
    )
    dias_usados = sum(solicitud.dias_habiles for solicitud in solicitudes)

    return SaldoVacaciones(
        empleado_id=empleado_id,
        anio=anio_consulta,
        dias_usados=dias_usados,
        dias_disponibles=TOPE_ANUAL_DIAS_HABILES - dias_usados,
        solicitudes=solicitudes,
    )
