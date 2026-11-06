"""Sesión 4 · Triage: ante pruebas fallidas, decide qué agente debe corregir.

Es el supervisor del flujo E2E: no corrige nada, solo enruta con una justificación.
"""
import os
from typing import Literal

from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel

from agentes.base import RAIZ, SALIDA


class Diagnostico(BaseModel):
    responsable: Literal["desarrollador", "automatizador", "despliegue"]
    causa: str          # qué falló, en una o dos frases
    criterio: str       # escenario de aceptación que se usa como referencia
    instruccion: str    # qué debe corregir el responsable


PROMPT = """Eres líder técnico. Unas pruebas automatizadas fallaron. Decide quién debe corregir:
- "desarrollador": la aplicación no cumple un criterio de aceptación.
- "automatizador": la prueba contradice el criterio o las reglas, usa un selector incorrecto o es frágil.
- "despliegue": la aplicación no responde (conexión rechazada, 502, contenedor caído).
El criterio de aceptación manda: si la prueba y la aplicación no coinciden, gana quien siga el criterio.
Pero las reglas de negocio mandan sobre los criterios: si un dato esperado del criterio o de la prueba
contradice las reglas (por ejemplo, un conteo de días hábiles que olvida un festivo de la tabla), el error
está en la prueba: el responsable es "automatizador" y la instrucción debe dar el valor correcto según
las reglas. Antes de culpar a la aplicación por un número, recalcúlalo con las reglas.

## Reglas de negocio
{reglas}

## Criterios de aceptación
{criterios}

## Pruebas fallidas
{fallos}"""


def diagnosticar(hu: str, fallos: str) -> Diagnostico:
    llm = ChatAnthropic(model=os.environ["MODEL"], max_tokens=2000)
    criterios = (SALIDA / hu / "criterios.feature").read_text(encoding="utf-8")
    reglas = (RAIZ / "contexto" / "reglas_negocio.md").read_text(encoding="utf-8")
    return llm.with_structured_output(Diagnostico).invoke(
        PROMPT.format(reglas=reglas, criterios=criterios, fallos=fallos[:6000]))
