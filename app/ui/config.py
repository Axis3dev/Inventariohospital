"""Vista de configuración de catálogos básicos."""
from __future__ import annotations

import flet as ft

from ..core import storage


class ConfigView(ft.Column):
    """Vista con catálogos de áreas y departamentos."""

    def __init__(self, page: ft.Page):
        super().__init__(spacing=20, expand=True, scroll=ft.ScrollMode.AUTO)
        self.page = page
        self.areas: list[str] = []
        self.departamentos: list[dict[str, str]] = []
        self._cargar_datos()

        self.txt_area = ft.TextField(label="Nueva área", width=280)
        self.dd_area_depto = ft.Dropdown(label="Área", width=220)
        self.txt_depto = ft.TextField(label="Nuevo departamento", width=280)

        self.areas_list = ft.ListView(expand=True, spacing=4)
        self.departamentos_list = ft.ListView(expand=True, spacing=4)

        self._refrescar_formularios()

        self.controls = [
            self._seccion_areas(),
            self._seccion_departamentos(),
        ]

    # ------------------------------------------------------------------
    # Datos
    def _cargar_datos(self) -> None:
        self.areas = storage.load_areas()
        self.departamentos = storage.load_departamentos()

    def _guardar_areas(self) -> None:
        storage.write_json(storage.DATA_DIR / "areas.json", self.areas)

    def _guardar_departamentos(self) -> None:
        storage.write_json(storage.DATA_DIR / "departamentos.json", self.departamentos)

    # ------------------------------------------------------------------
    # Render helpers
    def _seccion_areas(self) -> ft.Control:
        self._render_areas()
        formulario = ft.Row(
            spacing=12,
            controls=[
                self.txt_area,
                ft.FilledButton("Agregar área", icon=ft.Icons.ADD, on_click=self._agregar_area),
            ],
        )
        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            padding=16,
            content=ft.Column(
                spacing=12,
                controls=[ft.Text("Catálogo de áreas", size=18, weight=ft.FontWeight.W_600), self.areas_list, formulario],
            ),
        )

    def _seccion_departamentos(self) -> ft.Control:
        self._render_departamentos()
        formulario = ft.Row(
            spacing=12,
            controls=[
                self.dd_area_depto,
                self.txt_depto,
                ft.FilledButton("Agregar departamento", icon=ft.Icons.ADD, on_click=self._agregar_departamento),
            ],
        )
        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            padding=16,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Text("Catálogo de departamentos", size=18, weight=ft.FontWeight.W_600),
                    self.departamentos_list,
                    formulario,
                ],
            ),
        )

    def _refrescar_formularios(self) -> None:
        self.dd_area_depto.options = [ft.dropdown.Option(area) for area in self.areas]
        if self.areas and self.dd_area_depto.value not in self.areas:
            self.dd_area_depto.value = self.areas[0]

    def _render_areas(self) -> None:
        self.areas_list.controls.clear()
        for area in self.areas:
            self.areas_list.controls.append(
                ft.Container(
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=8,
                    padding=10,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(area, weight=ft.FontWeight.W_500),
                            ft.IconButton(
                                ft.Icons.DELETE_FOREVER,
                                tooltip="Eliminar área",
                                on_click=lambda _e, nombre=area: self._eliminar_area(nombre),
                            ),
                        ],
                    ),
                )
            )

    def _render_departamentos(self) -> None:
        self.departamentos_list.controls.clear()
        if not self.departamentos:
            self.departamentos_list.controls.append(ft.Text("Sin departamentos registrados"))
            return
        for item in sorted(self.departamentos, key=lambda x: (x.get("area", ""), x.get("departamento", ""))):
            etiqueta = f"{item.get('area', '')} / {item.get('departamento', '')}"
            self.departamentos_list.controls.append(
                ft.Container(
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=8,
                    padding=10,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(etiqueta, weight=ft.FontWeight.W_500),
                            ft.IconButton(
                                ft.Icons.DELETE_FOREVER,
                                tooltip="Eliminar departamento",
                                on_click=lambda _e, registro=item: self._eliminar_departamento(registro),
                            ),
                        ],
                    ),
                )
            )

    # ------------------------------------------------------------------
    # Acciones
    def _agregar_area(self, _: ft.ControlEvent) -> None:
        nombre = (self.txt_area.value or "").strip()
        if not nombre:
            self._toast("El nombre del área es obligatorio")
            return
        if nombre in self.areas:
            self._toast("El área ya existe")
            return
        self.areas.append(nombre)
        self.areas.sort()
        self._guardar_areas()
        self._refrescar_formularios()
        self._render_areas()
        self.txt_area.value = ""
        self.page.update()

    def _eliminar_area(self, nombre: str) -> None:
        self.areas = [area for area in self.areas if area != nombre]
        self.departamentos = [d for d in self.departamentos if d.get("area") != nombre]
        self._guardar_areas()
        self._guardar_departamentos()
        self._refrescar_formularios()
        self._render_areas()
        self._render_departamentos()
        self.page.update()

    def _agregar_departamento(self, _: ft.ControlEvent) -> None:
        area = self.dd_area_depto.value or ""
        depto = (self.txt_depto.value or "").strip()
        if not area or not depto:
            self._toast("Selecciona un área y captura el departamento")
            return
        if any(d.get("area") == area and d.get("departamento") == depto for d in self.departamentos):
            self._toast("El departamento ya existe")
            return
        self.departamentos.append({"area": area, "departamento": depto})
        self._guardar_departamentos()
        self._render_departamentos()
        self.txt_depto.value = ""
        self.page.update()

    def _eliminar_departamento(self, registro: dict[str, str]) -> None:
        self.departamentos = [d for d in self.departamentos if d != registro]
        self._guardar_departamentos()
        self._render_departamentos()
        self.page.update()

    def _toast(self, mensaje: str) -> None:
        self.page.snack_bar = ft.SnackBar(ft.Text(mensaje))
        self.page.snack_bar.open = True
        self.page.update()


def build(page: ft.Page) -> ft.Control:
    """Punto de entrada de la vista."""

    return ft.Container(expand=True, padding=20, content=ConfigView(page))
