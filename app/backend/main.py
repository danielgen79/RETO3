"""Punto de entrada de la API de gestión de empleados."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import modelos  # noqa: F401 registra el modelo Empleado en Base.metadata
from database import Base, engine
from rutas_empleados import router as router_empleados

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router_empleados, prefix="/api")


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(request: Request, exc: RequestValidationError):
    primer_error = exc.errors()[0]
    mensaje = str(primer_error["msg"])
    if mensaje.startswith("Value error, "):
        mensaje = mensaje[len("Value error, ") :]
    return JSONResponse(status_code=422, content={"detail": mensaje})


@app.get("/api/salud")
def salud():
    return {"estado": "ok"}
