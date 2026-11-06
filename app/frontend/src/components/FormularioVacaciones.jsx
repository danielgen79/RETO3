import { useEffect, useState } from "react";
import {
  obtenerSaldoVacaciones,
  solicitarVacaciones,
} from "../api/vacaciones.js";

export default function FormularioVacaciones({
  empleado,
  onRegistrada,
  onCancelar,
}) {
  const [fechaInicio, setFechaInicio] = useState("");
  const [fechaFin, setFechaFin] = useState("");
  const [diasDisponibles, setDiasDisponibles] = useState(null);
  const [mensaje, setMensaje] = useState("");

  useEffect(() => {
    obtenerSaldoVacaciones(empleado.id)
      .then((saldo) => setDiasDisponibles(saldo.dias_disponibles))
      .catch(() => setDiasDisponibles(null));
  }, [empleado.id]);

  async function manejarEnviar() {
    setMensaje("");
    try {
      const resultado = await solicitarVacaciones(empleado.id, {
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin,
      });
      const anio = resultado.fecha_inicio.slice(0, 4);
      setMensaje(
        `Solicitud registrada: ${resultado.dias_habiles} días hábiles. ` +
          `Te quedan ${resultado.dias_restantes} días hábiles en ${anio}.`
      );
      setDiasDisponibles(resultado.dias_restantes);
      onRegistrada?.();
    } catch (error) {
      setMensaje(error.message);
    }
  }

  return (
    <div>
      <h3>Solicitar vacaciones para {empleado.numero_empleado}</h3>
      <p>
        Días disponibles:{" "}
        <span data-testid="vacaciones-disponibles">
          {diasDisponibles ?? "..."}
        </span>
      </p>
      <div>
        <label htmlFor="vacaciones_fecha_inicio">Fecha de inicio</label>
        <input
          id="vacaciones_fecha_inicio"
          type="date"
          data-testid="vacaciones-fecha-inicio"
          value={fechaInicio}
          onChange={(evento) => setFechaInicio(evento.target.value)}
        />
      </div>
      <div>
        <label htmlFor="vacaciones_fecha_fin">Fecha de fin</label>
        <input
          id="vacaciones_fecha_fin"
          type="date"
          data-testid="vacaciones-fecha-fin"
          value={fechaFin}
          onChange={(evento) => setFechaFin(evento.target.value)}
        />
      </div>
      <button data-testid="vacaciones-enviar" onClick={manejarEnviar}>
        Enviar solicitud
      </button>
      <button type="button" onClick={onCancelar}>
        Cancelar
      </button>
      {mensaje && <p data-testid="vacaciones-mensaje">{mensaje}</p>}
    </div>
  );
}
