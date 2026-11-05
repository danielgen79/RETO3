# language: es
Característica: Editar y dar de baja a un empleado
  Como persona del área de Recursos Humanos
  quiero cambiar el puesto y el departamento de un empleado, y poder darlo de baja
  para mantener el directorio al día sin perder el historial

  Escenario: Editar puesto y departamento de un empleado activo
    Dado que existe el empleado "EMP-0007" con nombre "Laura Gómez", correo "laura.gomez@empresa.com", puesto "Analista Jr", departamento "Ventas" y estado "activo"
    Cuando edito al empleado "EMP-0007" con puesto "Analista Senior" y departamento "Tecnología"
    Entonces el sistema responde 200
    Y el empleado "EMP-0007" queda con puesto "Analista Senior" y departamento "Tecnología"
    Y el número de empleado sigue siendo "EMP-0007"
    Y el correo sigue siendo "laura.gomez@empresa.com"

  Escenario: Dar de baja a un empleado activo
    Dado que existe el empleado "EMP-0007" con fecha_ingreso "2022-05-10" y estado "activo"
    Cuando doy de baja al empleado "EMP-0007" con fecha_baja "2024-03-01"
    Entonces el sistema responde 200
    Y el empleado "EMP-0007" queda con estado "baja" y fecha_baja "2024-03-01"
    Y el empleado "EMP-0007" sigue apareciendo en el directorio

  Escenario: No se puede editar a un empleado dado de baja
    Dado que existe el empleado "EMP-0008" con estado "baja"
    Cuando edito al empleado "EMP-0008" con puesto "Analista Senior"
    Entonces el sistema responde 409
    Y el mensaje es "No se puede editar a un empleado dado de baja"

  Escenario: Error al editar con un puesto demasiado corto
    Dado que existe el empleado "EMP-0007" con estado "activo"
    Cuando edito al empleado "EMP-0007" con puesto "A"
    Entonces el sistema responde 422
    Y la pantalla señala que el campo "puesto" debe corregirse

  Escenario: Error al editar con un departamento que no existe en el catálogo
    Dado que existe el empleado "EMP-0007" con estado "activo"
    Cuando edito al empleado "EMP-0007" con departamento "Marketing"
    Entonces el sistema responde 422
    Y la pantalla señala que el campo "departamento" debe corregirse

  Escenario: Error al dar de baja con una fecha de baja anterior a la fecha de ingreso
    Dado que existe el empleado "EMP-0007" con fecha_ingreso "2022-05-10" y estado "activo"
    Cuando doy de baja al empleado "EMP-0007" con fecha_baja "2022-01-01"
    Entonces el sistema responde 422
    Y la pantalla señala que el campo "fecha_baja" debe corregirse

# Preguntas abiertas
# - No se especifica qué debe hacer el sistema si en una edición se envían valores distintos
#   para numero_empleado o correo (¿se ignoran silenciosamente o se responde un error?).
# - No se especifica si se puede dar de baja nuevamente a un empleado que ya está en estado "baja",
#   ni si existe alguna forma de reactivarlo.
