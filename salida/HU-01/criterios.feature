# language: es
Característica: Registrar empleado
  Como persona del área de Recursos Humanos
  Quiero registrar a un empleado con su nombre, correo corporativo, puesto, departamento y fecha de ingreso
  Para darlo de alta en la empresa

  Escenario: Registro exitoso de un nuevo empleado
    Dado que no existe ningún empleado con correo "ana.perez@empresa.com"
    Cuando registro un empleado con nombre "Ana Pérez", correo "Ana.Perez@empresa.com", puesto "Analista de RH", departamento "Recursos Humanos" y fecha de ingreso "2024-01-15"
    Entonces el sistema responde con estado 201
    Y el empleado queda registrado con numero_empleado "EMP-0001", correo "ana.perez@empresa.com" y estado "activo"
    Y la pantalla muestra el mensaje "Empleado EMP-0001 registrado correctamente"

  Escenario: Rechazo por correo ya registrado (regla 1)
    Dado que existe un empleado registrado con correo "carlos.ruiz@empresa.com"
    Cuando intento registrar un empleado con nombre "Carlos Ruiz Gómez", correo "Carlos.Ruiz@empresa.com", puesto "Supervisor", departamento "Operaciones" y fecha de ingreso "2024-02-01"
    Entonces el sistema responde con estado 409
    Y la pantalla muestra el mensaje "El correo ya está registrado"

  Escenario: Rechazo por correo que no es corporativo (regla 2)
    Dado que no existe ningún empleado con correo "luis.gomez@gmail.com"
    Cuando intento registrar un empleado con nombre "Luis Gómez", correo "luis.gomez@gmail.com", puesto "Vendedor", departamento "Ventas" y fecha de ingreso "2024-02-01"
    Entonces el sistema responde con estado 422
    Y la pantalla muestra el mensaje "Usa el correo corporativo @empresa.com"

  Escenario: Rechazo por nombre con menos de 2 caracteres (regla 3)
    Dado que no existe ningún empleado con correo "a.valido@empresa.com"
    Cuando intento registrar un empleado con nombre "A", correo "a.valido@empresa.com", puesto "Analista", departamento "Finanzas" y fecha de ingreso "2024-02-01"
    Entonces el sistema responde con estado 422
    Y la pantalla indica que el campo "nombre" debe corregirse con el mensaje "El nombre debe tener entre 2 y 80 caracteres"

  Escenario: Rechazo por fecha de ingreso futura (regla 4)
    Dado que no existe ningún empleado con correo "mario.diaz@empresa.com"
    Cuando intento registrar un empleado con nombre "Mario Díaz", correo "mario.diaz@empresa.com", puesto "Técnico", departamento "Tecnología" y fecha de ingreso "2099-01-01"
    Entonces el sistema responde con estado 422
    Y la pantalla muestra el mensaje "La fecha de ingreso no puede ser futura"

# Preguntas abiertas
# - No se especifica el mensaje exacto de error para cada campo inválido distinto de nombre (puesto, departamento);
#   se usó un ejemplo con el campo "nombre" para representar la regla 3. Confirmar los mensajes exactos para
#   puesto fuera de longitud (2-60) y departamento fuera de la lista permitida.
# - No se especifica el formato exacto de la fecha de ingreso (ISO, dd/mm/aaaa, etc.) en la interfaz; se asumió "aaaa-mm-dd".
