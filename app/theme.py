"""Configuración de tema y componentes comunes para la app."""
from __future__ import annotations

from typing import Callable

import flet as ft

PRIMARY_COLOR = ft.Colors.BLUE_700
ACCENT_COLOR = "#00BFA6"
TEXT_COLOR = ft.Colors.BLACK87
BACKGROUND_COLOR = ft.Colors.WHITE


def page_config(page: ft.Page) -> None:
    """Configura valores globales para la ventana principal."""

    page.title = "Inventario TI Hospitalario"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = BACKGROUND_COLOR

    page.window_full_screen = True
    page.window_maximized = True

    page.padding = 0
    page.spacing = 0
    page.scroll = ft.ScrollMode.AUTO
    page.update()


def primary_button(
    label: str,
    on_click: Callable[[ft.ControlEvent], None],
    icon: str | None = None,
) -> ft.Control:
    """Botón primario con la paleta institucional."""

    style = ft.ButtonStyle(
        bgcolor=PRIMARY_COLOR,
        color=ft.Colors.WHITE,
        overlay_color=ACCENT_COLOR,
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        shape=ft.RoundedRectangleBorder(radius=12),
    )
    return ft.ElevatedButton(text=label, icon=icon, on_click=on_click, style=style)


def flat_button(
    label: str,
    on_click: Callable[[ft.ControlEvent], None],
    icon: str | None = None,
) -> ft.Control:
    """Botón plano con énfasis en el color primario."""

    style = ft.ButtonStyle(
        bgcolor="transparent",
        color=PRIMARY_COLOR,
        overlay_color=ACCENT_COLOR,
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        shape=ft.RoundedRectangleBorder(radius=12, side=ft.BorderSide(color=PRIMARY_COLOR)),
    )
    return ft.OutlinedButton(text=label, icon=icon, on_click=on_click, style=style)


def card(*content: ft.Control, expand: bool = False) -> ft.Control:
    """Tarjeta con esquinas redondeadas y sombra suave."""

    return ft.Container(
        content=ft.Column(list(content), tight=True, spacing=8),
        bgcolor=ft.Colors.WHITE,
        border_radius=16,
        shadow=ft.BoxShadow(blur_radius=8, spread_radius=1, color="#1F293710"),
        padding=16,
        expand=expand,
    )
