const JSON_HEADERS = { "Content-Type": "application/json" };

async function leerRespuesta(respuesta) {
  const cuerpo = await respuesta.json();
  if (!respuesta.ok) {
    throw new Error(cuerpo.detail || "Ocurrió un error inesperado");
  }
  return cuerpo;
}

export async function crearEmpleado(datos) {
  const respuesta = await fetch("/api/empleados", {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify(datos),
  });
  return leerRespuesta(respuesta);
}

export async function obtenerDepartamentos() {
  const respuesta = await fetch("/api/departamentos");
  return leerRespuesta(respuesta);
}
