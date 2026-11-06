"""Rutas del recurso /api/empleados/{empleado_id}/vacaciones."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import extract
from sqlalchemy.orm import Session

from calculo_vacaciones import contar_dias_habiles, cumple_antiguedad, dias_usados_en_anio
from database import obtener_db
from esquemas_vacaciones import SaldoVacaciones, VacacionCrear, VacacionSalida
from festivos import ANIOS_SOPORTADOS
from modelos import Empleado, Vacacion

router = APIRouter()

TOPE_ANUAL_DIAS_HABILES = 12


def obtener_empleado_o_404(db: Session, empleado_id: int) -> Empleado:
    empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado


@router.post(
    "/empleados/{empleado_id}/vacaciones",
    response_model=VacacionSalida,
    status_code=201,
)
def solicitar_vacaciones(
    empleado_id: int, datos: VacacionCrear, db: Session = Depends(obtener_db)
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
    if anio not in ANIOS_SOPORTADOS:
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden solicitar vacaciones en 2026 y 2027",
        )

    if not cumple_antiguedad(empleado.fecha_ingreso, datos.fecha_inicio):
        raise HTTPException(
            status_code=400,
            detail="Se requiere al menos un año de antigüedad a la fecha de inicio",
        )

    dias_habiles = contar_dias_habiles(datos.fecha_inicio, datos.fecha_fin)
    if dias_habiles == 0:
        raise HTTPException(
            status_code=400, detail="El periodo no incluye días hábiles"
        )

    dias_disponibles = TOPE_ANUAL_DIAS_HABILES - dias_usados_en_anio(
        db, empleado_id, anio
    )
    if dias_habiles > dias_disponibles:
        raise HTTPException(
            status_code=400,
            detail=(
                "La solicitud excede los días disponibles: "
                f"quedan {dias_disponibles} días hábiles"
            ),
        )

    vacacion = Vacacion(
        empleado_id=empleado_id,
        fecha_inicio=datos.fecha_inicio,
        fecha_fin=datos.fecha_fin,
        dias_habiles=dias_habiles,
    )
    db.add(vacacion)
    db.commit()
    db.refresh(vacacion)

    return VacacionSalida(
        id=vacacion.id,
        empleado_id=empleado_id,
        fecha_inicio=vacacion.fecha_inicio,
        fecha_fin=vacacion.fecha_fin,
        dias_habiles=dias_habiles,
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
        db.query(Vacacion)
        .filter(
            Vacacion.empleado_id == empleado_id,
            extract("year", Vacacion.fecha_inicio) == anio_consulta,
        )
        .order_by(Vacacion.fecha_inicio.asc())
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
