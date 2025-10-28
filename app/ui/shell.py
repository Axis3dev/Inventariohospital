"""Contenedor principal con sidebar personalizada."""
from __future__ import annotations

from collections.abc import Callable

import flet as ft

SIDEBAR_W = 220

ICON_MAP: dict[str, ft.icons.IconData] = {
    "Dashboard": ft.Icons.DASHBOARD,
    "Inventario": ft.Icons.INVENTORY,
    "Nuevo equipo": ft.Icons.ADD_BOX,
    "Importar TXT": ft.Icons.UPLOAD_FILE,
    "Entregas": ft.Icons.LOCAL_SHIPPING,
    "Mantenimientos": ft.Icons.BUILD,
    "Reportes": ft.Icons.ANALYTICS,
    "Configuraciones": ft.Icons.SETTINGS,
}


def make_shell(
    page: ft.Page,
    title: str,
    routes: list[tuple[str, Callable[[ft.Page], ft.Control]]],
    selected_index: int,
    content: ft.Control,
) -> ft.Control:
    """Construye la interfaz principal con sidebar y topbar."""

    labels = [route[0] for route in routes]

    def _go(index: int) -> None:
        _, builder = routes[index]
        new_content = builder(page)
        page.controls.clear()
        page.add(make_shell(page, labels[index], routes, index, new_content))
        page.update()

    items: list[ft.Control] = []
    for idx, label in enumerate(labels):
        icon = ICON_MAP.get(label, ft.Icons.CIRCLE)
        button = ft.TextButton(
            content=ft.Row(
                controls=[ft.Icon(icon, color=ft.Colors.BLUE_700), ft.Text(label, size=14)],
                spacing=12,
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.HOVERED: ft.Colors.GREY_100},
                padding=ft.padding.symmetric(vertical=10, horizontal=8),
                alignment=ft.alignment.center_left,
            ),
            on_click=lambda _e, _i=idx: _go(_i),
        )
        if idx == selected_index:
            button = ft.Container(
                bgcolor=ft.Colors.BLUE_50,
                border_radius=8,
                padding=6,
                content=button,
            )
        items.append(button)

    sidebar = ft.Container(
        width=SIDEBAR_W,
        bgcolor=ft.Colors.GREY_50,
        border_radius=12,
        padding=12,
        content=ft.Column(
            expand=True,
            spacing=6,
            controls=[
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=6,
                        controls=items,
                    ),
                ),
                ft.Text("v1.0", size=12, color=ft.Colors.GREY, text_align=ft.TextAlign.CENTER),
            ],
        ),
    )

    topbar = ft.Container(
        padding=12,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(title, size=22, weight=ft.FontWeight.W_700, color=ft.Colors.BLUE_700),
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.FilledButton(text="Nuevo equipo", icon=ft.Icons.ADD, on_click=lambda _e: _go(2)),
                        ft.OutlinedButton(
                            text="Importar TXT",
                            icon=ft.Icons.UPLOAD_FILE,
                            on_click=lambda _e: _go(3),
                        ),
                    ],
                ),
            ],
        ),
    )

    main_area = ft.Row(
        expand=True,
        spacing=16,
        controls=[
            sidebar,
            ft.Container(expand=True, padding=12, content=content),
        ],
    )

    layout = ft.Column(expand=True, spacing=8, controls=[topbar, main_area])
    page.on_resize = lambda _e: page.update()
    return layout
