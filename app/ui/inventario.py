"""Vista de inventario con filtros, edición y egreso."""
from __future__ import annotations

from typing import Callable

import flet as ft

from ..core import reglas, storage
from ..core.modelos import Asset, Ubicacion


class InventarioView(ft.Column):
    """Vista principal del inventario."""

    def __init__(self, page: ft.Page):
        super().__init__(expand=True, spacing=16)
        self.page = page
        self.activos: list[Asset] = []
        self.sort_field = "sku"
        self.sort_ascending = True
        Asset.catalogo_estatus = storage.load_estatus()

        self.dd_area = ft.Dropdown(width=200, label="Área", on_change=lambda e: self._actualizar_departamentos())
        self.dd_depto = ft.Dropdown(width=200, label="Departamento", on_change=lambda e: self._refrescar())
        self.dd_categoria = ft.Dropdown(width=200, label="Categoría", on_change=lambda e: self._refrescar())
        self.dd_estado = ft.Dropdown(width=200, label="Estado", on_change=lambda e: self._refrescar())
        self.dd_estatus = ft.Dropdown(width=200, label="Estatus", on_change=lambda e: self._refrescar())
        self.txt_busqueda = ft.TextField(
            label="Buscar",
            hint_text="SKU, marca, modelo o serie",
            width=240,
            on_change=lambda e: self._refrescar(),
        )

        self.btn_limpiar = ft.TextButton("Limpiar filtros", on_click=lambda e: self._limpiar_filtros())
        self.btn_egreso = ft.FilledButton("Egreso de equipos", icon=ft.Icons.LOGOUT, on_click=lambda e: self._abrir_egreso())

        self.tabla = ft.DataTable(
            expand=True,
            column_spacing=16,
            heading_row_color=ft.Colors.BLUE_50,
            columns=self._construir_columnas(),
            rows=[],
        )

        self._cargar_catálogos()
        self._recargar_datos()

        filtros = ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            padding=16,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        spacing=12,
                        controls=[self.dd_area, self.dd_depto, self.dd_categoria, self.dd_estado, self.dd_estatus, self.txt_busqueda],
                        wrap=True,
                    ),
                    ft.Row(spacing=12, controls=[self.btn_limpiar, self.btn_egreso]),
                ],
            ),
        )

        self.controls = [
            filtros,
            ft.Container(expand=True, bgcolor=ft.Colors.WHITE, border_radius=12, padding=12, content=self.tabla),
        ]

    # ------------------------------------------------------------------
    def _cargar_catálogos(self) -> None:
        areas = ["Todos"] + storage.load_areas()
        categorias = ["Todos"] + [item.get("categoria", "") for item in storage.read_json_generic("categorias.json", [])]
        estados = ["Todos"] + Asset.catalogo_estados
        estatus = ["Todos"] + storage.load_estatus()

        self.dd_area.options = [ft.dropdown.Option(valor) for valor in areas if valor]
        self.dd_categoria.options = [ft.dropdown.Option(valor) for valor in categorias if valor]
        self.dd_estado.options = [ft.dropdown.Option(valor) for valor in estados if valor]
        self.dd_estatus.options = [ft.dropdown.Option(valor) for valor in estatus if valor]

        self.dd_area.value = "Todos"
        self.dd_categoria.value = "Todos"
        self.dd_estado.value = "Todos"
        self.dd_estatus.value = "Todos"
        self._actualizar_departamentos()

    def _actualizar_departamentos(self) -> None:
        area = None if self.dd_area.value in (None, "Todos") else self.dd_area.value
        departamentos = ["Todos"] + storage.departamentos_por_area(area)
        self.dd_depto.options = [ft.dropdown.Option(valor) for valor in departamentos if valor]
        self.dd_depto.value = "Todos"
        self._refrescar()

    # ------------------------------------------------------------------
    def _construir_columnas(self) -> list[ft.DataColumn]:
        columnas: list[tuple[str, str]] = [
            ("SKU", "sku"),
            ("Categoría", "categoria"),
            ("Área", "area"),
            ("Departamento", "departamento"),
            ("Estado", "estado"),
            ("Estatus", "estatus"),
            ("Fecha ingreso", "fecha_ingreso"),
        ]

        resultado: list[ft.DataColumn] = []
        for idx, (titulo, campo) in enumerate(columnas):
            resultado.append(
                ft.DataColumn(
                    ft.Text(titulo, weight=ft.FontWeight.W_600),
                    on_sort=self._crear_sort_handler(campo),
                )
            )
        resultado.append(ft.DataColumn(ft.Text("Acciones")))
        return resultado

    def _crear_sort_handler(self, campo: str) -> Callable[[ft.DataColumnSortEvent], None]:
        return lambda e: self._ordenar(campo, e.ascending)

    def _ordenar(self, campo: str, ascendente: bool) -> None:
        self.sort_field = campo
        self.sort_ascending = ascendente
        self._refrescar()

    # ------------------------------------------------------------------
    def _recargar_datos(self) -> None:
        self.activos = reglas.cargar_activos()
        self._refrescar()

    def _refrescar(self) -> None:
        filtrados = self._filtrar_activos()
        ordenados = sorted(
            filtrados,
            key=lambda item: self._clave_orden(item, self.sort_field),
            reverse=not self.sort_ascending,
        )
        self.tabla.rows = [self._fila(asset) for asset in ordenados]
        self.page.update()

    def _filtrar_activos(self) -> list[Asset]:
        area = None if self.dd_area.value in (None, "Todos") else self.dd_area.value
        depto = None if self.dd_depto.value in (None, "Todos") else self.dd_depto.value
        categoria = None if self.dd_categoria.value in (None, "Todos") else self.dd_categoria.value
        estado = None if self.dd_estado.value in (None, "Todos") else self.dd_estado.value
        estatus = None if self.dd_estatus.value in (None, "Todos") else self.dd_estatus.value
        texto = (self.txt_busqueda.value or "").strip().lower()

        resultado: list[Asset] = []
        for asset in self.activos:
            if area and asset.ubicacion_actual.area != area:
                continue
            if depto and asset.ubicacion_actual.departamento != depto:
                continue
            if categoria and asset.categoria != categoria:
                continue
            if estado and asset.estado != estado:
                continue
            if estatus and asset.estatus != estatus:
                continue
            if texto:
                blob = " ".join(
                    [
                        asset.sku,
                        asset.categoria,
                        asset.marca,
                        asset.modelo,
                        asset.numero_serie,
                        asset.descripcion,
                    ]
                ).lower()
                if texto not in blob:
                    continue
            resultado.append(asset)
        return resultado

    def _clave_orden(self, asset: Asset, campo: str) -> str:
        if campo == "area":
            return asset.ubicacion_actual.area or ""
        if campo == "departamento":
            return asset.ubicacion_actual.departamento or ""
        if campo == "fecha_ingreso":
            return asset.fecha_ingreso or ""
        if campo == "estado":
            return asset.estado or ""
        if campo == "estatus":
            return asset.estatus or ""
        return getattr(asset, campo, "") or ""

    def _fila(self, asset: Asset) -> ft.DataRow:
        chip_color = self._color_estatus(asset.estatus)
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(asset.sku)),
                ft.DataCell(ft.Text(asset.categoria)),
                ft.DataCell(ft.Text(asset.ubicacion_actual.area)),
                ft.DataCell(ft.Text(asset.ubicacion_actual.departamento)),
                ft.DataCell(ft.Text(asset.estado)),
                ft.DataCell(ft.Chip(label=ft.Text(asset.estatus), bgcolor=chip_color, color=ft.Colors.BLACK)),
                ft.DataCell(ft.Text(asset.fecha_ingreso)),
                ft.DataCell(
                    ft.IconButton(
                        ft.Icons.EDIT,
                        tooltip="Editar equipo",
                        on_click=lambda _e, sku=asset.sku: self._abrir_edicion(sku),
                    )
                ),
            ],
        )

    def _color_estatus(self, estatus: str) -> str:
        mapa = {
            "PENDIENTE_ENTREGA": ft.Colors.AMBER_100,
            "OPERATIVO": ft.Colors.GREEN_100,
            "EN_SERVICIO": ft.Colors.BLUE_100,
            "EN_MANTENIMIENTO": ft.Colors.ORANGE_100,
            "EN_REPARACION": ft.Colors.RED_100,
            "BAJA": ft.Colors.GREY_200,
        }
        return mapa.get(estatus, ft.Colors.GREY_100)

    def _limpiar_filtros(self) -> None:
        self.dd_area.value = "Todos"
        self.dd_categoria.value = "Todos"
        self.dd_estado.value = "Todos"
        self.dd_estatus.value = "Todos"
        self.txt_busqueda.value = ""
        self._actualizar_departamentos()

    def _abrir_edicion(self, sku: str) -> None:
        asset = next((a for a in self.activos if a.sku == sku), None)
        if not asset:
            self.page.snack_bar = ft.SnackBar(ft.Text("No se encontró el equipo seleccionado"), open=True)
            self.page.update()
            return
        dialog = EditarEquipoDialog(self, asset)
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _abrir_egreso(self) -> None:
        dialog = EgresoDialog(self)
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()


class EditarEquipoDialog(ft.AlertDialog):
    """Diálogo para editar un equipo existente."""

    def __init__(self, vista: InventarioView, asset: Asset):
        super().__init__(modal=True)
        self.vista = vista
        self.asset = asset
        self.confirmar_serie = False

        self.dd_categoria = ft.Dropdown(
            label="Categoría",
            value=asset.categoria,
            options=[ft.dropdown.Option(item.get("categoria")) for item in storage.read_json(storage.DATA_DIR / "categorias.json")],
        )
        self.txt_marca = ft.TextField(label="Marca", value=asset.marca)
        self.txt_modelo = ft.TextField(label="Modelo", value=asset.modelo)
        self.txt_serie = ft.TextField(label="Número de serie", value=asset.numero_serie)
        self.txt_descripcion = ft.TextField(label="Descripción", value=asset.descripcion, multiline=True, min_lines=2)

        self.dd_area = ft.Dropdown(
            label="Área",
            value=asset.ubicacion_actual.area,
            options=[ft.dropdown.Option(area) for area in storage.load_areas()],
            on_change=lambda e: self._actualizar_departamentos(),
        )
        self.dd_depto = ft.Dropdown(label="Departamento")
        self.dd_estatus = ft.Dropdown(
            label="Estatus",
            value=asset.estatus,
            options=[ft.dropdown.Option(valor) for valor in storage.load_estatus()],
        )
        self.dd_estado = ft.Dropdown(
            label="Estado operativo",
            value=asset.estado,
            options=[ft.dropdown.Option(valor) for valor in Asset.catalogo_estados],
        )

        self._actualizar_departamentos()

        self.content = ft.Column(
            tight=True,
            spacing=10,
            controls=[
                ft.Text(f"Editar equipo {asset.sku}", size=18, weight=ft.FontWeight.W_600),
                ft.Row(spacing=10, controls=[self.dd_categoria, self.txt_marca, self.txt_modelo]),
                ft.Row(spacing=10, controls=[self.txt_serie, self.dd_area, self.dd_depto]),
                self.dd_estatus,
                self.dd_estado,
                self.txt_descripcion,
            ],
        )
        self.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: self._cerrar()),
            ft.FilledButton("Guardar", icon=ft.Icons.SAVE, on_click=lambda e: self._guardar()),
        ]

    def _actualizar_departamentos(self) -> None:
        area = self.dd_area.value
        opciones = [ft.dropdown.Option(dep) for dep in storage.departamentos_por_area(area)]
        self.dd_depto.options = opciones
        if opciones:
            valores = [opcion.text for opcion in opciones]
            if self.asset.ubicacion_actual.departamento in valores:
                self.dd_depto.value = self.asset.ubicacion_actual.departamento
            else:
                self.dd_depto.value = valores[0]
        else:
            self.dd_depto.value = None

    def _guardar(self) -> None:
        serie = (self.txt_serie.value or "").strip()
        duplicado = any(
            a.numero_serie.lower() == serie.lower()
            and a.sku != self.asset.sku
            for a in self.vista.activos
            if serie
        )
        if duplicado and not self.confirmar_serie:
            self.confirmar_serie = True
            self.vista.page.snack_bar = ft.SnackBar(
                ft.Text("Número de serie duplicado. Presiona guardar nuevamente para confirmar."), open=True
            )
            self.vista.page.update()
            return

        self.asset.categoria = self.dd_categoria.value or self.asset.categoria
        self.asset.marca = self.txt_marca.value or ""
        self.asset.modelo = self.txt_modelo.value or ""
        self.asset.numero_serie = serie
        self.asset.descripcion = self.txt_descripcion.value or ""
        self.asset.estado = self.dd_estado.value or self.asset.estado
        self.asset.estatus = self.dd_estatus.value or self.asset.estatus
        self.asset.ubicacion_actual = Ubicacion(area=self.dd_area.value or "", departamento=self.dd_depto.value or "")

        try:
            self.asset.validar()
        except Exception as exc:  # noqa: BLE001
            self.vista.page.snack_bar = ft.SnackBar(ft.Text(str(exc)), open=True)
            self.vista.page.update()
            return

        reglas.guardar_activos(self.vista.activos)
        self.vista._recargar_datos()
        self._cerrar()

    def _cerrar(self) -> None:
        self.open = False
        self.vista.page.update()


class EgresoDialog(ft.AlertDialog):
    """Diálogo para registrar egreso de equipos."""

    def __init__(self, vista: InventarioView):
        super().__init__(modal=True)
        self.vista = vista
        activos_disponibles = [asset for asset in vista.activos if asset.estatus != "BAJA"]

        self.dd_sku = ft.Dropdown(
            label="Seleccionar equipo",
            width=260,
            options=[ft.dropdown.Option(asset.sku) for asset in activos_disponibles],
        )
        self.btn_agregar = ft.IconButton(ft.Icons.ADD, tooltip="Agregar", on_click=lambda e: self._agregar())
        self.txt_motivo = ft.TextField(label="Motivo de baja", multiline=True, min_lines=2)
        self.seleccionados: list[str] = []
        self.chips = ft.Wrap(spacing=6, run_spacing=6)

        self.content = ft.Column(
            tight=True,
            spacing=10,
            controls=[
                ft.Text("Egreso de equipos", size=18, weight=ft.FontWeight.W_600),
                ft.Row(spacing=8, controls=[self.dd_sku, self.btn_agregar]),
                self.chips,
                self.txt_motivo,
            ],
        )
        self.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: self._cerrar()),
            ft.FilledButton("Registrar egreso", icon=ft.Icons.SAVE, on_click=lambda e: self._guardar()),
        ]

    def _agregar(self) -> None:
        if not self.dd_sku.value:
            return
        if self.dd_sku.value not in self.seleccionados:
            self.seleccionados.append(self.dd_sku.value)
            self._refrescar_chips()

    def _refrescar_chips(self) -> None:
        self.chips.controls = [
            ft.Chip(
                label=ft.Text(sku),
                delete_icon=ft.Icon(ft.Icons.CLOSE),
                on_delete=lambda e, value=sku: self._quitar(value),
            )
            for sku in self.seleccionados
        ]
        self.vista.page.update()

    def _quitar(self, sku: str) -> None:
        if sku in self.seleccionados:
            self.seleccionados.remove(sku)
            self._refrescar_chips()

    def _guardar(self) -> None:
        if not self.seleccionados:
            self.vista.page.snack_bar = ft.SnackBar(ft.Text("Selecciona al menos un equipo"), open=True)
            self.vista.page.update()
            return
        motivo = (self.txt_motivo.value or "").strip()
        if not motivo:
            self.vista.page.snack_bar = ft.SnackBar(ft.Text("Captura el motivo de baja"), open=True)
            self.vista.page.update()
            return

        for sku in self.seleccionados:
            asset = next((a for a in self.vista.activos if a.sku == sku), None)
            if not asset:
                continue
            asset.estatus = "BAJA"
            asset.estado = "BAJA"
            reglas.registrar_egreso(asset, usuario="sistemas", nota=motivo)

        reglas.guardar_activos(self.vista.activos)
        self.vista._recargar_datos()
        self.vista.page.snack_bar = ft.SnackBar(ft.Text("Egreso registrado"), open=True)
        self.vista.page.update()
        self._cerrar()

    def _cerrar(self) -> None:
        self.open = False
        self.vista.page.update()


def build(page: ft.Page) -> ft.Control:
    """Entrada a la vista de inventario."""

    return ft.Container(expand=True, padding=16, content=InventarioView(page))
