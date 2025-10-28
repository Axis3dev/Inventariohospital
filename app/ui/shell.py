from collections.abc import Callable

import flet as ft

NAV_WIDTH = 96


def make_shell(
    page: ft.Page,
    title: str,
    destinations: list[tuple[str, str, Callable[[ft.Page], ft.Control]]],
    on_select_index: int,
    content: ft.Control,
) -> ft.Control:
    rail = ft.NavigationRail(
        selected_index=on_select_index,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=NAV_WIDTH,
        group_alignment=-1.0,
        destinations=[
            ft.NavigationRailDestination(
                icon=getattr(ft.Icons, icon_name),
                selected_icon=getattr(ft.Icons, icon_name),
                label=label,
            )
            for (label, icon_name, _builder) in destinations
        ],
    )

    rail_container = ft.Container(
        width=NAV_WIDTH,
        bgcolor=ft.Colors.GREY_50,
        padding=6,
        border_radius=12,
        content=ft.Column(
            expand=True,
            controls=[ft.Container(expand=True, content=rail)],
        ),
    )

    content_container = ft.Container(
        expand=True,
        padding=12,
        content=content,
    )

    layout = ft.Row(
        expand=True,
        spacing=16,
        controls=[rail_container, content_container],
    )

    rail.on_change = lambda e: _route_to(page, destinations, e.control.selected_index)

    shell = ft.Column(
        expand=True,
        spacing=8,
        controls=[_topbar(title), layout],
    )

    page.on_resize = lambda e: page.update()
    return shell


def _route_to(page: ft.Page, destinations, index: int) -> None:
    label, _icon, builder = destinations[index]
    new_content = builder(page)
    page.controls.clear()
    page.add(make_shell(page, label, destinations, index, new_content))
    page.update()


def _topbar(title: str) -> ft.Control:
    return ft.Container(
        padding=12,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(title, size=22, weight=ft.FontWeight.W_700, color=ft.Colors.BLUE_700),
                ft.Container(
                    width=680,
                    content=ft.TextField(
                        prefix_icon=ft.Icons.SEARCH,
                        hint_text="Buscar en el inventario",
                        border_radius=12,
                        dense=True,
                        autofocus=False,
                    ),
                ),
                ft.Container(
                    padding=8,
                    border_radius=12,
                    bgcolor=ft.Colors.GREY_100,
                    content=ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text("Usuario", size=12, color=ft.Colors.GREY),
                            ft.Text("capturista@hospital", size=13),
                        ],
                    ),
                ),
            ],
        ),
    )
