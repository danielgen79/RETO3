import { useEffect, useState } from "react";
import { crearEmpleado, obtenerDepartamentos } from "../api/empleados.js";

const ESTADO_INICIAL = {
  nombre: "",
  correo: "",
  puesto: "",
  departamento: "",
  fecha_ingreso: "",
};

export default function FormularioEmpleado({ onCreado } = {}) {
  const [datos, setDatos] = useState(ESTADO_INICIAL);
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
      const empleado = await crearEmpleado(datos);
      setMensajeExito(`Empleado ${empleado.numero_empleado} registrado correctamente`);
      setDatos(ESTADO_INICIAL);
      onCreado?.();
    } catch (error) {
      setMensajeError(error.message);
    }
  }

  return (
    <form onSubmit={manejarEnvio}>
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
        <label htmlFor="correo">Correo</label>
        <input
          id="correo"
          data-testid="empleado-correo"
          value={datos.correo}
          onChange={actualizarCampo("correo")}
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
          {departamentos.map((departamento) => (
            <option key={departamento} value={departamento}>
              {departamento}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="fecha_ingreso">Fecha de ingreso</label>
        <input
          id="fecha_ingreso"
          type="date"
          data-testid="empleado-fecha-ingreso"
          value={datos.fecha_ingreso}
          onChange={actualizarCampo("fecha_ingreso")}
        />
      </div>
      <button type="submit" data-testid="empleado-guardar">
        Guardar
      </button>
      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}
    </form>
  );
}
