"""Vista de mantenimientos preventivos y correctivos."""
from __future__ import annotations

from datetime import date, datetime, timedelta

import flet as ft

from ..core import reglas, reportes, storage
from ..core.modelos import Mantenimiento


class MantenimientosView(ft.Column):
    """Vista principal de mantenimiento."""

    def __init__(self, page: ft.Page):
        super().__init__(expand=True, spacing=16, scroll=ft.ScrollMode.AUTO)
        self.page = page
        self._recargar()

        botones = ft.Row(
            spacing=12,
            controls=[
                ft.FilledButton("Mantenimiento preventivo", icon=ft.Icons.EVENT_AVAILABLE, on_click=lambda e: self._nuevo_preventivo()),
                ft.OutlinedButton("Mantenimiento correctivo", icon=ft.Icons.BUILD, on_click=lambda e: self._nuevo_correctivo()),
            ],
        )

        self.preventivos_container = ft.Container()
        self.historial_container = ft.Container()
        self._render_secciones()

        self.controls = [
            botones,
            self.preventivos_container,
            self.historial_container,
        ]

    # ------------------------------------------------------------------
    def _recargar(self) -> None:
        self.activos = reglas.cargar_activos()
        self.mantenimientos = [Mantenimiento.from_dict(item) for item in storage.read_json_list("mantenimientos.json")]

    def _render_secciones(self) -> None:
        self.preventivos_container.content = self._seccion_preventivos()
        self.historial_container.content = self._seccion_historial()

    # ------------------------------------------------------------------
    def _seccion_preventivos(self) -> ft.Control:
        pendientes = [m for m in self.mantenimientos if m.tipo == "PREVENTIVO" and not m.fecha_realizado]
        if not pendientes:
            return ft.Container(
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                padding=16,
                content=ft.Column(
                    spacing=8,
                    controls=[ft.Text("Preventivos pendientes", size=20, weight=ft.FontWeight.W_700), ft.Text("Sin registros")],
                ),
            )

        tarjetas: list[ft.Control] = []
        for mto in pendientes:
            color = self._color_semáforo(mto.fecha_programada)
            tarjetas.append(
                ft.Container(
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    padding=16,
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(f"{mto.sku}", size=18, weight=ft.FontWeight.W_600),
                                    ft.Container(width=16, height=16, bgcolor=color, border_radius=8),
                                ],
                            ),
                            ft.Text(f"Programado: {mto.fecha_programada or 'Sin fecha'}"),
                            ft.Text(mto.observaciones or "Sin observaciones"),
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.OutlinedButton("Aplazar", icon=ft.Icons.SCHEDULE, on_click=lambda _e, item=mto: self._aplazar(item)),
                                    ft.FilledButton("Registrar", icon=ft.Icons.CHECK, on_click=lambda _e, item=mto: self._registrar(item)),
                                ],
                            ),
                        ],
                    ),
                )
            )

        return ft.Container(
            content=ft.Column(
                spacing=12,
                controls=[ft.Text("Preventivos pendientes", size=20, weight=ft.FontWeight.W_700)] + tarjetas,
            )
        )

    def _seccion_historial(self) -> ft.Control:
        registros = sorted(self.mantenimientos, key=lambda m: (m.fecha_realizado or m.fecha_programada or ""), reverse=True)
        filas = []
        for mto in registros:
            texto_fecha = mto.fecha_realizado or mto.fecha_programada or "Sin fecha"
            filas.append(
                ft.Container(
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    padding=12,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text(f"{mto.id_mto} - {mto.sku}", weight=ft.FontWeight.W_600),
                                    ft.Text(f"{mto.tipo} | {texto_fecha}"),
                                ],
                            ),
                            ft.OutlinedButton(
                                "PDF",
                                icon=ft.Icons.PICTURE_AS_PDF,
                                on_click=lambda _e, item=mto: self._pdf(item),
                            ),
                        ],
                    ),
                )
            )
        if not filas:
            filas = [ft.Text("Sin historial registrado", color=ft.Colors.GREY)]
        return ft.Container(
            content=ft.Column(
                spacing=12,
                controls=[ft.Text("Historial", size=20, weight=ft.FontWeight.W_700)] + filas,
            )
        )

    # ------------------------------------------------------------------
    def _color_semáforo(self, fecha: str | None) -> str:
        if not fecha:
            return ft.Colors.GREY_200
        try:
            fecha_obj = datetime.fromisoformat(fecha).date()
        except ValueError:
            return ft.Colors.GREY_200
        hoy = date.today()
        if fecha_obj <= hoy:
            return ft.Colors.RED_200
        if fecha_obj <= hoy + timedelta(days=7):
            return ft.Colors.AMBER_200
        return ft.Colors.GREEN_200

    def _guardar_mantenimientos(self) -> None:
        storage.write_json(storage.DATA_DIR / "mantenimientos.json", [mto.to_dict() for mto in self.mantenimientos])

    def _actualizar_activo(self, sku: str, fecha_ultimo: str | None = None, fecha_prox: str | None = None) -> None:
        for asset in self.activos:
            if asset.sku == sku:
                if fecha_ultimo:
                    asset.fecha_ultimo_mto = fecha_ultimo
                if fecha_prox is not None:
                    asset.fecha_prox_mto = fecha_prox
        reglas.guardar_activos(self.activos)

    # ------------------------------------------------------------------
    def _pdf(self, mantenimiento: Mantenimiento) -> None:
        ruta = reportes.generar_pdf_mantenimiento(mantenimiento.id_mto, mantenimiento.to_dict())
        self.page.snack_bar = ft.SnackBar(ft.Text(f"PDF generado en {ruta}"), open=True)
        self.page.update()

    def _nuevo_preventivo(self) -> None:
        dialog = PreventivoDialog(self)
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _nuevo_correctivo(self) -> None:
        dialog = CorrectivoDialog(self)
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _aplazar(self, mantenimiento: Mantenimiento) -> None:
        dialog = AplazarDialog(self, mantenimiento)
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _registrar(self, mantenimiento: Mantenimiento) -> None:
        dialog = RegistrarPreventivoDialog(self, mantenimiento)
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def refrescar(self) -> None:
        self._recargar()
        self._render_secciones()
        self.update()


class PreventivoDialog(ft.AlertDialog):
    """Registro de nuevo mantenimiento preventivo."""

    def __init__(self, vista: MantenimientosView):
        super().__init__(modal=True)
        self.vista = vista
        self.dd_sku = ft.Dropdown(
            label="Equipo",
            options=[ft.dropdown.Option(asset.sku) for asset in vista.activos],
            width=260,
        )
        self.fecha_programada = ft.TextField(label="Fecha programada (YYYY-MM-DD)")
        self.estado_inicial = ft.TextField(label="Estado inicial")
        self.elementos = ft.TextField(label="Elementos a utilizar")
        self.observaciones = ft.TextField(label="Observaciones", multiline=True)
        self.responsable = ft.TextField(label="Responsable")
        self.usuario = ft.TextField(label="Usuario", value="sistemas")

        self.content = ft.Column(
            tight=True,
            spacing=8,
            controls=[
                ft.Text("Nuevo mantenimiento preventivo", size=18, weight=ft.FontWeight.W_600),
                self.dd_sku,
                self.fecha_programada,
                self.estado_inicial,
                self.elementos,
                self.observaciones,
                self.responsable,
                self.usuario,
            ],
        )
        self.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: self._cerrar()),
            ft.FilledButton("Guardar", icon=ft.Icons.SAVE, on_click=lambda e: self._guardar()),
        ]

    def _cerrar(self) -> None:
        self.open = False
        self.vista.page.update()

    def _guardar(self) -> None:
        if not self.dd_sku.value:
            self.vista.page.snack_bar = ft.SnackBar(ft.Text("Selecciona un equipo"), open=True)
            self.vista.page.update()
            return
        consecutivo = len(self.vista.mantenimientos) + 1
        mantenimiento = Mantenimiento(
            id_mto=f"MTO-{date.today().year}-{consecutivo:03d}",
            sku=self.dd_sku.value,
            tipo="PREVENTIVO",
            fecha_programada=self.fecha_programada.value or None,
            fecha_realizado=None,
            estado_inicial=self.estado_inicial.value or "",
            estado_final="",
            elementos_utilizados=self.elementos.value or "",
            observaciones=self.observaciones.value or "",
            responsable=self.responsable.value or "",
            usuario_registro=self.usuario.value or "sistemas",
        )
        self.vista.mantenimientos.append(mantenimiento)
        self.vista._guardar_mantenimientos()
        self.vista._actualizar_activo(mantenimiento.sku, fecha_prox=mantenimiento.fecha_programada)
        self.vista.refrescar()
        self._cerrar()


class CorrectivoDialog(ft.AlertDialog):
    """Registro de mantenimiento correctivo."""

    def __init__(self, vista: MantenimientosView):
        super().__init__(modal=True)
        self.vista = vista
        self.dd_sku = ft.Dropdown(
            label="Equipo",
            options=[ft.dropdown.Option(asset.sku) for asset in vista.activos],
            width=260,
        )
        self.fecha_realizado = ft.TextField(label="Fecha realizado (YYYY-MM-DD)", value=date.today().isoformat())
        self.estado_inicial = ft.TextField(label="Estado inicial")
        self.estado_final = ft.TextField(label="Estado final")
        self.elementos = ft.TextField(label="Elementos utilizados")
        self.observaciones = ft.TextField(label="Observaciones", multiline=True)
        self.responsable = ft.TextField(label="Responsable")
        self.usuario = ft.TextField(label="Usuario", value="sistemas")

        self.content = ft.Column(
            tight=True,
            spacing=8,
            controls=[
                ft.Text("Nuevo correctivo", size=18, weight=ft.FontWeight.W_600),
                self.dd_sku,
                self.fecha_realizado,
                self.estado_inicial,
                self.estado_final,
                self.elementos,
                self.observaciones,
                self.responsable,
                self.usuario,
            ],
        )
        self.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: self._cerrar()),
            ft.FilledButton("Guardar", icon=ft.Icons.SAVE, on_click=lambda e: self._guardar()),
        ]

    def _cerrar(self) -> None:
        self.open = False
        self.vista.page.update()

    def _guardar(self) -> None:
        if not self.dd_sku.value:
            self.vista.page.snack_bar = ft.SnackBar(ft.Text("Selecciona un equipo"), open=True)
            self.vista.page.update()
            return
        consecutivo = len(self.vista.mantenimientos) + 1
        mantenimiento = Mantenimiento(
            id_mto=f"MTO-{date.today().year}-{consecutivo:03d}",
            sku=self.dd_sku.value,
            tipo="CORRECTIVO",
            fecha_programada=None,
            fecha_realizado=self.fecha_realizado.value or date.today().isoformat(),
            estado_inicial=self.estado_inicial.value or "",
            estado_final=self.estado_final.value or "",
            elementos_utilizados=self.elementos.value or "",
            observaciones=self.observaciones.value or "",
            responsable=self.responsable.value or "",
            usuario_registro=self.usuario.value or "sistemas",
        )
        self.vista.mantenimientos.append(mantenimiento)
        self.vista._guardar_mantenimientos()
        self.vista._actualizar_activo(mantenimiento.sku, fecha_ultimo=mantenimiento.fecha_realizado)
        reportes.generar_pdf_mantenimiento(mantenimiento.id_mto, mantenimiento.to_dict())
        self.vista.refrescar()
        self._cerrar()


class AplazarDialog(ft.AlertDialog):
    """Dialogo para ajustar la fecha programada de un preventivo."""

    def __init__(self, vista: MantenimientosView, mantenimiento: Mantenimiento):
        super().__init__(modal=True)
        self.vista = vista
        self.mantenimiento = mantenimiento
        self.nueva_fecha = ft.TextField(label="Nueva fecha programada", value=mantenimiento.fecha_programada or "")
        self.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: self._cerrar()),
            ft.FilledButton("Guardar", icon=ft.Icons.SAVE, on_click=lambda e: self._guardar()),
        ]
        self.content = ft.Column(
            tight=True,
            spacing=8,
            controls=[
                ft.Text(f"Aplazar preventivo {mantenimiento.sku}", size=18, weight=ft.FontWeight.W_600),
                self.nueva_fecha,
            ],
        )

    def _cerrar(self) -> None:
        self.open = False
        self.vista.page.update()

    def _guardar(self) -> None:
        self.mantenimiento.fecha_programada = self.nueva_fecha.value or None
        self.vista._guardar_mantenimientos()
        self.vista._actualizar_activo(self.mantenimiento.sku, fecha_prox=self.mantenimiento.fecha_programada)
        self.vista.refrescar()
        self._cerrar()


class RegistrarPreventivoDialog(ft.AlertDialog):
    """Dialogo para concluir un preventivo pendiente."""

    def __init__(self, vista: MantenimientosView, mantenimiento: Mantenimiento):
        super().__init__(modal=True)
        self.vista = vista
        self.mantenimiento = mantenimiento
        self.fecha_realizado = ft.TextField(label="Fecha realizado", value=date.today().isoformat())
        self.estado_final = ft.TextField(label="Estado final")
        self.elementos = ft.TextField(label="Elementos utilizados", value=mantenimiento.elementos_utilizados)
        self.observaciones = ft.TextField(label="Observaciones", value=mantenimiento.observaciones, multiline=True)
        self.responsable = ft.TextField(label="Responsable", value=mantenimiento.responsable)

        self.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: self._cerrar()),
            ft.FilledButton("Registrar", icon=ft.Icons.CHECK, on_click=lambda e: self._guardar()),
        ]
        self.content = ft.Column(
            tight=True,
            spacing=8,
            controls=[
                ft.Text(f"Registrar preventivo {mantenimiento.sku}", size=18, weight=ft.FontWeight.W_600),
                self.fecha_realizado,
                self.estado_final,
                self.elementos,
                self.observaciones,
                self.responsable,
            ],
        )

    def _cerrar(self) -> None:
        self.open = False
        self.vista.page.update()

    def _guardar(self) -> None:
        self.mantenimiento.fecha_realizado = self.fecha_realizado.value or date.today().isoformat()
        self.mantenimiento.estado_final = self.estado_final.value or ""
        self.mantenimiento.elementos_utilizados = self.elementos.value or ""
        self.mantenimiento.observaciones = self.observaciones.value or ""
        self.mantenimiento.responsable = self.responsable.value or ""
        self.vista._guardar_mantenimientos()
        self.vista._actualizar_activo(self.mantenimiento.sku, fecha_ultimo=self.mantenimiento.fecha_realizado, fecha_prox=None)
        reportes.generar_pdf_mantenimiento(self.mantenimiento.id_mto, self.mantenimiento.to_dict())
        self.vista.refrescar()
        self._cerrar()


def build(page: ft.Page) -> ft.Control:
    """Entrada para la vista de mantenimientos."""

    return ft.Container(expand=True, padding=16, content=MantenimientosView(page))
