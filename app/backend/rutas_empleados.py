"""Rutas del recurso /api/empleados y /api/departamentos."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from catalogo import DEPARTAMENTOS
from database import obtener_db
from esquemas import EmpleadoActualizar, EmpleadoBaja, EmpleadoCrear, EmpleadoSalida
from modelos import Empleado

router = APIRouter()


def generar_numero_empleado(db: Session) -> str:
    total = db.query(func.count(Empleado.id)).scalar() or 0
    return f"EMP-{total + 1:04d}"


def obtener_empleado_o_404(db: Session, id: int) -> Empleado:
    empleado = db.query(Empleado).filter(Empleado.id == id).first()
    if empleado is None:
        raise HTTPException(status_code=404, detail="El empleado no existe")
    return empleado


@router.post("/empleados", response_model=EmpleadoSalida, status_code=201)
def crear_empleado(datos: EmpleadoCrear, db: Session = Depends(obtener_db)):
    existente = (
        db.query(Empleado).filter(func.lower(Empleado.correo) == datos.correo).first()
    )
    if existente is not None:
        raise HTTPException(status_code=409, detail="El correo ya está registrado")

    empleado = Empleado(
        numero_empleado=generar_numero_empleado(db),
        nombre=datos.nombre,
        correo=datos.correo,
        puesto=datos.puesto,
        departamento=datos.departamento,
        fecha_ingreso=datos.fecha_ingreso,
        estado="activo",
        creado_en=datetime.utcnow(),
    )
    db.add(empleado)
    db.commit()
    db.refresh(empleado)
    return empleado


@router.get("/empleados", response_model=list[EmpleadoSalida])
def listar_empleados(
    busqueda: str | None = None,
    departamento: str | None = None,
    db: Session = Depends(obtener_db),
):
    consulta = db.query(Empleado)

    if busqueda:
        patron = f"%{busqueda.lower()}%"
        consulta = consulta.filter(
            or_(
                func.lower(Empleado.nombre).like(patron),
                func.lower(Empleado.correo).like(patron),
            )
        )

    if departamento in DEPARTAMENTOS:
        consulta = consulta.filter(Empleado.departamento == departamento)

    return consulta.order_by(Empleado.id.asc()).all()


@router.get("/departamentos")
def obtener_departamentos():
    return DEPARTAMENTOS


@router.put("/empleados/{id}", response_model=EmpleadoSalida)
def actualizar_empleado(
    id: int, datos: EmpleadoActualizar, db: Session = Depends(obtener_db)
):
    empleado = obtener_empleado_o_404(db, id)
    if empleado.estado == "baja":
        raise HTTPException(
            status_code=409,
            detail="No se puede editar a un empleado dado de baja",
        )

    if datos.nombre is not None:
        empleado.nombre = datos.nombre
    if datos.puesto is not None:
        empleado.puesto = datos.puesto
    if datos.departamento is not None:
        empleado.departamento = datos.departamento

    db.commit()
    db.refresh(empleado)
    return empleado


@router.post("/empleados/{id}/baja", response_model=EmpleadoSalida)
def dar_baja_empleado(id: int, datos: EmpleadoBaja, db: Session = Depends(obtener_db)):
    empleado = obtener_empleado_o_404(db, id)
    if datos.fecha_baja < empleado.fecha_ingreso:
        raise HTTPException(
            status_code=422,
            detail="La fecha de baja no puede ser anterior a la fecha de ingreso",
        )

    empleado.estado = "baja"
    empleado.fecha_baja = datos.fecha_baja

    db.commit()
    db.refresh(empleado)
    return empleado
