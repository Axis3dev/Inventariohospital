"""Dashboard con indicadores rápidos."""
from __future__ import annotations

import flet as ft

from ..core import storage


def _kpi(titulo: str, valor: str) -> ft.Control:
    return ft.Container(
        bgcolor=ft.Colors.WHITE,
        border_radius=12,
        padding=16,
        content=ft.Column(
            controls=[
                ft.Text(titulo, weight=ft.FontWeight.W_600),
                ft.Text(valor, size=26, weight=ft.FontWeight.W_700),
            ],
            spacing=6,
        ),
    )


def build(page: ft.Page) -> ft.Control:  # noqa: ARG001
    """Construye la vista principal del dashboard."""

    assets = storage.read_json(storage.DATA_DIR / "assets.json") or []
    total = len(assets)

    return ft.Container(
        expand=True,
        padding=16,
        content=ft.Column(
            spacing=16,
            expand=True,
            controls=[
                ft.Row(
                    spacing=12,
                    controls=[
                        _kpi("Equipos totales", str(total)),
                        _kpi("Entregas pendientes", "0"),
                        _kpi("Mantenimientos próximos", "Hoy: 0 / 7d: 0 / 30d: 0"),
                    ],
                    wrap=True,
                ),
                ft.Text("Equipos por estado", size=18, weight=ft.FontWeight.W_700),
                ft.Container(
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    padding=16,
                    content=ft.Text("Próximamente: gráfico/tabla"),
                ),
            ],
        ),
    )
