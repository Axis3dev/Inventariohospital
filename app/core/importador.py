"""Importación de sesiones de inventario desde archivos TXT."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable

from . import reglas, storage
from .modelos import Asset, Ubicacion


def importar_txt(ruta: Path, area: str, depto: str, usuario: str) -> dict[str, any]:
    """Procesa un archivo TXT con SKUs uno por línea."""

    if ruta.suffix.lower() != ".txt":
        raise ValueError("Solo se permiten archivos TXT")
    storage.backup_data()
    with ruta.open("r", encoding="utf-8") as fh:
        skus = {line.strip() for line in fh if line.strip()}
    activos = reglas.cargar_activos()
    movimientos: list[dict[str, str]] = []
    nuevos: list[Asset] = []
    cambios = False
    for sku in skus:
        asset = next((a for a in activos if a.sku == sku), None)
        if asset:
            if asset.ubicacion_actual.area != area or asset.ubicacion_actual.departamento != depto:
                origen = (asset.ubicacion_actual.area, asset.ubicacion_actual.departamento)
                asset.ubicacion_actual = Ubicacion(area=area, departamento=depto)
                reglas.registrar_movimiento(asset, origen, (area, depto), usuario, nota="Importación TXT")
                movimientos.append({"sku": sku, "origen": origen, "destino": (area, depto)})
                cambios = True
        else:
            nuevos.append(
                Asset(
                    sku=sku,
                    categoria="",
                    marca="",
                    modelo="",
                    numero_serie="",
                    descripcion="",
                    estado="OPERATIVO",
                    ubicacion_actual=Ubicacion(area=area, departamento=depto),
                    fecha_ingreso=datetime.utcnow().date().isoformat(),
                )
            )
            cambios = True
    if nuevos:
        activos.extend(nuevos)
    if cambios:
        reglas.guardar_activos(activos)
    diferencias = reglas.diferencias_importacion(skus, area, depto)
    sesion_dir = storage.DATA_DIR / "sesiones" / f"{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{area}-{depto}"
    sesion_dir.mkdir(parents=True, exist_ok=True)
    resumen = {
        "archivo": str(ruta),
        "area": area,
        "departamento": depto,
        "usuario": usuario,
        "total_leidos": len(skus),
        "movimientos": movimientos,
        "nuevos": [asset.to_dict() for asset in nuevos],
        "diferencias": diferencias,
    }
    with (sesion_dir / "import.json").open("w", encoding="utf-8") as fh:
        json.dump(resumen, fh, ensure_ascii=False, indent=2)
    _guardar_diferencias_csv(sesion_dir / "diferencias.csv", diferencias)
    return resumen


def _guardar_diferencias_csv(path: Path, diferencias: Iterable[dict[str, str]]) -> None:
    cabeceras = [
        "tipo",
        "sku",
        "detalle",
        "origen_area",
        "origen_depto",
        "destino_area",
        "destino_depto",
    ]
    storage.ensure_structure()
    with path.open("w", encoding="utf-8") as fh:
        fh.write(",".join(cabeceras) + "\n")
        for row in diferencias:
            fh.write(",".join(row.get(col, "") for col in cabeceras) + "\n")


def importar_sesion(path_txt: str, area: str, depto: str, usuario: str = "sistemas") -> tuple[bool, str]:
    """Ejecuta una importación rápida y devuelve un resumen legible."""

    try:
        resumen = importar_txt(Path(path_txt), area, depto, usuario)
        total = resumen.get("total_leidos", 0)
        movidos = len(resumen.get("movimientos", []))
        nuevos = len(resumen.get("nuevos", []))
        return True, f"Leídos: {total} | Movidos: {movidos} | Nuevos: {nuevos}"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)
