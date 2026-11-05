"""Rutas del recurso /api/empleados y /api/departamentos."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from catalogo import DEPARTAMENTOS
from database import obtener_db
from esquemas import EmpleadoCrear, EmpleadoSalida
from modelos import Empleado

router = APIRouter()


def generar_numero_empleado(db: Session) -> str:
    total = db.query(func.count(Empleado.id)).scalar() or 0
    return f"EMP-{total + 1:04d}"


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


@router.get("/departamentos")
def obtener_departamentos():
    return DEPARTAMENTOS
