# language: es
# HU-10 · Solicitar vacaciones

Característica: Solicitar vacaciones
  Como empleado de la empresa
  quiero solicitar días de vacaciones indicando una fecha de inicio y una de fin
  para que mi solicitud quede registrada y sepa cuántos días me quedan en el año

  Escenario: Camino feliz - se registra una solicitud válida y un festivo dentro del periodo no se descuenta
    Dado un empleado activo con id 7, número de empleado "EMP-0007", fecha de ingreso "2024-01-10" y 0 días hábiles usados en 2026
    Cuando solicita vacaciones con fecha_inicio "2026-12-21" y fecha_fin "2026-12-31"
    Entonces la respuesta tiene código 201
    Y el campo "dias_habiles" de la respuesta es 8
    Y el campo "dias_restantes" de la respuesta es 4
    Y en la pantalla el elemento "vacaciones-mensaje" muestra "Solicitud registrada: 8 días hábiles. Te quedan 4 días hábiles en 2026."

  Escenario: Límite - se puede usar exactamente los días hábiles que quedan en el año
    Dado un empleado activo con id 8, número de empleado "EMP-0008", fecha de ingreso "2024-01-10" y 5 días hábiles usados en 2026
    Cuando solicita vacaciones con fecha_inicio "2026-07-13" y fecha_fin "2026-07-21"
    Entonces la respuesta tiene código 201
    Y el campo "dias_habiles" de la respuesta es 7
    Y el campo "dias_restantes" de la respuesta es 0
    Y en la pantalla el elemento "vacaciones-mensaje" muestra "Solicitud registrada: 7 días hábiles. Te quedan 0 días hábiles en 2026."

  Escenario: Límite - el empleado puede solicitar vacaciones el mismo día en que cumple exactamente un año de antigüedad
    Dado un empleado activo con id 9, número de empleado "EMP-0009", fecha de ingreso "2025-12-21" y 0 días hábiles usados en 2026
    Cuando solicita vacaciones con fecha_inicio "2026-12-21" y fecha_fin "2026-12-21"
    Entonces la respuesta tiene código 201
    Y el campo "dias_habiles" de la respuesta es 1
    Y el campo "dias_restantes" de la respuesta es 11

  Escenario: Error - el empleado no existe
    Dado que no existe ningún empleado con id 999
    Cuando solicita vacaciones para el empleado 999 con fecha_inicio "2026-07-06" y fecha_fin "2026-07-10"
    Entonces la respuesta tiene código 404
    Y el mensaje de error es "Empleado no encontrado"

  Escenario: Error - el empleado está dado de baja
    Dado un empleado con id 10, número de empleado "EMP-0010", estado "baja" y fecha de ingreso "2024-01-10"
    Cuando solicita vacaciones con fecha_inicio "2026-07-06" y fecha_fin "2026-07-10"
    Entonces la respuesta tiene código 409
    Y el mensaje de error es "No se pueden solicitar vacaciones para un empleado dado de baja"

  Escenario: Error - la fecha de fin es anterior a la fecha de inicio
    Dado un empleado activo con id 11, número de empleado "EMP-0011", fecha de ingreso "2024-01-10" y 0 días hábiles usados en 2026
    Cuando solicita vacaciones con fecha_inicio "2026-07-10" y fecha_fin "2026-07-05"
    Entonces la respuesta tiene código 400
    Y el mensaje de error es "La fecha de fin no puede ser anterior a la fecha de inicio"

  Escenario: Error - el periodo cruza de un año a otro
    Dado un empleado activo con id 12, número de empleado "EMP-0012", fecha de ingreso "2024-01-10" y 0 días hábiles usados en 2026
    Cuando solicita vacaciones con fecha_inicio "2026-12-28" y fecha_fin "2027-01-08"
    Entonces la respuesta tiene código 400
    Y el mensaje de error es "Las vacaciones deben estar dentro de un mismo año calendario"

  Escenario: Error - el año solicitado no está en la tabla de festivos
    Dado un empleado activo con id 13, número de empleado "EMP-0013", fecha de ingreso "2024-01-10" y 0 días hábiles usados en 2028
    Cuando solicita vacaciones con fecha_inicio "2028-01-10" y fecha_fin "2028-01-14"
    Entonces la respuesta tiene código 400
    Y el mensaje de error es "Solo se pueden solicitar vacaciones en 2026 y 2027"

  Escenario: Error - antigüedad insuficiente a la fecha de inicio
    Dado un empleado activo con id 14, número de empleado "EMP-0014", fecha de ingreso "2025-12-21" y 0 días hábiles usados en 2026
    Cuando solicita vacaciones con fecha_inicio "2026-12-18" y fecha_fin "2026-12-18"
    Entonces la respuesta tiene código 400
    Y el mensaje de error es "Se requiere al menos un año de antigüedad a la fecha de inicio"

  Escenario: Error - el periodo no incluye ningún día hábil
    Dado un empleado activo con id 15, número de empleado "EMP-0015", fecha de ingreso "2024-01-10" y 0 días hábiles usados en 2026
    Cuando solicita vacaciones con fecha_inicio "2026-07-11" y fecha_fin "2026-07-12"
    Entonces la respuesta tiene código 400
    Y el mensaje de error es "El periodo no incluye días hábiles"

  Escenario: Error - la solicitud rebasa los días disponibles por un día
    Dado un empleado activo con id 16, número de empleado "EMP-0016", fecha de ingreso "2024-01-10" y 4 días hábiles usados en 2026
    Cuando solicita vacaciones con fecha_inicio "2026-08-03" y fecha_fin "2026-08-13"
    Entonces la respuesta tiene código 400
    Y el mensaje de error es "La solicitud excede los días disponibles: quedan 8 días hábiles"

  Escenario: Error - el tope anual ya está agotado
    Dado un empleado activo con id 17, número de empleado "EMP-0017", fecha de ingreso "2024-01-10" y 12 días hábiles usados en 2026
    Cuando solicita vacaciones con fecha_inicio "2026-09-14" y fecha_fin "2026-09-18"
    Entonces la respuesta tiene código 400
    Y el mensaje de error es "La solicitud excede los días disponibles: quedan 0 días hábiles"
