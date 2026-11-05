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

export async function obtenerEmpleados({ busqueda, departamento } = {}) {
  const parametros = new URLSearchParams();
  if (busqueda) parametros.set("busqueda", busqueda);
  if (departamento) parametros.set("departamento", departamento);
  const cadena = parametros.toString();
  const respuesta = await fetch(`/api/empleados${cadena ? `?${cadena}` : ""}`);
  return leerRespuesta(respuesta);
}

export async function actualizarEmpleado(id, datos) {
  const respuesta = await fetch(`/api/empleados/${id}`, {
    method: "PUT",
    headers: JSON_HEADERS,
    body: JSON.stringify(datos),
  });
  return leerRespuesta(respuesta);
}

export async function darDeBajaEmpleado(id, fechaBaja) {
  const respuesta = await fetch(`/api/empleados/${id}/baja`, {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify({ fecha_baja: fechaBaja }),
  });
  return leerRespuesta(respuesta);
}
