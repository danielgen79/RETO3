# language: es
# HU-10 · Solicitar vacaciones

Característica: Solicitar vacaciones
  Como empleado de la empresa
  Quiero solicitar días de vacaciones indicando una fecha de inicio y una de fin
  Para que mi solicitud quede registrada y sepa cuántos días me quedan en el año

  # --- Camino feliz ---

  Escenario: Registrar una solicitud válida descuenta los días hábiles y calcula el saldo restante
    Dado que existe un empleado activo con id 7, fecha de ingreso "2020-01-01" y 0 días hábiles usados en 2026
    Cuando solicita vacaciones del "2026-07-06" al "2026-07-10"
    Entonces la respuesta tiene código 201
    Y el campo "dias_habiles" de la respuesta es 5
    Y el campo "dias_restantes" de la respuesta es 7
    Y en "vacaciones-mensaje" se muestra "Solicitud registrada: 5 días hábiles. Te quedan 7 días hábiles en 2026."

  # --- Regla 3: días hábiles ---

  Escenario: Los sábados, domingos y festivos dentro del periodo no se descuentan
    Dado que existe un empleado activo con id 8, fecha de ingreso "2020-01-01" y 0 días hábiles usados en 2026
    Cuando solicita vacaciones del "2026-12-21" al "2026-12-31"
    Entonces la respuesta tiene código 201
    Y el campo "dias_habiles" de la respuesta es 8
    Y el campo "dias_restantes" de la respuesta es 4

  Escenario: Un periodo compuesto solo por fin de semana no tiene días hábiles y se rechaza
    Dado que existe un empleado activo con id 9, fecha de ingreso "2020-01-01" y 0 días hábiles usados en 2026
    Cuando solicita vacaciones del "2026-07-11" al "2026-07-12"
    Entonces la respuesta tiene código 400
    Y el mensaje de error es "El periodo no incluye días hábiles"
    Y en "vacaciones-mensaje" se muestra "El periodo no incluye días hábiles"

  # --- Regla 2: tope anual ---

  Escenario: Usar exactamente los días que quedan en el año se acepta
    Dado que existe un empleado activo con id 10, fecha de ingreso "2020-01-01" y 5 días hábiles usados en 2026
    Cuando solicita vacaciones del "2026-07-13" al "2026-07-21"
    Entonces la respuesta tiene código 201
    Y el campo "dias_habiles" de la respuesta es 7
    Y el campo "dias_restantes" de la respuesta es 0

  Escenario: Pasarse por un día del saldo disponible se rechaza
    Dado que existe un empleado activo con id 11, fecha de ingreso "2020-01-01" y 4 días hábiles usados en 2026
    Cuando solicita vacaciones del "2026-08-10" al "2026-08-20"
    Entonces la respuesta tiene código 400
    Y el mensaje de error es "La solicitud excede los días disponibles: quedan 8 días hábiles"
    Y en "vacaciones-mensaje" se muestra "La solicitud excede los días disponibles: quedan 8 días hábiles"

  Escenario: Con el tope anual agotado se rechaza cualquier solicitud nueva
    Dado que existe un empleado activo con id 12, fecha de ingreso "2020-01-01" y 12 días hábiles usados en 2026
    Cuando solicita vacaciones del "2026-03-02" al "2026-03-02"
    Entonces la respuesta tiene código 400
    Y el mensaje de error es "La solicitud excede los días disponibles: quedan 0 días hábiles"

  # --- Regla 1: antigüedad ---

  Escenario: Cumplir exactamente un año de antigüedad el día de inicio se acepta
    Dado que existe un empleado activo con id 13, fecha de ingreso "2025-12-21" y 0 días hábiles usados en 2026
    Cuando solicita vacaciones del "2026-12-21" al "2026-12-21"
    Entonces la respuesta tiene código 201
    Y el campo "dias_habiles" de la respuesta es 1
    Y el campo "dias_restantes" de la respuesta es 11

  Escenario: Menos de un año de antigüedad se rechaza
    Dado que existe un empleado activo con id 14, fecha de ingreso "2025-12-21" y 0 días hábiles usados en 2026
    Cuando solicita vacaciones del "2026-12-18" al "2026-12-18"
    Entonces la respuesta tiene código 400
    Y el mensaje de error es "Se requiere al menos un año de antigüedad a la fecha de inicio"
    Y en "vacaciones-mensaje" se muestra "Se requiere al menos un año de antigüedad a la fecha de inicio"

  # --- Validaciones de fechas ---

  Escenario: Una fecha de fin anterior a la de inicio se rechaza
    Dado que existe un empleado activo con id 15, fecha de ingreso "2020-01-01" y 0 días hábiles usados en 2026
    Cuando solicita vacaciones del "2026-07-10" al "2026-07-05"
    Entonces la respuesta tiene código 400
    Y el mensaje de error es "La fecha de fin no puede ser anterior a la fecha de inicio"
    Y en "vacaciones-mensaje" se muestra "La fecha de fin no puede ser anterior a la fecha de inicio"

  Escenario: Un periodo que cruza de un año a otro se rechaza
    Dado que existe un empleado activo con id 16, fecha de ingreso "2020-01-01" y 0 días hábiles usados en 2026
    Cuando solicita vacaciones del "2026-12-28" al "2027-01-08"
    Entonces la respuesta tiene código 400
    Y el mensaje de error es "Las vacaciones deben estar dentro de un mismo año calendario"
    Y en "vacaciones-mensaje" se muestra "Las vacaciones deben estar dentro de un mismo año calendario"

  Escenario: Un año fuera del rango soportado se rechaza
    Dado que existe un empleado activo con id 17, fecha de ingreso "2020-01-01" y 0 días hábiles usados en 2028
    Cuando solicita vacaciones del "2028-01-10" al "2028-01-14"
    Entonces la respuesta tiene código 400
    Y el mensaje de error es "Solo se pueden solicitar vacaciones en 2026 y 2027"
    Y en "vacaciones-mensaje" se muestra "Solo se pueden solicitar vacaciones en 2026 y 2027"

  # --- Validaciones del empleado ---

  Escenario: Un empleado que no existe se rechaza
    Dado que no existe ningún empleado con id 9999
    Cuando solicita vacaciones del "2026-07-06" al "2026-07-10" para el empleado 9999
    Entonces la respuesta tiene código 404
    Y el mensaje de error es "Empleado no encontrado"

  Escenario: Un empleado dado de baja no puede solicitar vacaciones
    Dado que existe un empleado con id 18, estado "baja" y fecha de ingreso "2020-01-01"
    Cuando solicita vacaciones del "2026-07-06" al "2026-07-10"
    Entonces la respuesta tiene código 409
    Y el mensaje de error es "No se pueden solicitar vacaciones para un empleado dado de baja"
    Y en "vacaciones-mensaje" se muestra "No se pueden solicitar vacaciones para un empleado dado de baja"

  # --- Consulta de saldo ---

  Escenario: Consultar el saldo del año refleja los días usados y disponibles
    Dado que existe un empleado activo con id 19, fecha de ingreso "2020-01-01" y 0 días hábiles usados en 2026
    Y el empleado solicitó vacaciones del "2026-07-06" al "2026-07-10"
    Cuando consulta su saldo de vacaciones del año 2026
    Entonces la respuesta tiene código 200
    Y el campo "dias_usados" de la respuesta es 5
    Y el campo "dias_disponibles" de la respuesta es 7
    Y la lista "solicitudes" de la respuesta tiene 1 elemento
    Y en "vacaciones-disponibles" se muestra 7

# Preguntas abiertas
# - El caso límite de antigüedad para una fecha de ingreso 29 de febrero (reglas_negocio.md,
#   regla 1) no se pudo plasmar como escenario ejecutable: para probar el aniversario exacto
#   (29 feb -> 1 marzo en año no bisiesto) la fecha de inicio tendría que caer en un año fuera
#   de 2026-2027, el único rango que la API acepta según convenciones_vacaciones.md. Falta
#   definir si el soporte de festivos se ampliará a otros años para poder cubrir este caso.
