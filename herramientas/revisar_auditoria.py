"""Cruza auditoria.jsonl con los cambios de Git: cada archivo cambiado en app/ debe tener
una escritura (Write/Edit) registrada por algún agente. No forma parte de la fábrica.

Uso:  python herramientas/revisar_auditoria.py
"""
import collections
import json
import re
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
registros = [json.loads(l) for l in (RAIZ / "auditoria.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

print(f"Registros en auditoria.jsonl: {len(registros)}\n")
print("Llamadas a herramientas por agente:")
for (agente, herramienta), n in sorted(collections.Counter((r["agente"], r["herramienta"]) for r in registros).items()):
    print(f"  {agente:22} {herramienta:8} {n}")

# Archivos escritos por cada agente (la entrada se guarda como texto, recortada a 300 caracteres)
escritos: dict[str, set[str]] = collections.defaultdict(set)
for r in registros:
    if r["herramienta"] in ("Write", "Edit", "MultiEdit"):
        m = re.search(r"'file_path': '([^']+)'", r["entrada"])
        if m:
            ruta = m.group(1).replace("\\\\", "/").replace("\\", "/")
            relativa = ruta.split("/app/", 1)[-1] if "/app/" in ruta else ruta
            escritos[relativa].add(r["agente"])

cambios = subprocess.run(["git", "status", "--porcelain", "-uall", "app"], cwd=RAIZ,
                         capture_output=True, text=True, encoding="utf-8").stdout.splitlines()
print("\nArchivos cambiados en app/ y quién los escribió:")
sin_registro = []
for linea in cambios:
    archivo = linea[3:].strip().strip('"').removeprefix("app/")
    if archivo == "CLAUDE.md":
        print(f"  {archivo:50} copiado por la fábrica desde contexto/convenciones_app.md (preparar_app)")
        continue
    agentes = escritos.get(archivo)
    print(f"  {archivo:50} {', '.join(sorted(agentes)) if agentes else 'SIN REGISTRO'}")
    if not agentes:
        sin_registro.append(archivo)

print("\nResultado:", "todo cambio en app/ tiene un agente registrado" if not sin_registro
      else f"{len(sin_registro)} archivo(s) sin registro: revisar")
