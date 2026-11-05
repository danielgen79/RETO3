# language: es

Característica: Consultar el directorio de empleados
  Como persona del área de Recursos Humanos
  Quiero ver el directorio de empleados, buscarlos por nombre o correo y filtrarlos por departamento
  Para encontrar rápido a una persona

  Antecedentes:
    Dado que existen los siguientes empleados registrados:
      | numero_empleado | nombre       | correo                    | puesto                | departamento      | estado |
      | EMP-0001        | Ana Pérez    | ana.perez@empresa.com     | Analista de Sistemas  | Tecnología        | activo |
      | EMP-0002        | Luis Gómez   | luis.gomez@empresa.com    | Ejecutivo de Ventas   | Ventas            | baja   |
      | EMP-0003        | María López  | maria.lopez@empresa.com   | Contadora             | Finanzas          | activo |

  Escenario: Ver el listado completo del directorio
    Dado que estoy en la pantalla del directorio de empleados
    Cuando consulto el directorio sin aplicar filtros
    Entonces veo el listado con número de empleado, nombre, puesto, departamento y estado de cada persona
    Y veo a "EMP-0001" "Ana Pérez" con estado "activo"
    Y veo a "EMP-0002" "Luis Gómez" con estado "baja"
    Y veo a "EMP-0003" "María López" con estado "activo"

  Escenario: Buscar por nombre sin distinguir mayúsculas de minúsculas
    Dado que estoy en la pantalla del directorio de empleados
    Cuando busco "ana"
    Entonces veo únicamente al empleado "EMP-0001" "Ana Pérez" en el resultado

  Escenario: Buscar por correo sin distinguir mayúsculas de minúsculas
    Dado que estoy en la pantalla del directorio de empleados
    Cuando busco "ANA.PEREZ@EMPRESA.COM"
    Entonces veo únicamente al empleado con correo "ana.perez@empresa.com" en el resultado

  Escenario: Filtrar por un departamento válido
    Dado que estoy en la pantalla del directorio de empleados
    Cuando filtro por el departamento "Ventas"
    Entonces veo únicamente a los empleados del departamento "Ventas"
    Y veo a "EMP-0002" "Luis Gómez" en el resultado

  Escenario: Un empleado dado de baja sigue apareciendo en el directorio
    Dado que el empleado "EMP-0002" "Luis Gómez" tiene estado "baja"
    Cuando consulto el directorio sin aplicar filtros
    Entonces veo a "EMP-0002" "Luis Gómez" en el listado con estado "baja"

  Escenario: Buscar un término que no coincide con ningún empleado
    Dado que estoy en la pantalla del directorio de empleados
    Cuando busco "Zzz_no_existe"
    Entonces no veo ningún empleado en el resultado
    Y veo el mensaje "No se encontraron empleados que coincidan con la búsqueda."

# Preguntas abiertas
# - ¿Cuál es el texto exacto del mensaje que debe mostrarse cuando la búsqueda no arroja resultados?
#   Se asumió "No se encontraron empleados que coincidan con la búsqueda." a partir de la nota del dueño del producto.
# - ¿Qué debe ocurrir si se intenta filtrar por un departamento que no está en la lista válida
#   (Tecnología, Ventas, Finanzas, Recursos Humanos, Operaciones)? ¿Se debe impedir la selección desde la pantalla
#   o el sistema debe responder con algún mensaje de error?
