"""Punto de entrada de la aplicación Flet."""
from __future__ import annotations

import flet as ft

from .theme import PRIMARY_COLOR, TEXT_COLOR, get_icon, page_config
from .ui import config as config_view
from .ui import dashboard, entregas, inventario, mantenimientos, reportes


SECCIONES = [
    ("Dashboard", get_icon("DASHBOARD"), dashboard.build),
    ("Inventario", get_icon("INVENTORY"), inventario.build),
    ("Entregas", get_icon("LOCAL_SHIPPING"), entregas.build),
    ("Mantenimientos", get_icon("BUILD"), mantenimientos.build),
    ("Reportes", get_icon("INSIGHTS"), reportes.build),
    ("Configuración", get_icon("SETTINGS"), config_view.build),
]


def main(page: ft.Page) -> None:
    page_config(page)
    header = _header(page)
    contenido = ft.Container(expand=True)

    def navegar(index: int) -> None:
        nombre, _, constructor = SECCIONES[index]
        contenido.content = constructor(page)
        page.update()

    rail = ft.NavigationRail(
        destinations=[
            ft.NavigationRailDestination(icon=icono, label=texto)
            for texto, icono, _ in SECCIONES
        ],
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        bgcolor="white",
        on_change=lambda e: navegar(e.control.selected_index),
        min_width=80,
        group_alignment=-0.9,
    )

    navegar(0)
    page.add(ft.Column([header, ft.Row([rail, contenido], expand=True)], expand=True))


def _header(page: ft.Page) -> ft.Control:
    buscador = ft.TextField(
        hint_text="Buscar en todo el inventario",
        prefix_icon=get_icon("SEARCH"),
        expand=True,
    )
    usuario = ft.Container(
        ft.Column(
            [ft.Text("Usuario", size=14, color=TEXT_COLOR), ft.Text("capturista@hospital", size=12, color="#6B7280")],
            tight=True,
        ),
        padding=8,
        bgcolor="white",
        border_radius=12,
    )
    return ft.Container(
        content=ft.Row(
            [
                ft.Text("Inventario TI Hospitalario", size=20, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR),
                buscador,
                usuario,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=20,
    )


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
