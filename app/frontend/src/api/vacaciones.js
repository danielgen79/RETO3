const JSON_HEADERS = { "Content-Type": "application/json" };

async function leerRespuesta(respuesta) {
  const cuerpo = await respuesta.json();
  if (!respuesta.ok) {
    throw new Error(cuerpo.detail || "Ocurrió un error inesperado");
  }
  return cuerpo;
}

export async function solicitarVacaciones(empleadoId, datos) {
  const respuesta = await fetch(`/api/empleados/${empleadoId}/vacaciones`, {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify(datos),
  });
  return leerRespuesta(respuesta);
}

export async function obtenerSaldoVacaciones(empleadoId, anio) {
  const parametros = new URLSearchParams();
  if (anio) parametros.set("anio", anio);
  const cadena = parametros.toString();
  const respuesta = await fetch(
    `/api/empleados/${empleadoId}/vacaciones${cadena ? `?${cadena}` : ""}`
  );
  return leerRespuesta(respuesta);
}
