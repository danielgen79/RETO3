"""Rutas del recurso /api/empleados/{id}/vacaciones."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import obtener_db
from esquemas_vacaciones import SaldoAnioSalida, VacacionesCrear, VacacionesSalida
from festivos import FESTIVOS
from modelos import Empleado, Vacaciones
from reglas_vacaciones import calcular_dias_habiles, cumple_antiguedad

router = APIRouter()

TOPE_ANUAL = 12


def obtener_empleado_o_404(db: Session, id: int) -> Empleado:
    empleado = db.query(Empleado).filter(Empleado.id == id).first()
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado


def dias_usados_en_anio(db: Session, empleado_id: int, anio: int) -> int:
    total = (
        db.query(func.coalesce(func.sum(Vacaciones.dias_habiles), 0))
        .filter(
            Vacaciones.empleado_id == empleado_id,
            Vacaciones.fecha_inicio >= date(anio, 1, 1),
            Vacaciones.fecha_inicio <= date(anio, 12, 31),
        )
        .scalar()
    )
    return total or 0


@router.post(
    "/empleados/{id}/vacaciones", response_model=VacacionesSalida, status_code=201
)
def solicitar_vacaciones(
    id: int, datos: VacacionesCrear, db: Session = Depends(obtener_db)
):
    empleado = obtener_empleado_o_404(db, id)

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

    dias_habiles = calcular_dias_habiles(datos.fecha_inicio, datos.fecha_fin)
    if dias_habiles == 0:
        raise HTTPException(
            status_code=400, detail="El periodo no incluye días hábiles"
        )

    usados = dias_usados_en_anio(db, id, anio)
    disponibles = TOPE_ANUAL - usados
    if dias_habiles > disponibles:
        raise HTTPException(
            status_code=400,
            detail=(
                "La solicitud excede los días disponibles: "
                f"quedan {disponibles} días hábiles"
            ),
        )

    solicitud = Vacaciones(
        empleado_id=id,
        fecha_inicio=datos.fecha_inicio,
        fecha_fin=datos.fecha_fin,
        dias_habiles=dias_habiles,
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)

    return {
        "id": solicitud.id,
        "empleado_id": id,
        "fecha_inicio": solicitud.fecha_inicio,
        "fecha_fin": solicitud.fecha_fin,
        "dias_habiles": dias_habiles,
        "dias_restantes": disponibles - dias_habiles,
    }


@router.get("/empleados/{id}/vacaciones", response_model=SaldoAnioSalida)
def consultar_saldo_vacaciones(
    id: int, anio: int | None = None, db: Session = Depends(obtener_db)
):
    obtener_empleado_o_404(db, id)
    anio_consulta = anio or date.today().year

    solicitudes = (
        db.query(Vacaciones)
        .filter(
            Vacaciones.empleado_id == id,
            Vacaciones.fecha_inicio >= date(anio_consulta, 1, 1),
            Vacaciones.fecha_inicio <= date(anio_consulta, 12, 31),
        )
        .order_by(Vacaciones.fecha_inicio.asc())
        .all()
    )
    usados = sum(solicitud.dias_habiles for solicitud in solicitudes)

    return {
        "empleado_id": id,
        "anio": anio_consulta,
        "dias_usados": usados,
        "dias_disponibles": TOPE_ANUAL - usados,
        "solicitudes": solicitudes,
    }
