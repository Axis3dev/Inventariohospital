"""Dashboard con indicadores básicos del inventario."""
from __future__ import annotations

from collections import Counter

import flet as ft

from ..core import reglas


def _kpi(titulo: str, valor: str) -> ft.Control:
    return ft.Container(
        bgcolor=ft.Colors.WHITE,
        border_radius=12,
        padding=16,
        content=ft.Column(
            spacing=6,
            controls=[
                ft.Text(titulo, weight=ft.FontWeight.W_600),
                ft.Text(valor, size=26, weight=ft.FontWeight.W_700),
            ],
        ),
    )


def build(page: ft.Page) -> ft.Control:
    activos = reglas.cargar_activos()
    resumen = reglas.resumen_dashboard()
    estatus = Counter(asset.estatus for asset in activos)

    chips = ft.Wrap(
        spacing=8,
        run_spacing=8,
        controls=[
            ft.Chip(label=ft.Text(f"{nombre}: {cantidad}"), bgcolor=ft.Colors.GREY_100)
            for nombre, cantidad in estatus.items()
        ]
        or [ft.Text("Sin equipos registrados", color=ft.Colors.GREY)],
    )

    mantenimientos_texto = (
        f"Hoy: {resumen['mantenimientos_hoy']} / 7 días: {resumen['mantenimientos_7']} / 30 días: {resumen['mantenimientos_30']}"
    )

    return ft.Container(
        expand=True,
        padding=16,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Row(
                    spacing=12,
                    wrap=True,
                    controls=[
                        _kpi("Equipos totales", str(resumen["total_activos"])),
                        _kpi("Entregas pendientes", str(resumen["pendientes_entrega"])),
                        _kpi("Mantenimientos próximos", mantenimientos_texto),
                    ],
                ),
                ft.Container(
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    padding=16,
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Text("Equipos por estatus", size=18, weight=ft.FontWeight.W_700),
                            chips,
                        ],
                    ),
                ),
                ft.Container(
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    padding=16,
                    content=ft.Text(
                        f"Última sesión de inventario: {resumen['ultima_sesion']}",
                        color=ft.Colors.GREY_700,
                    ),
                ),
            ],
        ),
    )
