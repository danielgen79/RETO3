import { useState } from "react";
import DirectorioEmpleados from "./components/DirectorioEmpleados.jsx";
import FormularioEdicion from "./components/FormularioEdicion.jsx";
import FormularioEmpleado from "./components/FormularioEmpleado.jsx";

function App() {
  const [empleadoEditando, setEmpleadoEditando] = useState(null);
  const [refrescarContador, setRefrescarContador] = useState(0);

  function refrescarDirectorio() {
    setRefrescarContador((contador) => contador + 1);
  }

  return (
    <main>
      <h1>Registrar empleado</h1>
      {empleadoEditando ? (
        <FormularioEdicion
          empleado={empleadoEditando}
          onActualizado={refrescarDirectorio}
          onVolver={() => setEmpleadoEditando(null)}
        />
      ) : (
        <FormularioEmpleado onCreado={refrescarDirectorio} />
      )}
      <DirectorioEmpleados
        onEditar={setEmpleadoEditando}
        refrescarContador={refrescarContador}
      />
    </main>
  );
}

export default App;
