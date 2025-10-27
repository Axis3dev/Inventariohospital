"""Contenedor principal de la interfaz."""
from __future__ import annotations

from typing import Callable, Iterable, Sequence, Tuple

import flet as ft

from ..theme import PRIMARY_COLOR, TEXT_COLOR


Destino = Tuple[str, str, Callable[[ft.Page], ft.Control]]


def make_shell(
    page: ft.Page,
    section_title: str,
    destinations: Iterable[Destino],
    selected_index: int,
    content: ft.Control,
) -> ft.Control:
    """Construye la estructura de navegación y contenido."""

    title_text = ft.Text(section_title, size=20, weight=ft.FontWeight.W_600, color=PRIMARY_COLOR)
    subtitle = ft.Text("Inventario TI Hospitalario", size=12, color=ft.Colors.GREY_600)
    heading = ft.Column([subtitle, title_text], spacing=4, tight=True)

    search = ft.TextField(
        hint_text="Buscar en el inventario",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
    )

    user_badge = ft.Container(
        padding=8,
        border_radius=12,
        bgcolor=ft.Colors.GREY_100,
        content=ft.Column(
            [ft.Text("Usuario", size=14, color=TEXT_COLOR), ft.Text("capturista@hospital", size=12, color=ft.Colors.GREY_600)],
            tight=True,
            spacing=2,
        ),
    )

    header = ft.Container(
        padding=20,
        bgcolor=ft.Colors.WHITE,
        content=ft.Row(
            [heading, search, user_badge],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    content_container = ft.Container(expand=True, padding=20, content=content)
    destinos: Sequence[Destino] = tuple(destinations)

    def on_nav_change(event: ft.ControlEvent) -> None:
        index = event.control.selected_index
        new_title, _, builder = destinos[index]
        title_text.value = new_title
        content_container.content = builder(page)
        page.update()

    def _destination(label: str, icon_name: str) -> ft.NavigationRailDestination:
        return ft.NavigationRailDestination(
            icon=ft.Icon(name=icon_name),
            selected_icon=ft.Icon(name=icon_name),
            label=label,
        )

    nav = ft.NavigationRail(
        selected_index=selected_index,
        label_type=ft.NavigationRailLabelType.ALL,
        destinations=[_destination(label, icon) for label, icon, _ in destinos],
        on_change=on_nav_change,
        bgcolor=ft.Colors.WHITE,
        min_width=80,
        group_alignment=-0.9,
        expand=True,
    )

    rail_container = ft.Container(
        width=96,
        bgcolor=ft.Colors.GREY_50,
        padding=12,
        border_radius=0,
        content=nav,
        expand=True,
    )

    body = ft.Row([rail_container, content_container], spacing=0, expand=True)

    return ft.Column([header, body], expand=True, spacing=0)
