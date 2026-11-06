"""Sesión 1 · Agente 1, analista: historia de usuario -> criterios de aceptación en Gherkin.

Uso:  python -m agentes.analista historias/HU-01-registrar-empleado.md
"""
import re
import sys
from pathlib import Path

from agentes.base import RAIZ, SALIDA, ejecutar_agente, herramientas_archivos, hu_de, rel

SISTEMA = """Eres analista de producto en un equipo de software. Conviertes historias de usuario
en criterios de aceptación escritos en Gherkin, en español.

Cómo trabajas:
1. Lee la historia, contexto/reglas_negocio.md y contexto/convenciones_app.md (ahí están la API,
   los códigos de respuesta, los mensajes de error y los data-testid).
2. Escribe {destino}. La primera línea es `# language: es` y usas las palabras clave
   Característica, Escenario, Dado, Cuando, Entonces, Y.
3. Incluye el camino feliz y un escenario de error por cada regla de negocio que aplique a ESTA historia.
   Si el contexto trae una tabla de errores para esta historia, escribe un escenario por cada fila,
   con su código de respuesta y su mensaje copiado letra por letra, entre comillas dobles.
   Donde el mensaje lleva un número variable (por ejemplo N), escribe el número concreto del escenario.
4. Incluye los casos límite que el contexto menciona (por ejemplo, usar exactamente lo que queda,
   pasarse por uno, el primer día en que se cumple una condición).
5. Cada escenario se puede verificar desde la pantalla o la API: datos concretos, nada de «funciona bien».
6. No inventes reglas. Si falta información, agrégala al final como comentarios bajo `# Preguntas abiertas`.
7. Responde al final con una sola línea: cuántos escenarios escribiste."""

# Historias cuyas convenciones traen una tabla de errores con mensajes exactos.
# Los criterios deben citar cada mensaje letra por letra: la API se califica con pruebas automáticas.
FUENTE_MENSAJES = {"HU-10": RAIZ / "contexto" / "convenciones_vacaciones.md"}


def mensajes_exactos(hu: str) -> list[str]:
    """Lee las filas `| caso | código | `mensaje` |` del archivo de convenciones de la historia."""
    fuente = FUENTE_MENSAJES.get(hu)
    if fuente is None or not fuente.exists():
        return []
    texto = fuente.read_text(encoding="utf-8")
    return re.findall(r"^\|[^|\n]+\|\s*\d{3}\s*\|\s*`([^`]+)`\s*\|", texto, flags=re.MULTILINE)


def escenarios(gherkin: str) -> list[str]:
    return re.findall(r"^\s*Escenario:\s*(.+?)\s*$", gherkin, flags=re.MULTILINE)


def preguntas_abiertas(gherkin: str) -> list[str]:
    if "# Preguntas abiertas" not in gherkin:
        return []
    bloque = gherkin.split("# Preguntas abiertas", 1)[1]
    return [l.lstrip("# -").strip() for l in bloque.splitlines() if l.strip().lstrip("#").strip()]


def validar_gherkin(texto: str, mensajes: list[str] | None = None) -> list[str]:
    """Evaluador determinista: devuelve los problemas encontrados; vacío = válido.

    Si se pasan `mensajes`, cada uno debe aparecer letra por letra en los criterios
    (un « N » del mensaje acepta un número concreto, por ejemplo «quedan 4 días hábiles»).
    """
    problemas = []
    if not texto.lstrip().startswith("# language: es"):
        problemas.append("La primera línea debe ser '# language: es'.")
    if "Característica:" not in texto:
        problemas.append("Falta 'Característica:'.")
    bloques = re.split(r"^\s*Escenario:", texto, flags=re.MULTILINE)[1:]
    if len(bloques) < 2:
        problemas.append("Se esperan al menos 2 escenarios (camino feliz y un error).")
    for i, bloque in enumerate(bloques, 1):
        for clave in ("Dado", "Cuando", "Entonces"):
            if not re.search(rf"^\s*{clave}\b", bloque, flags=re.MULTILINE):
                problemas.append(f"El escenario {i} no tiene '{clave}'.")
    for mensaje in mensajes or []:
        patron = r" (?:N|\d+) ".join(re.escape(parte) for parte in mensaje.split(" N "))
        if not re.search(patron, texto):
            problemas.append(f"Falta un escenario con el mensaje exacto, letra por letra: «{mensaje}».")
    return problemas


def generar_criterios(historia: Path, max_intentos: int = 3) -> Path:
    hu = hu_de(historia)
    carpeta = SALIDA / hu
    destino = carpeta / "criterios.feature"
    mensajes = mensajes_exactos(hu)
    herramientas = herramientas_archivos(lectura=[RAIZ / "historias", RAIZ / "contexto"], escritura=carpeta)
    tarea = f"Historia de usuario: {rel(historia)}"
    for intento in range(1, max_intentos + 1):
        print(f"Analista · intento {intento}")
        ejecutar_agente(SISTEMA.format(destino=rel(destino)), herramientas, tarea, nombre="analista")
        problemas = validar_gherkin(destino.read_text(encoding="utf-8"), mensajes) if destino.exists() \
            else [f"No se escribió {rel(destino)}."]
        if not problemas:
            return destino
        print("  Validador de Gherkin:\n  - " + "\n  - ".join(problemas))
        # Reflexión guiada por un evaluador determinista: el agente recibe los problemas y corrige
        tarea += "\n\nTu versión anterior tiene estos problemas; corrígelos:\n- " + "\n- ".join(problemas)
    raise ValueError("Criterios inválidos tras varios intentos:\n- " + "\n- ".join(problemas))


if __name__ == "__main__":
    ruta = generar_criterios(Path(sys.argv[1]).resolve())
    texto = ruta.read_text(encoding="utf-8")
    print(f"\nListo: {rel(ruta)} · {len(escenarios(texto))} escenarios")
    for p in preguntas_abiertas(texto):
        print("  Pregunta abierta:", p)
