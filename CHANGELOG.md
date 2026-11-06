# Changelog

Cambios relevantes de la fábrica de agentes durante el Reto 3 (HU-10 · Solicitar vacaciones).
Formato: versión · fecha · resumen. Cada cambio corrige a un **agente** (instrucciones, contexto,
herramientas, validadores o permisos), nunca su resultado en `app/` o `salida/`.

## [2.3.1] · 2026-11-05
- **disenador_pruebas.py:** el lote máximo de `guardar_casos` (4 casos) se impone en el esquema
  (`maxItems`) y en la función, no solo en la instrucción. En el intento 3 el diseñador volvió a
  rebasar `max_tokens` al intentar guardar demasiados casos de una vez.
- **.gitignore:** se ignoran los `*.log` (un log del servidor de prueba se había colado en un commit).

## [2.3.0] · 2026-11-05
- **calendario.py (nuevo):** herramienta determinista `contar_dias_habiles` que lee la tabla de
  festivos de `contexto/reglas_vacaciones.md`. El analista y el diseñador la usan en lugar de contar
  de memoria. Motivo: en el intento 2 un criterio contaba 4 días hábiles del 2 al 5 de febrero de
  2026 olvidando el festivo del día 2, y el error se propagó hasta las pruebas.
- **triage.py:** recibe las reglas de negocio; si un dato esperado contradice las reglas, el
  responsable es el automatizador. En el intento 2 culpó dos veces al desarrollador.

## [2.2.0] · 2026-11-05
- **claude_code.py:** `PowerShell` en `disallowed_tools`. La auditoría del intento 1 mostró que los
  agentes lo usaban para detener procesos y abrir programas sin pasar por el hook
  `comandos_permitidos`, que solo vigila `Bash`.
- **desarrollador.py:** prueba su backend en el puerto 8011 y solo detiene procesos propios.
  En el intento 1 detuvo el proceso de Docker que ocupaba el puerto 8000 y tumbó los contenedores.

## [2.1.0] · 2026-11-05
- **disenador_pruebas.py:** `guardar_casos` guarda por lotes y acumula (un id repetido reemplaza al
  anterior); hasta 25 pasos. El diseñador rebasó `max_tokens` al guardar 25 casos en una sola llamada.

## [2.0.0] · 2026-11-05 · Preparación para HU-10
- **contexto/:** historia, reglas y convenciones de vacaciones agregadas. Los archivos venían con
  doble codificación («dÃ­as»); se repararon antes de dárselos a los agentes.
- **analista.py:** lee también `convenciones_app.md`; un escenario por fila de la tabla de errores;
  el validador exige los 8 mensajes exactos letra por letra; hasta 3 intentos.
- **disenador_pruebas.py:** plantillas con `{id}` en rutas y data-testid (nunca números de ejemplo),
  un empleado por caso, validación de mensajes exactos; hasta 3 intentos.
- **desarrollador.py:** las convenciones de cada historia mandan sobre las generales (400 en lugar
  de 422), orden de validación exacto, sin reglas inventadas, cálculos en el backend.
- **automatizador.py:** un empleado nuevo por prueba con su `fecha_ingreso`; comparación exacta (`==`).
- **.gitignore:** `auditoria.jsonl` ya no se ignora (es evidencia de la entrega).

## [1.2.0] · 2026-11-05
- **automatizador.py:** prohibido `pytest.skip`/`xfail`; las precondiciones se preparan por la API.
  En HU-02 cuatro pruebas se saltaban para siempre y ocultaban la funcionalidad de baja.

## [1.1.0] · 2026-11-05
- **flujo_s2.py:** al rechazar un plan, los comentarios se acumulan y el desarrollador recibe su plan
  anterior. En HU-01 cada plan rehecho olvidaba correcciones previas.
- **verificacion.py:** `_correr` usa `shutil.which` para encontrar `npm.cmd` en Windows, y la salida
  de npm y pytest se lee en UTF-8.

## [1.0.0] · 2026-11-05
- Punto de partida: fábrica de seis agentes del Lab 4. HU-01 a HU-03 generadas por la fábrica.

## Herramientas de revisión (fuera de la fábrica)
- **herramientas/verificar_hu10.py:** 30 comprobaciones de HU-10 contra la API desplegada.
- **herramientas/revisar_auditoria.py:** cruza `auditoria.jsonl` con los cambios de Git en `app/`.
