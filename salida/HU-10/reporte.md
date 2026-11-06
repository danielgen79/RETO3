# Reporte · HU-10

**Estado:** ESCALAR A UNA PERSONA
**Costo de agentes:** 2.07 USD
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
- Pruebas automatizadas: OK (17 casos)
- Despliegue: OK
- Despliegue y pruebas listos
- Pruebas E2E: 1 failed, 49 passed, 1 skipped, 1 warning in 52.51s
- Triage → desarrollador: El escenario "Error Regla 2 - la solicitud rebasa los días disponibles del año" indica que con 4 días usados y una solicitud del 2026-11-02 al 2026-11-12 (8 días hábiles calculados sin fines de semana ni festivos), el mensaje debe indicar "quedan 8 días hábiles" (12 - 4 = 8). El resultado del test (assert 3 == 4) sugiere que el cálculo de días hábiles disponibles o usados que la API está devolviendo no coincide con el valor esperado por el criterio de aceptación, indicando un error en la lógica de cálculo de días hábiles/restantes en el backend.
- Código corregido; redespliegue OK
- Pruebas E2E: 1 failed, 49 passed, 1 skipped, 1 warning in 51.93s
- Triage → desarrollador: El criterio "Error Regla 2 - la solicitud rebasa los días disponibles del año" indica que con 4 días usados y solicitud del 2026-11-02 al 2026-11-12, deben quedar 8 días hábiles disponibles (12 - 4 = 8). La API está devolviendo un valor distinto al esperado en el cálculo de días hábiles restantes (assert 3 == 4), lo que indica que el cálculo de días hábiles en el periodo o el descuento de días usados/disponibles en la aplicación no coincide con la regla de negocio definida en el criterio de aceptación.
- Código corregido; redespliegue OK
- Pruebas E2E: 1 failed, 49 passed, 1 skipped, 1 warning in 54.23s

## Última ejecución de pruebas
```
1 failed, 49 passed, 1 skipped, 1 warning in 54.23s
- tests.api.test_hu_10::test_cp_15_rebasa_dias_disponibles
  assert 3 == 4
```