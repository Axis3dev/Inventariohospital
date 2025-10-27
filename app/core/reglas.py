"""Reglas de negocio del inventario."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable

from . import storage
from .modelos import Asset, Entrega, Mantenimiento


def cargar_activos() -> list[Asset]:
    return [Asset.from_dict(item) for item in storage.read_json_list("assets.json")]


def guardar_activos(activos: list[Asset]) -> None:
    storage.write_json(storage.DATA_DIR / "assets.json", [asset.to_dict() for asset in activos])


def registrar_ingreso(asset: Asset, usuario: str, nota: str = "") -> None:
    storage.append_csv(
        "ingresos.csv",
        {
            "timestamp": storage.timestamp(),
            "sku": asset.sku,
            "area": asset.ubicacion_actual.area,
            "departamento": asset.ubicacion_actual.departamento,
            "usuario": usuario,
            "nota": nota,
        },
    )


def registrar_movimiento(asset: Asset, origen: tuple[str, str], destino: tuple[str, str], usuario: str, nota: str = "") -> None:
    storage.append_csv(
        "movimientos.csv",
        {
            "timestamp": storage.timestamp(),
            "sku": asset.sku,
            "origen_area": origen[0],
            "origen_depto": origen[1],
            "destino_area": destino[0],
            "destino_depto": destino[1],
            "usuario": usuario,
            "nota": nota,
        },
    )


def registrar_egreso(asset: Asset, usuario: str, nota: str = "") -> None:
    storage.append_csv(
        "egresos.csv",
        {
            "timestamp": storage.timestamp(),
            "sku": asset.sku,
            "area": asset.ubicacion_actual.area,
            "departamento": asset.ubicacion_actual.departamento,
            "usuario": usuario,
            "nota": nota,
        },
    )


def resumen_dashboard() -> dict[str, int]:
    activos = cargar_activos()
    total = len(activos)
    por_estado = Counter(asset.estado for asset in activos)
    entregas = [Entrega.from_dict(item) for item in storage.read_json_list("entregas.json")]
    pendientes = sum(1 for entrega in entregas if entrega.estado_entrega == "PENDIENTE")
    mantenimientos = [Mantenimiento.from_dict(item) for item in storage.read_json_list("mantenimientos.json")]
    proximos = _mantenimientos_proximos(mantenimientos)
    sesiones = list((storage.DATA_DIR / "sesiones").glob("*/import.json"))
    ultima_sesion = max(sesiones, default=None, key=lambda p: p.stat().st_mtime)
    return {
        "total_activos": total,
        "pendientes_entrega": pendientes,
        "mantenimientos_hoy": proximos["hoy"],
        "mantenimientos_7": proximos["siete"],
        "mantenimientos_30": proximos["treinta"],
        "ultima_sesion": ultima_sesion.read_text(encoding="utf-8") if ultima_sesion else "Sin registros",
        "por_estado": por_estado,
    }


def _mantenimientos_proximos(mantenimientos: list[Mantenimiento]) -> dict[str, int]:
    hoy = date.today()
    rangos = {"hoy": 0, "siete": 0, "treinta": 0}
    for mto in mantenimientos:
        if not mto.fecha_programada:
            continue
        try:
            fecha = datetime.fromisoformat(mto.fecha_programada).date()
        except ValueError:
            continue
        if fecha == hoy:
            rangos["hoy"] += 1
        if hoy <= fecha <= hoy + timedelta(days=7):
            rangos["siete"] += 1
        if hoy <= fecha <= hoy + timedelta(days=30):
            rangos["treinta"] += 1
    return rangos


def grafica_categorias_por_area() -> dict[str, dict[str, int]]:
    activos = cargar_activos()
    data: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for asset in activos:
        data[asset.ubicacion_actual.area][asset.categoria] += 1
    return {area: dict(categorias) for area, categorias in data.items()}


def kardex_general() -> list[dict[str, str]]:
    movimientos = storage.read_csv("movimientos.csv")
    ingresos = storage.read_csv("ingresos.csv")
    egresos = storage.read_csv("egresos.csv")
    return sorted(movimientos + ingresos + egresos, key=lambda row: row.get("timestamp", ""))


def kardex_por_sku(sku: str) -> list[dict[str, str]]:
    return [row for row in kardex_general() if row.get("sku") == sku]


def diferencias_importacion(leidos: Iterable[str], area: str, depto: str) -> list[dict[str, str]]:
    activos = cargar_activos()
    leidos_set = set(leidos)
    maestro = [a for a in activos if a.ubicacion_actual.area == area and a.ubicacion_actual.departamento == depto]
    maestro_skus = {a.sku for a in maestro}
    faltantes = maestro_skus - leidos_set
    sobrantes = {
        sku
        for sku in leidos_set
        if sku not in maestro_skus and any(a.sku == sku for a in activos)
    }
    movidos = {
        a.sku
        for a in activos
        if a.sku in leidos_set
        and (a.ubicacion_actual.area != area or a.ubicacion_actual.departamento != depto)
    }
    nuevos = [sku for sku in leidos_set if all(a.sku != sku for a in activos)]
    rows: list[dict[str, str]] = []
    for sku in sorted(faltantes):
        rows.append({
            "tipo": "FALTANTE",
            "sku": sku,
            "detalle": "Equipo no encontrado en conteo",
            "origen_area": area,
            "origen_depto": depto,
            "destino_area": "",
            "destino_depto": "",
        })
    for sku in sorted(sobrantes):
        origen = next((a.ubicacion_actual for a in activos if a.sku == sku), None)
        rows.append({
            "tipo": "SOBRANTE",
            "sku": sku,
            "detalle": "Registrado en otro departamento",
            "origen_area": origen.area if origen else "",
            "origen_depto": origen.departamento if origen else "",
            "destino_area": area,
            "destino_depto": depto,
        })
    for sku in sorted(movidos):
        origen = next((a.ubicacion_actual for a in activos if a.sku == sku), None)
        rows.append({
            "tipo": "MOVIDO",
            "sku": sku,
            "detalle": "Se movió de ubicación",
            "origen_area": origen.area if origen else "",
            "origen_depto": origen.departamento if origen else "",
            "destino_area": area,
            "destino_depto": depto,
        })
    for sku in sorted(nuevos):
        rows.append({
            "tipo": "NUEVO",
            "sku": sku,
            "detalle": "No existe en el maestro",
            "origen_area": "",
            "origen_depto": "",
            "destino_area": area,
            "destino_depto": depto,
        })
    return rows
