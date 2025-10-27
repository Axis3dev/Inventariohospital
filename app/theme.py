"""Definición de tema y componentes comunes para la aplicación."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import flet as ft


PRIMARY_COLOR = "#1A73E8"
ACCENT_COLOR = "#00BFA6"
BACKGROUND_COLOR = "#F5F6F8"
TEXT_COLOR = "#1F2937"
CARD_COLOR = "white"


@dataclass
class ThemedButton:
    """Fábrica de botones con estilos coherentes."""

    label: str
    on_click: Callable[[ft.ControlEvent], None]
    icon: str | None = None
    filled: bool = True

    def build(self) -> ft.Control:
        style = ft.ButtonStyle(
            bgcolor=PRIMARY_COLOR if self.filled else "transparent",
            color="white" if self.filled else PRIMARY_COLOR,
            overlay_color=ACCENT_COLOR,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            shape=ft.RoundedRectangleBorder(radius=12),
        )
        return ft.ElevatedButton(
            text=self.label,
            icon=self.icon,
            on_click=self.on_click,
            style=style,
        )


def primary_button(label: str, on_click: Callable[[ft.ControlEvent], None], icon: str | None = None) -> ft.Control:
    """Crea un botón elevado con el estilo primario."""

    return ThemedButton(label=label, icon=icon, on_click=on_click, filled=True).build()


def flat_button(label: str, on_click: Callable[[ft.ControlEvent], None], icon: str | None = None) -> ft.Control:
    """Crea un botón plano con borde y color primario."""

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
        bgcolor=CARD_COLOR,
        border_radius=16,
        shadow=ft.BoxShadow(blur_radius=8, spread_radius=1, color="#1F293710"),
        padding=16,
        expand=expand,
    )


def page_config(page: ft.Page) -> None:
    """Configura valores globales para la página Flet."""

    page.title = "Inventario TI Hospitalario"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = BACKGROUND_COLOR
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.scroll = ft.ScrollMode.AUTO
    page.fonts = {}


