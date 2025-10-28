"""Vista básica del inventario de equipos."""
from __future__ import annotations

import flet as ft

from ..core import storage


def build(page: ft.Page) -> ft.Control:  # noqa: ARG001
    """Muestra una tabla sencilla con los equipos registrados."""

    assets = storage.read_json(storage.DATA_DIR / "assets.json") or []
    rows = [
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(asset.get("sku", ""))),
                ft.DataCell(ft.Text(asset.get("categoria", ""))),
                ft.DataCell(ft.Text(asset.get("marca", ""))),
                ft.DataCell(ft.Text(asset.get("modelo", ""))),
                ft.DataCell(ft.Text(asset.get("numero_serie", ""))),
                ft.DataCell(ft.Text(asset.get("ubicacion_actual", {}).get("area", ""))),
                ft.DataCell(ft.Text(asset.get("ubicacion_actual", {}).get("departamento", ""))),
            ]
        )
        for asset in assets
    ]

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("SKU")),
            ft.DataColumn(ft.Text("Categoría")),
            ft.DataColumn(ft.Text("Marca")),
            ft.DataColumn(ft.Text("Modelo")),
            ft.DataColumn(ft.Text("Serie")),
            ft.DataColumn(ft.Text("Área")),
            ft.DataColumn(ft.Text("Depto")),
        ],
        rows=rows,
        column_spacing=18,
        heading_row_color=ft.Colors.BLUE_50,
    )

    return ft.Container(expand=True, padding=16, content=table)
