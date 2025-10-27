"""Vista de inventario de activos."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import flet as ft

from ..core import importador, reglas, sku, storage
from ..core.modelos import Asset, Ubicacion
from ..theme import card, flat_button, primary_button


class InventarioView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(spacing=16, scroll=ft.ScrollMode.AUTO)
        self.page = page
        self.filtro_texto = ft.TextField(label="Buscar", expand=True, on_change=self._filtrar)
        self.filtro_area = ft.Dropdown(label="Área", options=[], on_change=self._filtrar)
        self.filtro_depto = ft.Dropdown(label="Departamento", options=[], on_change=self._filtrar)
        self.filtro_categoria = ft.Dropdown(label="Categoría", options=[], on_change=self._filtrar)
        self.filtro_estado = ft.Dropdown(label="Estado", options=[], on_change=self._filtrar)
        self.tabla = ft.DataTable(columns=self._columnas())
        self.file_picker = ft.FilePicker(on_result=self._importar_resultado)
        if self.file_picker not in self.page.overlay:
            self.page.overlay.append(self.file_picker)
        self.activos: list[Asset] = []
        self.controls = [
            card(
                ft.Row(
                    [
                        self.filtro_texto,
                        self.filtro_area,
                        self.filtro_depto,
                        self.filtro_categoria,
                        self.filtro_estado,
                        primary_button("+ Alta", self._abrir_alta, icon=ft.Icons.ADD),
                        flat_button("Importar TXT", self._importar_txt, icon=ft.Icons.UPLOAD_FILE),
                    ],
                    wrap=True,
                )
            ),
            card(self.tabla, expand=True),
        ]
        self.actualizar_catalogos()
        self.actualizar_datos()

    def _columnas(self) -> list[ft.DataColumn]:
        return [
            ft.DataColumn(ft.Text("SKU")),
            ft.DataColumn(ft.Text("Categoría")),
            ft.DataColumn(ft.Text("Marca")),
            ft.DataColumn(ft.Text("Modelo")),
            ft.DataColumn(ft.Text("Área")),
            ft.DataColumn(ft.Text("Departamento")),
            ft.DataColumn(ft.Text("Estado")),
        ]

    def actualizar_catalogos(self) -> None:
        areas = storage.read_json_list("areas.json")
        self.filtro_area.options = [ft.dropdown.Option(""), *[ft.dropdown.Option(area) for area in areas]]
        departamentos = storage.read_json_list("departamentos.json")
        self.filtro_depto.options = [ft.dropdown.Option(""), *[ft.dropdown.Option(item["departamento"]) for item in departamentos]]
        categorias = storage.read_json_list("categorias.json")
        self.filtro_categoria.options = [ft.dropdown.Option(""), *[ft.dropdown.Option(item["categoria"]) for item in categorias]]
        self.filtro_estado.options = [ft.dropdown.Option(""), *[ft.dropdown.Option(estado) for estado in Asset.catalogo_estados]]

    def actualizar_datos(self) -> None:
        self.activos = reglas.cargar_activos()
        self._filtrar()

    def _filtrar(self, e: ft.ControlEvent | None = None) -> None:  # noqa: ARG002
        texto = self.filtro_texto.value.lower()
        area = self.filtro_area.value or None
        depto = self.filtro_depto.value or None
        categoria = self.filtro_categoria.value or None
        estado = self.filtro_estado.value or None
        filtrados: list[Asset] = []
        for asset in self.activos:
            if texto and texto not in json_string(asset).lower():
                continue
            if area and asset.ubicacion_actual.area != area:
                continue
            if depto and asset.ubicacion_actual.departamento != depto:
                continue
            if categoria and asset.categoria != categoria:
                continue
            if estado and asset.estado != estado:
                continue
            filtrados.append(asset)
        self.tabla.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(asset.sku or "-")),
                    ft.DataCell(ft.Text(asset.categoria)),
                    ft.DataCell(ft.Text(asset.marca)),
                    ft.DataCell(ft.Text(asset.modelo)),
                    ft.DataCell(ft.Text(asset.ubicacion_actual.area)),
                    ft.DataCell(ft.Text(asset.ubicacion_actual.departamento)),
                    ft.DataCell(ft.Text(asset.estado)),
                ]
            )
            for asset in filtrados
        ]
        self.update()

    def _abrir_alta(self, e: ft.ControlEvent | None = None) -> None:  # noqa: ARG002
        dialog = AltaDialog(self)
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _importar_txt(self, e: ft.ControlEvent | None = None) -> None:  # noqa: ARG002
        self.file_picker.pick_files(allow_multiple=False, allowed_extensions=["txt"])

    def _importar_resultado(self, evento: ft.FilePickerResultEvent) -> None:
        if not evento.files:
            return
        archivo = Path(evento.files[0].path)
        area = self.filtro_area.value or "Urgencias"
        depto = self.filtro_depto.value or "Triage"
        try:
            resumen = importador.importar_txt(archivo, area, depto, self.page.session_id or "usuario")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Importación completada. {resumen['total_leidos']} SKUs"))
            self.page.snack_bar.open = True
            self.actualizar_datos()
        except Exception as exc:  # noqa: BLE001
            self.page.snack_bar = ft.SnackBar(ft.Text(str(exc)))
            self.page.snack_bar.open = True
        finally:
            self.page.update()


class AltaDialog(ft.AlertDialog):
    def __init__(self, vista: InventarioView):
        super().__init__(modal=True)
        self.vista = vista
        categorias = storage.read_json_list("categorias.json")
        areas = storage.read_json_list("departamentos.json")
        self.categoria = ft.Dropdown(label="Categoría", options=[ft.dropdown.Option(cat["categoria"]) for cat in categorias])
        self.marca = ft.TextField(label="Marca", autofocus=True)
        self.modelo = ft.TextField(label="Modelo")
        self.serie = ft.TextField(label="Número de serie")
        self.descripcion = ft.TextField(label="Descripción", multiline=True, min_lines=2)
        self.area = ft.Dropdown(label="Área", options=[ft.dropdown.Option(item["area"]) for item in areas])
        self.depto = ft.Dropdown(label="Departamento", options=[ft.dropdown.Option(item["departamento"]) for item in areas])
        self.estado = ft.Dropdown(label="Estado", options=[ft.dropdown.Option(estado) for estado in Asset.catalogo_estados], value="OPERATIVO")
        self.usuario = ft.TextField(label="Usuario que registra")
        self.actions = [
            flat_button("Cancelar", self._cerrar),
            primary_button("Guardar", self._guardar),
        ]
        self.content = ft.Column(
            [
                self.categoria,
                self.marca,
                self.modelo,
                self.serie,
                self.descripcion,
                self.area,
                self.depto,
                self.estado,
                self.usuario,
            ],
            tight=True,
            spacing=8,
        )

    def _cerrar(self, e: ft.ControlEvent | None = None) -> None:  # noqa: ARG002
        self.open = False
        self.vista.page.update()

    def _guardar(self, e: ft.ControlEvent | None = None) -> None:  # noqa: ARG002
        try:
            if not all([self.categoria.value, self.marca.value, self.modelo.value, self.serie.value, self.descripcion.value]):
                raise ValueError("Todos los campos son obligatorios")
            sku_generado = sku.siguiente_sku(self.categoria.value)
            asset = Asset(
                categoria=self.categoria.value,
                marca=self.marca.value,
                modelo=self.modelo.value,
                numero_serie=self.serie.value,
                descripcion=self.descripcion.value,
                estado=self.estado.value or "OPERATIVO",
                ubicacion_actual=Ubicacion(area=self.area.value or "", departamento=self.depto.value or ""),
                fecha_ingreso=date.today().isoformat(),
                sku=sku_generado,
            )
            asset.validar()
            activos = reglas.cargar_activos()
            if any(a.numero_serie == asset.numero_serie for a in activos):
                self.vista.page.snack_bar = ft.SnackBar(ft.Text("Número de serie duplicado"))
                self.vista.page.snack_bar.open = True
                self.vista.page.update()
            activos.append(asset)
            reglas.guardar_activos(activos)
            reglas.registrar_ingreso(asset, self.usuario.value or "sistema")
            self.vista.actualizar_datos()
            self.vista.page.snack_bar = ft.SnackBar(ft.Text("Equipo registrado correctamente"))
            self.vista.page.snack_bar.open = True
        except Exception as exc:  # noqa: BLE001
            self.vista.page.snack_bar = ft.SnackBar(ft.Text(str(exc)))
            self.vista.page.snack_bar.open = True
        finally:
            self.open = False
            self.vista.page.update()


def build(page: ft.Page) -> ft.Control:
    return InventarioView(page)


def json_string(asset: Asset) -> str:
    return f"{asset.sku} {asset.categoria} {asset.marca} {asset.modelo} {asset.numero_serie} {asset.ubicacion_actual.area} {asset.ubicacion_actual.departamento} {asset.estado}"
