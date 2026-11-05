"""Configuración de la base de datos SQLite con SQLAlchemy 2."""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

CARPETA_DATOS = Path(__file__).resolve().parent / "datos"
CARPETA_DATOS.mkdir(exist_ok=True)

URL_BASE_DATOS = f"sqlite:///{CARPETA_DATOS / 'empleados.db'}"

engine = create_engine(
    URL_BASE_DATOS, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def obtener_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
