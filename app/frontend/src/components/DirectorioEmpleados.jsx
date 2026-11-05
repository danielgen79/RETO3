import { useEffect, useState } from "react";
import { obtenerDepartamentos, obtenerEmpleados } from "../api/empleados.js";

const ETIQUETAS_ESTADO = {
  activo: "Activo",
  baja: "Baja",
};

export default function DirectorioEmpleados() {
  const [empleados, setEmpleados] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [departamento, setDepartamento] = useState("");
  const [departamentos, setDepartamentos] = useState([]);

  useEffect(() => {
    obtenerDepartamentos()
      .then(setDepartamentos)
      .catch(() => setDepartamentos([]));
  }, []);

  useEffect(() => {
    obtenerEmpleados({ busqueda, departamento })
      .then(setEmpleados)
      .catch(() => setEmpleados([]));
  }, [busqueda, departamento]);

  return (
    <section>
      <h2>Directorio de empleados</h2>
      <div>
        <input
          data-testid="buscar-empleados"
          placeholder="Buscar por nombre o correo"
          value={busqueda}
          onChange={(evento) => setBusqueda(evento.target.value)}
        />
        <select
          data-testid="filtro-departamento"
          value={departamento}
          onChange={(evento) => setDepartamento(evento.target.value)}
        >
          <option value="">Todos los departamentos</option>
          {departamentos.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </div>

      {empleados.length === 0 ? (
        <p data-testid="sin-resultados">
          No se encontraron empleados que coincidan con la búsqueda.
        </p>
      ) : (
        <table data-testid="tabla-empleados">
          <thead>
            <tr>
              <th>Número</th>
              <th>Nombre</th>
              <th>Puesto</th>
              <th>Departamento</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {empleados.map((empleado) => (
              <tr key={empleado.id} data-testid={`fila-empleado-${empleado.id}`}>
                <td data-testid={`numero-empleado-${empleado.id}`}>
                  {empleado.numero_empleado}
                </td>
                <td>{empleado.nombre}</td>
                <td>{empleado.puesto}</td>
                <td>{empleado.departamento}</td>
                <td data-testid={`estado-empleado-${empleado.id}`}>
                  {ETIQUETAS_ESTADO[empleado.estado] || empleado.estado}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
