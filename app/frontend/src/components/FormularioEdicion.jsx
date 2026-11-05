import { useEffect, useState } from "react";
import { actualizarEmpleado, obtenerDepartamentos } from "../api/empleados.js";

export default function FormularioEdicion({ empleado, onActualizado, onVolver }) {
  const [datos, setDatos] = useState({
    nombre: empleado.nombre,
    puesto: empleado.puesto,
    departamento: empleado.departamento,
  });
  const [departamentos, setDepartamentos] = useState([]);
  const [mensajeExito, setMensajeExito] = useState("");
  const [mensajeError, setMensajeError] = useState("");

  useEffect(() => {
    obtenerDepartamentos()
      .then(setDepartamentos)
      .catch(() => setDepartamentos([]));
  }, []);

  function actualizarCampo(campo) {
    return (evento) => {
      setDatos((anterior) => ({ ...anterior, [campo]: evento.target.value }));
    };
  }

  async function manejarEnvio(evento) {
    evento.preventDefault();
    setMensajeExito("");
    setMensajeError("");
    try {
      const actualizado = await actualizarEmpleado(empleado.id, datos);
      setMensajeExito(
        `Empleado ${actualizado.numero_empleado} actualizado correctamente`
      );
      onActualizado();
    } catch (error) {
      setMensajeError(error.message);
    }
  }

  return (
    <form onSubmit={manejarEnvio}>
      <h2>Editar empleado {empleado.numero_empleado}</h2>
      <div>
        <label htmlFor="correo">Correo</label>
        <input id="correo" value={empleado.correo} disabled readOnly />
      </div>
      <div>
        <label htmlFor="nombre">Nombre</label>
        <input
          id="nombre"
          data-testid="empleado-nombre"
          value={datos.nombre}
          onChange={actualizarCampo("nombre")}
        />
      </div>
      <div>
        <label htmlFor="puesto">Puesto</label>
        <input
          id="puesto"
          data-testid="empleado-puesto"
          value={datos.puesto}
          onChange={actualizarCampo("puesto")}
        />
      </div>
      <div>
        <label htmlFor="departamento">Departamento</label>
        <select
          id="departamento"
          data-testid="empleado-departamento"
          value={datos.departamento}
          onChange={actualizarCampo("departamento")}
        >
          <option value="">Selecciona un departamento</option>
          {departamentos.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </div>
      <button type="submit" data-testid="empleado-guardar">
        Guardar
      </button>
      <button type="button" onClick={onVolver}>
        Volver a registrar
      </button>
      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}
    </form>
  );
}
