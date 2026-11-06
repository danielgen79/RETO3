# Decisiones · HU-10 Solicitar vacaciones

La ejecución entregada es el **intento 3**. Los intentos 1 (`auditoria_hu10_intento1.jsonl`) y 2
(`auditoria_hu10_intento2.jsonl`) quedaron en el historial de Git como evidencia de lo que corregí.

## 1. ¿Qué pasos son workflow y cuáles son agente?

**Workflow (decide el código):** el orden de las etapas en `flujo_s4.py`, los reintentos según
`validar_gherkin` y `validar_plan`, `verificar_app`, `verificar_despliegue`, el paso de la app desplegada
a pytest y todos los límites (3 intentos, 2 ciclos, 2 USD por llamada). **Agentes (decide el modelo):**
el analista y el diseñador deciden qué leer, qué escenarios escribir y cuántas veces consultar el
calendario (6 y 7 llamadas en el intento 3); el desarrollador, el despliegue y el automatizador deciden
cómo implementar; el triage decide a quién enrutar. Mi criterio: lo que se puede verificar con código no se
le deja al modelo. Por eso contar días hábiles pasó de ser trabajo del agente a una herramienta
determinista (`agentes/calendario.py`) después del intento 2.

## 2. ¿Cómo se validó cada salida? ¿Qué atrapó un validador?

Criterios: `validar_gherkin` revisa la estructura y que estén los 8 mensajes de error letra por letra.
Atrapó «El escenario 9 no tiene 'Dado'» (intento 1) y «El escenario 11 no tiene 'Dado'» (intento 3);
el segundo intento del analista pasó ambas veces. Casos: Pydantic dentro de `guardar_casos`, más
`validar_plan` (cada escenario cubierto, mensajes exactos, nada de `EMP-0007` en rutas); el lote máximo de
4 casos lo impone el esquema. Código: `/api/salud`, `npm run build`, despliegue y pytest con Playwright: 46 pruebas pasan (HU-01 a
HU-03 y los 13 casos de HU-10), 1 saltada legítima de HU-03, sin ciclos de corrección.
Además corrí mis propias revisiones: `herramientas/verificar_hu10.py` pasa 30 de 30 comprobaciones
(mensajes exactos, orden y límites) y `herramientas/revisar_auditoria.py` confirma que cada archivo
cambiado en `app/` tiene un agente registrado.

## 3. ¿Dónde intervine como persona y qué vi para decidir?

En la aprobación del plan de cada intento rechacé el primero con seis puntos concretos: el 29 de febrero
provocaría un error 500, N del mensaje de cupo es antes de la solicitud y `dias_restantes` después, las
reglas van en la ruta y no en validadores de Pydantic (si no, se pierde el orden de la tabla), el año por
defecto del GET, el mensaje de éxito exacto y refrescar el saldo. El segundo plan los cumplió todos.
Antes, en HU-03, rechacé migrar los data-testid a `numero_empleado` porque rompía HU-02 y las rutas de HU-10.
También reparé la codificación de los archivos de HU-10 («dÃ­as») antes de dárselos a los agentes, y leí
`auditoria.jsonl` del intento 1, donde vi que un agente había detenido el proceso de Docker.

## 4. ¿Qué arquitectura de orquestación y por qué no otra?

Un orquestador con flujo fijo (`StateGraph`), con paralelización (despliegue ∥ automatización), evaluador
con reflexión en el analista y el diseñador, humano en el bucle en el plan y un supervisor acotado (el
triage) solo en el ciclo de corrección. No usé un supervisor LLM general porque el orden de las etapas no
cambia entre historias: añadiría costo y variación sin ganar nada. Tampoco una red o pizarra: los agentes
no negocian, cada uno entrega un artefacto validado al siguiente.

## 5. ¿Qué corregí en el agente y por qué no en su resultado?

| Falla | Evidencia | Corrección en la fábrica |
| --- | --- | --- |
| Docker se caía | Auditoría intento 1: el desarrollador hizo `Stop-Process` sobre el proceso del puerto 8000 | Prueba en el puerto 8011 y solo detiene procesos propios; PowerShell bloqueado (los hooks solo vigilaban Bash) |
| ESCALAR en el intento 2 | Un criterio contaba 4 días del 2 al 5 de feb. de 2026; el 2 es festivo. El triage culpó 2 veces al desarrollador | Herramienta `contar_dias_habiles`; el triage recibe las reglas |
| El diseñador se cortó | `stop_reason=max_tokens` al guardar 25 casos de una vez | Guardado por lotes, con el límite impuesto por el código |

Corregir a mano la prueba CP-15 habría arreglado un archivo, pero el analista habría vuelto a olvidar un
festivo en la siguiente historia, y la auditoría mostraría la edición. Corregir al agente arregla la causa.
