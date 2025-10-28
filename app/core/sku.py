"""Generador de SKU para equipos."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Iterable

from . import storage


def generar_sku(categoria: str, prefijo: str, existentes: Iterable[str]) -> str:
    """Genera un SKU con formato CAT-AAAA-####."""

    anio = datetime.utcnow().year
    consecutivos: dict[tuple[str, int], int] = defaultdict(int)
    for sku in existentes:
        try:
            cat, year, consecutivo = sku.split("-")
            consecutivos[(cat, int(year))] = max(consecutivos[(cat, int(year))], int(consecutivo))
        except ValueError:
            continue
    consecutivo = consecutivos[(prefijo, anio)] + 1
    return f"{prefijo}-{anio}-{consecutivo:04d}"


def siguiente_sku(categoria: str) -> str:
    """Obtiene el siguiente SKU basado en la categoría."""

    categorias = storage.read_json_list("categorias.json")
    prefijo = next((item["prefijo"] for item in categorias if item["categoria"] == categoria), None)
    if not prefijo:
        raise ValueError(f"No existe prefijo para la categoría {categoria}")
    assets = storage.read_json_list("assets.json")
    existentes = [asset["sku"] for asset in assets if asset.get("categoria") == categoria]
    return generar_sku(categoria, prefijo, existentes)
