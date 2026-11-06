# Reporte · HU-10

**Estado:** LISTA
**Costo de agentes:** 2.96 USD
**Ciclos de corrección:** 2

## Bitácora
- Filtro de historia: OK
- Criterios escritos en criterios.feature
- Preguntas abiertas: la persona respondió 'si'
- Casos de prueba escritos en casos_prueba.json
- Plan rechazado: Buen plan, consérvalo y precisa 6 cosas: 1) cumple_antiguedad no debe sumar un año con replace a secas: si fecha_ingreso es 29 de febrero y el año siguiente no es bisiesto, el aniversario es el 1 de marzo (si no, un ingreso 2024-02-29 provoca un error 500); la antigüedad se cumple el mismo día del aniversario (>=). 2) En el mensaje de cupo, N son los días que quedan ANTES de esta solicitud (12 menos los usados en ese año) y siempre se escribe 'días hábiles', también con N=1; dias_restantes del 201 son los que quedan DESPUÉS. 3) Las reglas de negocio se validan en la ruta, no con validadores de Pydantic: el esquema solo declara los tipos date, para respetar el 404 y el orden de la tabla, y que un formato inválido dé el 422 automático. 4) En el GET, si no se manda anio se usa el año en curso. 5) El mensaje de éxito en vacaciones-mensaje es exactamente 'Solicitud registrada: N días hábiles. Te quedan M días hábiles en AAAA.' con N = dias_habiles, M = dias_restantes y AAAA el año de la solicitud. 6) Después de una solicitud exitosa, vacaciones-disponibles se actualiza con el nuevo saldo.
- Plan aprobado por una persona
- Construcción 1
- Verificación: OK
- Pruebas automatizadas: OK (23 casos)
- Despliegue: FALLA
- Despliegue y pruebas listos
- Pruebas E2E: 56 failed, 1 skipped, 1 warning in 255.08s (0:04:15)
- Triage → despliegue: Todas las pruebas fallan con httpx.ConnectError (WinError 10061: conexión rechazada), lo que indica que la aplicación/API no está disponible o el servidor/contenedor no está levantado en el entorno de pruebas, no permitiendo establecer conexión en absoluto.
- Despliegue corregido
- Pruebas E2E: 22 failed, 34 passed, 1 skipped, 1 warning in 242.75s (0:04:02)
- Triage → despliegue: Todas las solicitudes a la API devuelven 404 (incluso "Not Found" genérico en vez del cuerpo JSON esperado con mensaje "Empleado no encontrado"), lo que indica que el endpoint/servicio de vacaciones no está desplegado, la ruta no está registrada o el contenedor/servicio backend no está disponible en el entorno de pruebas. Esto también provoca timeouts en los tests E2E, ya que la UI depende de esas respuestas de la API para habilitar o mostrar elementos (p.ej. "vacaciones-abrir-148"), causando que los selectores nunca aparezcan.
- Despliegue corregido
- Pruebas E2E: 56 passed, 1 skipped, 1 warning in 63.44s (0:01:03)

## Última ejecución de pruebas
```
56 passed, 1 skipped, 1 warning in 63.44s (0:01:03)

```