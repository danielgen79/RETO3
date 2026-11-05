import { useState } from "react";
import { darDeBajaEmpleado } from "../api/empleados.js";

export default function ModalBaja({ empleado, onConfirmada, onCancelar }) {
  const [fechaBaja, setFechaBaja] = useState("");
  const [mensajeExito, setMensajeExito] = useState("");
  const [mensajeError, setMensajeError] = useState("");

  async function manejarConfirmar() {
    setMensajeExito("");
    setMensajeError("");
    try {
      await darDeBajaEmpleado(empleado.id, fechaBaja);
      setMensajeExito(
        `Empleado ${empleado.numero_empleado} dado de baja correctamente`
      );
      onConfirmada();
    } catch (error) {
      setMensajeError(error.message);
    }
  }

  return (
    <div>
      <h3>Dar de baja a {empleado.numero_empleado}</h3>
      <div>
        <label htmlFor="fecha_baja">Fecha de baja</label>
        <input
          id="fecha_baja"
          type="date"
          data-testid="empleado-fecha-baja"
          value={fechaBaja}
          onChange={(evento) => setFechaBaja(evento.target.value)}
        />
      </div>
      <button data-testid="confirmar-baja" onClick={manejarConfirmar}>
        Confirmar baja
      </button>
      <button type="button" onClick={onCancelar}>
        Cancelar
      </button>
      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}
    </div>
  );
}
