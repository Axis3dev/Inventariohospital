"""Punto de entrada de la aplicación Flet."""
from __future__ import annotations

import flet as ft

from .theme import page_config
from .ui import config, dashboard, entregas, inventario, mantenimientos, reportes
from .ui.shell import make_shell


def main(page: ft.Page) -> None:
    """Configura la página y monta la shell principal."""

    page_config(page)
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.vertical_alignment = ft.MainAxisAlignment.START

    destinations = [
        ("Dashboard", ft.Icons.DASHBOARD, dashboard.build),
        ("Inventario", ft.Icons.INVENTORY, inventario.build),
        ("Entregas", ft.Icons.LOCAL_SHIPPING, entregas.build),
        ("Mantenimientos", ft.Icons.BUILD, mantenimientos.build),
        ("Reportes", ft.Icons.ANALYTICS, reportes.build),
        ("Configuración", ft.Icons.SETTINGS, config.build),
    ]

    initial_index = 0
    content = destinations[initial_index][2](page)
    shell = make_shell(page, destinations[initial_index][0], destinations, initial_index, content)
    page.add(shell)


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
