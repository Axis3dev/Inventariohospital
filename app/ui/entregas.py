"""Gestión de entregas agrupadas por estatus pendiente."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime

import flet as ft

from ..core import reglas, reportes, storage
from ..core.modelos import Entrega, Ubicacion


class EntregasView(ft.Column):
    """Vista completa para atender entregas."""

    def __init__(self, page: ft.Page):
        super().__init__(expand=True, spacing=16, scroll=ft.ScrollMode.AUTO)
        self.page = page
        self.file_picker = ft.FilePicker(on_result=self._resolver_adjuntar)
        if self.file_picker not in page.overlay:
            page.overlay.append(self.file_picker)
        self.entrega_por_adjuntar: Entrega | None = None

        self._recargar_datos()
        self._renderizar()

    # ------------------------------------------------------------------
    def _recargar_datos(self) -> None:
        self.activos = reglas.cargar_activos()
        self.entregas = [Entrega.from_dict(item) for item in storage.read_json_list("entregas.json")]

    def _renderizar(self) -> None:
        self.controls = [
            self._seccion_pendientes_por_entregar(),
            self._seccion_entregas_pendientes(),
            self._seccion_historico(),
        ]
        self.page.update()

    # ------------------------------------------------------------------
    def _seccion_pendientes_por_entregar(self) -> ft.Control:
        grupos: dict[tuple[str, str], list] = defaultdict(list)
        for asset in self.activos:
            if asset.estatus == "PENDIENTE_ENTREGA":
                key = (asset.ubicacion_actual.area, asset.ubicacion_actual.departamento)
                grupos[key].append(asset)

        tarjetas = []
        for (area, depto), assets in grupos.items():
            lista = ft.Column(
                spacing=6,
                controls=[ft.Text(asset.sku) for asset in assets],
            )
            tarjetas.append(
                ft.Container(
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    padding=16,
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Text(f"{area} / {depto}", size=18, weight=ft.FontWeight.W_600),
                            ft.Text(f"Equipos pendientes: {len(assets)}"),
                            lista,
                            ft.FilledButton(
                                "Generar entrega",
                                icon=ft.Icons.LOCAL_SHIPPING,
                                on_click=lambda _e, info=(area, depto, assets): self._abrir_generacion(info),
                            ),
                        ],
                    ),
                )
            )

        if not tarjetas:
            tarjetas.append(ft.Text("No hay equipos pendientes de entrega", color=ft.Colors.GREY))

        return ft.Container(
            bgcolor=ft.Colors.GREY_50,
            border_radius=12,
            padding=16,
            content=ft.Column(
                spacing=12,
                controls=[ft.Text("Pendientes por entregar", size=20, weight=ft.FontWeight.W_700)] + tarjetas,
            ),
        )

    def _seccion_entregas_pendientes(self) -> ft.Control:
        pendientes = [entrega for entrega in self.entregas if entrega.estado_entrega == "PENDIENTE"]
        tarjetas = [self._tarjeta_entrega(entrega) for entrega in pendientes]
        if not tarjetas:
            tarjetas = [ft.Text("Sin entregas en proceso", color=ft.Colors.GREY)]
        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            padding=16,
            content=ft.Column(
                spacing=12,
                controls=[ft.Text("Entregas registradas", size=20, weight=ft.FontWeight.W_700)] + tarjetas,
            ),
        )

    def _seccion_historico(self) -> ft.Control:
        historico = [entrega for entrega in self.entregas if entrega.estado_entrega == "ENTREGADO"]
        tarjetas = [self._tarjeta_entrega(entrega, editable=False) for entrega in historico]
        if not tarjetas:
            tarjetas = [ft.Text("Sin historial", color=ft.Colors.GREY)]
        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            padding=16,
            content=ft.Column(
                spacing=12,
                controls=[ft.Text("Histórico", size=20, weight=ft.FontWeight.W_700)] + tarjetas,
            ),
        )

    def _tarjeta_entrega(self, entrega: Entrega, editable: bool = True) -> ft.Control:
        resumen = ft.Column(
            spacing=4,
            controls=[
                ft.Text(f"ID: {entrega.id_entrega}", weight=ft.FontWeight.W_600),
                ft.Text(f"Fecha: {entrega.fecha}"),
                ft.Text(f"Destino: {entrega.destino_area} / {entrega.destino_depto}"),
                ft.Text(f"Equipos: {', '.join(entrega.equipos)}"),
                ft.Text(f"Estado: {entrega.estado_entrega}"),
                ft.Text(f"PDF: {entrega.pdf or 'Sin generar'}", selectable=True),
            ],
        )

        acciones: list[ft.Control] = []
        if editable:
            acciones.append(
                ft.OutlinedButton(
                    "Generar PDF",
                    icon=ft.Icons.PICTURE_AS_PDF,
                    on_click=lambda _e, ent=entrega: self._generar_pdf(ent),
                )
            )
            acciones.append(
                ft.FilledButton(
                    "Adjuntar PDF firmado",
                    icon=ft.Icons.UPLOAD_FILE,
                    on_click=lambda _e, ent=entrega: self._adjuntar_pdf(ent),
                )
            )

        controles = [resumen]
        if acciones:
            controles.append(ft.Column(spacing=8, controls=acciones))

        return ft.Container(
            bgcolor=ft.Colors.GREY_50,
            border_radius=12,
            padding=16,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=controles,
            ),
        )

    # ------------------------------------------------------------------
    def _abrir_generacion(self, info: tuple[str, str, list]) -> None:
        area, depto, assets = info
        dialog = GenerarEntregaDialog(self, area, depto, assets)
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _generar_pdf(self, entrega: Entrega) -> None:
        activos = {asset.sku: asset.to_dict() for asset in self.activos}
        equipos = [activos.get(sku, {"sku": sku}) for sku in entrega.equipos]
        ruta = reportes.generar_pdf_entrega(
            entrega.id_entrega,
            equipos,
            {
                "fecha": entrega.fecha,
                "area": entrega.destino_area,
                "depto": entrega.destino_depto,
                "responsable": entrega.responsable,
            },
        )
        entrega.pdf = str(ruta)
        self._guardar_entregas()
        self.page.snack_bar = ft.SnackBar(ft.Text(f"PDF generado en {ruta}"), open=True)
        self.page.update()

    def _adjuntar_pdf(self, entrega: Entrega) -> None:
        self.entrega_por_adjuntar = entrega
        self.file_picker.pick_files(allow_multiple=False, allowed_extensions=["pdf"])

    def _resolver_adjuntar(self, evento: ft.FilePickerResultEvent) -> None:
        if not self.entrega_por_adjuntar or not evento.files:
            self.entrega_por_adjuntar = None
            return
        entrega = self.entrega_por_adjuntar
        entrega.pdf = evento.files[0].path
        entrega.estado_entrega = "ENTREGADO"

        for asset in self.activos:
            if asset.sku in entrega.equipos:
                origen = (asset.ubicacion_actual.area, asset.ubicacion_actual.departamento)
                asset.estatus = "OPERATIVO"
                destino = (entrega.destino_area, entrega.destino_depto)
                asset.ubicacion_actual = Ubicacion(area=destino[0], departamento=destino[1])
                reglas.registrar_movimiento(asset, origen, destino, usuario="sistemas", nota="Entrega")

        reglas.guardar_activos(self.activos)
        self._guardar_entregas()
        self.page.snack_bar = ft.SnackBar(ft.Text("Entrega marcada como ENTREGADO"), open=True)
        self.entrega_por_adjuntar = None
        self._recargar_datos()
        self._renderizar()

    def _guardar_entregas(self) -> None:
        storage.write_json(storage.DATA_DIR / "entregas.json", [entrega.to_dict() for entrega in self.entregas])


class GenerarEntregaDialog(ft.AlertDialog):
    """Dialogo para crear una entrega a partir de un grupo."""

    def __init__(self, vista: EntregasView, area: str, depto: str, assets: list):
        super().__init__(modal=True)
        self.vista = vista
        self.area = area
        self.depto = depto
        self.assets = assets

        self.txt_responsable = ft.TextField(label="Responsable de recepción")
        self.txt_usuario = ft.TextField(label="Capturista", value="sistemas")

        lista = ft.Column(spacing=4, controls=[ft.Text(asset.sku) for asset in assets])

        self.content = ft.Column(
            tight=True,
            spacing=10,
            controls=[
                ft.Text(f"Nueva entrega para {area} / {depto}", size=18, weight=ft.FontWeight.W_600),
                ft.Text(f"Equipos incluidos: {len(assets)}"),
                lista,
                self.txt_responsable,
                self.txt_usuario,
            ],
        )
        self.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: self._cerrar()),
            ft.FilledButton("Crear entrega", icon=ft.Icons.SAVE, on_click=lambda e: self._guardar()),
        ]

    def _cerrar(self) -> None:
        self.open = False
        self.vista.page.update()

    def _guardar(self) -> None:
        responsable = (self.txt_responsable.value or "").strip()
        if not responsable:
            self.vista.page.snack_bar = ft.SnackBar(ft.Text("Captura el responsable"), open=True)
            self.vista.page.update()
            return

        nuevo_id = self._generar_id()
        entrega = Entrega(
            id_entrega=nuevo_id,
            fecha=datetime.utcnow().date().isoformat(),
            destino_area=self.area,
            destino_depto=self.depto,
            equipos=[asset.sku for asset in self.assets],
            estado_entrega="PENDIENTE",
            responsable=responsable,
            usuario=self.txt_usuario.value or "sistemas",
            pdf=None,
        )
        self.vista.entregas.append(entrega)
        self.vista._guardar_entregas()
        self.vista._recargar_datos()
        self.vista._renderizar()
        self._cerrar()

    def _generar_id(self) -> str:
        year = datetime.utcnow().year
        consecutivo = sum(1 for ent in self.vista.entregas if ent.id_entrega.startswith(f"ENT-{year}")) + 1
        return f"ENT-{year}-{consecutivo:04d}"


def build(page: ft.Page) -> ft.Control:
    """Entrada de la vista de entregas."""

    return ft.Container(expand=True, padding=16, content=EntregasView(page))
