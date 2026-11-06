# language: es
Característica: Solicitar vacaciones
  Como empleado de la empresa
  Quiero solicitar días de vacaciones indicando una fecha de inicio y una de fin
  Para que mi solicitud quede registrada y sepa cuántos días me quedan en el año

  Escenario: Camino feliz - una solicitud válida se registra y descuenta los días hábiles
    Dado un empleado activo con id 7, fecha_ingreso "2023-01-10" y 0 días usados en el año 2026
    Cuando solicita vacaciones con fecha_inicio "2026-07-06" y fecha_fin "2026-07-10"
    Entonces la API responde 201
    Y el campo "dias_habiles" de la respuesta es 5
    Y el campo "dias_restantes" de la respuesta es 7
    Y en la pantalla el elemento "vacaciones-mensaje" muestra "Solicitud registrada: 5 días hábiles. Te quedan 7 días hábiles en 2026."

  Escenario: Camino feliz - consultar el saldo del año refleja los días usados
    Dado un empleado activo con id 7, fecha_ingreso "2023-01-10"
    Y que ya registró una solicitud de vacaciones del "2026-07-06" al "2026-07-10" con 5 días hábiles
    Cuando consulta GET "/api/empleados/7/vacaciones?anio=2026"
    Entonces la API responde 200
    Y el campo "dias_usados" de la respuesta es 5
    Y el campo "dias_disponibles" de la respuesta es 7
    Y la lista "solicitudes" de la respuesta tiene 1 elemento

  Escenario: Límite - el empleado puede solicitar justo el día en que cumple un año de antigüedad
    Dado un empleado activo con id 8, fecha_ingreso "2025-12-21" y 0 días usados en el año 2026
    Cuando solicita vacaciones con fecha_inicio "2026-12-21" y fecha_fin "2026-12-21"
    Entonces la API responde 201
    Y el campo "dias_habiles" de la respuesta es 1
    Y el campo "dias_restantes" de la respuesta es 11

  Escenario: Error Regla 1 - antigüedad insuficiente, le faltan días para cumplir el año
    Dado un empleado activo con id 8, fecha_ingreso "2025-12-21" y 0 días usados en el año 2026
    Cuando solicita vacaciones con fecha_inicio "2026-12-18" y fecha_fin "2026-12-20"
    Entonces la API responde 400
    Y el mensaje de error es "Se requiere al menos un año de antigüedad a la fecha de inicio"
    Y en la pantalla el elemento "vacaciones-mensaje" muestra "Se requiere al menos un año de antigüedad a la fecha de inicio"

  Escenario: Error - el empleado no existe
    Dado que no existe ningún empleado con id 9999
    Cuando solicita vacaciones para el empleado 9999 con fecha_inicio "2026-07-06" y fecha_fin "2026-07-10"
    Entonces la API responde 404
    Y el mensaje de error es "Empleado no encontrado"

  Escenario: Error - el empleado está dado de baja
    Dado un empleado con id 9, estado "baja" y fecha_ingreso "2023-01-10"
    Cuando solicita vacaciones con fecha_inicio "2026-07-06" y fecha_fin "2026-07-10"
    Entonces la API responde 409
    Y el mensaje de error es "No se pueden solicitar vacaciones para un empleado dado de baja"

  Escenario: Error - la fecha de fin es anterior a la fecha de inicio
    Dado un empleado activo con id 7, fecha_ingreso "2023-01-10" y 0 días usados en el año 2026
    Cuando solicita vacaciones con fecha_inicio "2026-07-10" y fecha_fin "2026-07-05"
    Entonces la API responde 400
    Y el mensaje de error es "La fecha de fin no puede ser anterior a la fecha de inicio"

  Escenario: Error - el periodo cruza de un año calendario a otro
    Dado un empleado activo con id 7, fecha_ingreso "2023-01-10" y 0 días usados en el año 2026
    Cuando solicita vacaciones con fecha_inicio "2026-12-28" y fecha_fin "2027-01-08"
    Entonces la API responde 400
    Y el mensaje de error es "Las vacaciones deben estar dentro de un mismo año calendario"

  Escenario: Error - el año de la solicitud no está en la tabla de festivos
    Dado un empleado activo con id 7, fecha_ingreso "2023-01-10" y 0 días usados en el año 2025
    Cuando solicita vacaciones con fecha_inicio "2025-07-06" y fecha_fin "2025-07-10"
    Entonces la API responde 400
    Y el mensaje de error es "Solo se pueden solicitar vacaciones en 2026 y 2027"

  Escenario: Los sábados, domingos y festivos dentro del periodo no se descuentan
    Dado un empleado activo con id 7, fecha_ingreso "2023-01-10" y 0 días usados en el año 2026
    Cuando solicita vacaciones con fecha_inicio "2026-09-14" y fecha_fin "2026-09-18"
    Entonces la API responde 201
    Y el campo "dias_habiles" de la respuesta es 4
    Y el campo "dias_restantes" de la respuesta es 8

  Escenario: Error Regla 3 - un periodo sin ningún día hábil se rechaza
    Dado un empleado activo con id 7, fecha_ingreso "2023-01-10" y 0 días usados en el año 2026
    Cuando solicita vacaciones con fecha_inicio "2026-07-11" y fecha_fin "2026-07-12"
    Entonces la API responde 400
    Y el mensaje de error es "El periodo no incluye días hábiles"

  Escenario: Límite - se puede usar exactamente lo que queda del tope anual
    Dado un empleado activo con id 7, fecha_ingreso "2023-01-10" y 5 días usados en el año 2026
    Cuando solicita vacaciones con fecha_inicio "2026-07-13" y fecha_fin "2026-07-21"
    Entonces la API responde 201
    Y el campo "dias_habiles" de la respuesta es 7
    Y el campo "dias_restantes" de la respuesta es 0

  Escenario: Error Regla 2 - la solicitud rebasa los días disponibles del año
    Dado un empleado activo con id 7, fecha_ingreso "2023-01-10" y 4 días usados en el año 2026
    Cuando solicita vacaciones con fecha_inicio "2026-11-02" y fecha_fin "2026-11-12"
    Entonces la API responde 400
    Y el mensaje de error es "La solicitud excede los días disponibles: quedan 8 días hábiles"

  Escenario: Límite - la solicitud se pasa por un solo día hábil del tope disponible
    Dado un empleado activo con id 7, fecha_ingreso "2023-01-10" y 11 días usados en el año 2026
    Cuando solicita vacaciones con fecha_inicio "2026-10-05" y fecha_fin "2026-10-06"
    Entonces la API responde 400
    Y el mensaje de error es "La solicitud excede los días disponibles: quedan 1 días hábiles"

  Escenario: Límite - el tope anual ya está agotado y cualquier solicitud se rechaza
    Dado un empleado activo con id 7, fecha_ingreso "2023-01-10" y 12 días usados en el año 2026
    Cuando solicita vacaciones con fecha_inicio "2026-08-03" y fecha_fin "2026-08-03"
    Entonces la API responde 400
    Y el mensaje de error es "La solicitud excede los días disponibles: quedan 0 días hábiles"

# Preguntas abiertas
# - No se especifica qué ocurre si la solicitud intenta superponerse con otra ya registrada en fechas que se encimen;
#   el contexto no menciona una regla de solapamiento, así que no se incluyó un escenario para ello.
# - No se especifica el comportamiento exacto de la pantalla cuando el `empleado_id` no existe o está dado de baja
#   (por ejemplo, si el botón "Solicitar vacaciones" se oculta); se documentó solo el comportamiento de la API.
