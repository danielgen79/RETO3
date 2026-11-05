# Reporte · HU-01

**Estado:** LISTA
**Costo de agentes:** 1.57 USD
**Ciclos de corrección:** 0

## Bitácora
- Filtro de historia: OK
- Criterios escritos en criterios.feature
- Preguntas abiertas: la persona respondió 'si'
- Casos de prueba escritos en casos_prueba.json
- Plan rechazado: Buen plan, ajusta 4 cosas: 1) Incluye GET /api/salud que responda {"estado": "ok"}. 2) Organiza el backend en módulos: database.py, models.py, schemas.py y un router por recurso (routers/empleados.py), para que historias futuras como vacaciones agreguen su propio router sin reescribir main.py. 3) Copia letra por letra los mensajes de reglas_negocio.md para correo duplicado (409), correo no corporativo (422) y fecha de ingreso futura (422). 4) Sí incluye un GET /api/empleados sencillo, sin filtros.
- Plan rechazado: Casi listo, se perdieron 2 cosas del plan anterior: 1) Incluye GET /api/departamentos que devuelva el catálogo, como pide convenciones_app.md, y que el select del formulario lo use. 2) Valida que el departamento esté en el catálogo y responda 422 si no. Conserva también el proxy de /api hacia localhost:8000 en vite.config.js.
- Plan aprobado por una persona
- Construcción 1
- Verificación: OK
- Pruebas automatizadas: OK (10 casos)
- Despliegue: OK
- Despliegue y pruebas listos
- Pruebas E2E: 10 passed, 1 warning in 19.99s

## Última ejecución de pruebas
```
10 passed, 1 warning in 19.99s

```