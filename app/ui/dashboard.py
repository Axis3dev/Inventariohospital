"""Vista de dashboard principal."""
from __future__ import annotations

import json

import flet as ft

from ..core import reglas
from ..theme import card


def build() -> ft.Control:
    resumen = reglas.resumen_dashboard()
    cards = ft.Row(
        [
            card(ft.Text("Equipos totales", weight=ft.FontWeight.BOLD), ft.Text(str(resumen["total_activos"]), size=32)),
            card(
                ft.Text("Entregas pendientes", weight=ft.FontWeight.BOLD),
                ft.Text(str(resumen["pendientes_entrega"]), size=32),
            ),
            card(
                ft.Text("Mantenimientos próximos", weight=ft.FontWeight.BOLD),
                ft.Text(f"Hoy: {resumen['mantenimientos_hoy']}  / 7d: {resumen['mantenimientos_7']}  / 30d: {resumen['mantenimientos_30']}", size=16),
            ),
        ],
        wrap=True,
        spacing=16,
    )
    estados = ft.Column([
        ft.Text("Equipos por estado", weight=ft.FontWeight.BOLD, size=20),
        ft.DataTable(
            columns=[ft.DataColumn(ft.Text("Estado")), ft.DataColumn(ft.Text("Cantidad"))],
            rows=[ft.DataRow(cells=[ft.DataCell(ft.Text(nombre)), ft.DataCell(ft.Text(str(valor)))]) for nombre, valor in resumen["por_estado"].items()],
        ),
    ])
    ultima = card(ft.Text("Última sesión de inventario", weight=ft.FontWeight.BOLD), ft.Text(resumen["ultima_sesion"][:500]))
    grafica_data = reglas.grafica_categorias_por_area()
    grafica = card(
        ft.Text("Resumen por área", weight=ft.FontWeight.BOLD),
        ft.Text(json.dumps(grafica_data, ensure_ascii=False, indent=2), selectable=True),
    )
    return ft.Column([cards, ft.Row([estados, ultima], wrap=True, spacing=16), grafica], scroll=ft.ScrollMode.AUTO, spacing=16)
