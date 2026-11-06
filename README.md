# Fábrica de software con agentes · Módulo 3

Una cadena de seis agentes orquestada con **LangGraph** que convierte una historia de usuario en una
aplicación de gestión de empleados **desplegada en Docker y probada de punta a punta**. En el Reto 3
la fábrica implementó **HU-10 · Solicitar vacaciones** sobre la app de HU-01 a HU-03.

| # | Agente | Rol en el reto | Entrada | Salida |
| --- | --- | --- | --- | --- |
| 1 | Analista | Planificador (requisitos) | Historia + `contexto/` | `salida/HU-xx/criterios.feature` |
| 2 | Diseñador de pruebas | Planificador (pruebas) | Criterios | `salida/HU-xx/casos_prueba.json` |
| 3 | Desarrollador (Claude Code) | Codificador | Criterios, casos, plan aprobado | `app/backend`, `app/frontend` |
| 4 | Despliegue (Claude Code) | Codificador (infraestructura) | Código | Contenedores con Docker Compose |
| 5 | Automatizador (Claude Code) | Tester | Casos de prueba | `app/tests` (pytest + Playwright) |
| 6 | Triage | Reviewer / supervisor | Pruebas fallidas + reglas + criterios | A quién corregir y por qué |

Además, un **filtro de seguridad** revisa cada historia antes de que la lea ningún agente, y una
persona aprueba o rechaza el plan del desarrollador (human-in-the-loop).

## Arquitectura

Es un **orquestador con flujo fijo** (`flujos/flujo_s4.py`): el orden de las etapas no cambia entre
historias, así que un supervisor LLM añadiría costo y variación sin ganar nada. El único punto donde
un LLM decide la ruta es el triage, y solo entre tres responsables posibles.

```
filtrar_historia → analizar → (pedir_aclaracion) → disenar_casos → planificar → aprobar_plan ⟲
   → construir → verificar ⟲ → [desplegar ∥ automatizar] → pruebas_e2e → triage ⟲ → reporte
```

- **Estado tipado** (`TypedDict`) compartido por todos los nodos; `costo_usd` y `bitacora` usan
  reductores que suman lo que aporta cada nodo.
- **Checkpointer** (`InMemorySaver`) con `thread_id` por historia: permite las pausas con `interrupt`.
- **Human-in-the-loop:** preguntas abiertas del analista y aprobación del plan.
- **Paralelización:** despliegue y automatización corren a la vez y se unen en `listo`.
- **Verificaciones deterministas:** el código, no el agente, decide si un paso terminó bien
  (validador de Gherkin, validador de casos, `/api/salud`, `npm run build`, pytest).
- **Límites en todo bucle:** intentos por agente, 2 ciclos de corrección, presupuesto en USD.

## Requisitos

Python 3.12, Node 20 o superior, Docker Desktop, Claude Code y una clave de API de Anthropic con créditos.

## Instalación

**Mac / Linux**
```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env        # escribe ANTHROPIC_API_KEY y MODEL
```

**Windows (CMD)**
```cmd
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
copy .env.example .env
notepad .env
```

## Uso

Abre Docker Desktop y, con el entorno virtual activo, desde la raíz:

```bash
python -m flujos.flujo_s4 historias/HU-10-solicitar-vacaciones.md
```

La terminal se detiene en dos momentos:

1. **Preguntas abiertas** del analista: `si` para continuar; cualquier otra cosa detiene el flujo.
2. **Aprobación del plan:** `si` lo aprueba; cualquier otro texto es un comentario de rechazo y el
   desarrollador rehace el plan con todos los comentarios acumulados. Escribe el comentario en
   **una sola línea**. Ejemplo real de este reto:

   ```
   Buen plan, consérvalo y precisa 6 cosas: 1) cumple_antiguedad no debe sumar un año con replace a secas ...
   ```

Al terminar, `salida/HU-xx/reporte.md` dice **LISTA** o **ESCALAR A UNA PERSONA** con la bitácora
completa. La app queda en http://localhost:8080 y la documentación de la API en http://localhost:8000/docs.

### Ejemplo: probar HU-10 a mano

```bash
curl -X POST http://localhost:8000/api/empleados/1/vacaciones \
     -H "Content-Type: application/json" \
     -d '{"fecha_inicio": "2026-12-21", "fecha_fin": "2026-12-31"}'
# 201 · {"dias_habiles": 8, "dias_restantes": 4, ...}   (el 25 de diciembre es festivo)
```

### Revisar el resultado por tu cuenta

```bash
python herramientas/verificar_hu10.py      # 30 comprobaciones de reglas, mensajes exactos y orden
python herramientas/revisar_auditoria.py   # cada archivo cambiado en app/ tiene un agente registrado
```

## Seguridad

| Medida | Dónde |
| --- | --- |
| Validación de inputs: la historia es contenido no confiable y un filtro LLM la bloquea si trae instrucciones para la IA | `flujo_s4.filtrar_historia` |
| Prompt hardening: la historia va entre etiquetas `<historia_no_confiable>` con la orden de analizar, no obedecer | `flujo_s4.filtrar_historia` |
| Validación de outputs: validadores deterministas de Gherkin y casos (incluidos los mensajes exactos), build, salud y pruebas | `agentes/analista.py`, `agentes/disenador_pruebas.py`, `flujos/verificacion.py` |
| Sandboxing: cada agente escribe solo en sus carpetas, lee solo dentro de `app/`, nunca archivos con secretos, solo usa programas permitidos; sin WebFetch, WebSearch ni PowerShell | `seguridad/hooks.py`, `agentes/claude_code.py` |
| Logging de seguridad: cada herramienta que usa un agente queda en `auditoria.jsonl` | `seguridad/hooks.auditar` |

`DEFENSAS=0` apaga los hooks de seguridad y solo se usa en clase para demostrar el ataque de
`historias/HU-99-envenenada.md`. Nunca se usó en el reto.

## Problemas comunes

- **`FileNotFoundError` con npm en Windows:** ya resuelto en `verificacion.py` (`shutil.which`).
- **Docker se cae durante una ejecución:** algo detuvo el proceso que ocupa el puerto 8000; el
  desarrollador ahora prueba en el 8011.
- **Acentos raros («dÃ­as») en el contexto:** el archivo tiene doble codificación; repáralo antes de
  ejecutar, porque los mensajes de error deben ser exactos.
- **`max_tokens` en el diseñador:** guarda por lotes de máximo 4 casos (impuesto por el código).

## Estructura

- `historias/`: historias de usuario de entrada (HU-99 es la historia envenenada).
- `contexto/`: reglas de negocio y convenciones que leen todos los agentes.
- `agentes/`: los seis agentes, la herramienta de calendario y el puente con Claude Code.
- `flujos/`: el orquestador LangGraph (una versión por sesión) y las verificaciones deterministas.
- `seguridad/hooks.py`: hooks de rol y de seguridad.
- `herramientas/`: revisiones independientes del resultado (no forman parte de la fábrica).
- `app/`: la aplicación que generan los agentes. `salida/`: artefactos por historia.
- `CHANGELOG.md`: cambios de la fábrica durante el reto.
