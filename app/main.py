"""Punto de entrada de la aplicación Flet."""
from __future__ import annotations

import flet as ft

from .theme import page_config
from .ui import config, dashboard, entregas, inventario, mantenimientos, reportes
from .ui.shell import make_shell


def main(page: ft.Page) -> None:
    """Configura la página y monta la shell principal."""

    page_config(page)

    destinations = [
        ("Dashboard", "DASHBOARD", dashboard.build),
        ("Inventario", "INVENTORY", inventario.build),
        ("Entregas", "LOCAL_SHIPPING", entregas.build),
        ("Mantenimientos", "BUILD", mantenimientos.build),
        ("Reportes", "ANALYTICS", reportes.build),
        ("Configuración", "SETTINGS", config.build),
    ]

    idx = 0
    content = destinations[idx][2](page)
    page.controls.clear()
    page.add(make_shell(page, destinations[idx][0], destinations, idx, content))
    page.update()


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
