"""Vista de reportes exportables."""
from __future__ import annotations

import flet as ft

from ..core import reportes
from ..theme import card, primary_button


def build(page: ft.Page) -> ft.Control:
    botones = ft.Column(
        [
            primary_button("Listado por departamento (CSV)", lambda e: _exportar(page, "csv")),
            primary_button("Listado por departamento (XLSX)", lambda e: _exportar(page, "xlsx")),
        ],
        spacing=12,
    )
    return card(ft.Text("Reportes disponibles", weight=ft.FontWeight.BOLD), botones)


def _exportar(page: ft.Page, formato: str) -> None:
    try:
        ruta = reportes.exportar_listado_por_departamento(formato=formato)
        page.snack_bar = ft.SnackBar(ft.Text(f"Reporte generado en {ruta}"))
        page.snack_bar.open = True
    except Exception as exc:  # noqa: BLE001
        page.snack_bar = ft.SnackBar(ft.Text(str(exc)))
        page.snack_bar.open = True
    finally:
        page.update()
