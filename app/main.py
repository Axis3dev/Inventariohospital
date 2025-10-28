"""Punto de entrada principal de la aplicación."""
from __future__ import annotations

import flet as ft

from .theme import page_config
from .ui import dashboard, entregas, inventario, mantenimientos, reportes
from .ui.import_txt import importar_txt_view
from .ui.quick_new import quick_new_equipo
from .ui.shell import make_shell


def main(page: ft.Page) -> None:
    """Inicializa la aplicación en modo fullscreen con la shell personalizada."""

    page_config(page)

    routes = [
        ("Dashboard", dashboard.build),
        ("Inventario", inventario.build),
        ("Nuevo equipo", quick_new_equipo),
        ("Importar TXT", importar_txt_view),
        ("Entregas", entregas.build),
        ("Mantenimientos", mantenimientos.build),
        ("Reportes", reportes.build),
    ]

    initial_index = 0
    content = routes[initial_index][1](page)
    page.controls.clear()
    page.add(make_shell(page, routes[initial_index][0], routes, initial_index, content))
    page.update()


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
