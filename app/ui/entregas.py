"""Vista de entregas de equipos."""
from __future__ import annotations

from datetime import date
import flet as ft

from ..core import reglas, reportes, storage
from ..core.modelos import Entrega
from ..theme import card, flat_button, primary_button


class EntregasView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(spacing=16, scroll=ft.ScrollMode.AUTO)
        self.page = page
        self.entregas = [Entrega.from_dict(item) for item in storage.read_json_list("entregas.json")]
        self.controls = [
            card(primary_button("Nueva entrega", self._abrir_dialogo, icon=ft.Icons.LOCAL_SHIPPING)),
            self._seccion_pendientes(),
            self._seccion_historico(),
        ]

    def _seccion_pendientes(self) -> ft.Control:
        pendientes = [entrega for entrega in self.entregas if entrega.estado_entrega == "PENDIENTE"]
        filas = [self._fila_entrega(entrega) for entrega in pendientes] or [ft.Text("Sin entregas pendientes")]
        return card(ft.Text("Pendientes", weight=ft.FontWeight.BOLD), *filas)

    def _seccion_historico(self) -> ft.Control:
        historico = [entrega for entrega in self.entregas if entrega.estado_entrega != "PENDIENTE"]
        filas = [self._fila_entrega(entrega) for entrega in historico] or [ft.Text("Sin historial disponible")]
        return card(ft.Text("Histórico", weight=ft.FontWeight.BOLD), *filas)

    def _fila_entrega(self, entrega: Entrega) -> ft.Control:
        return ft.ListTile(
            title=ft.Text(f"{entrega.id_entrega} - {entrega.destino_area}/{entrega.destino_depto}"),
            subtitle=ft.Text(f"Equipos: {', '.join(entrega.equipos)}"),
            trailing=flat_button(
                "Generar PDF",
                lambda e, entrega=entrega: self._generar_pdf(entrega),
                icon=ft.Icons.PICTURE_AS_PDF,
            ),
        )

    def _abrir_dialogo(self, e: ft.ControlEvent | None = None) -> None:  # noqa: ARG002
        dialog = NuevaEntregaDialog(self)
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _generar_pdf(self, entrega: Entrega) -> None:
        activos = {asset.sku: asset.to_dict() for asset in reglas.cargar_activos()}
        equipos = [activos.get(sku, {"sku": sku}) for sku in entrega.equipos]
        ruta = reportes.generar_pdf_entrega(entrega.id_entrega, equipos, {
            "fecha": entrega.fecha,
            "area": entrega.destino_area,
            "depto": entrega.destino_depto,
            "responsable": entrega.responsable,
        })
        self.page.snack_bar = ft.SnackBar(ft.Text(f"PDF generado en {ruta}"))
        self.page.snack_bar.open = True
        self.page.update()

    def recargar(self) -> None:
        self.entregas = [Entrega.from_dict(item) for item in storage.read_json_list("entregas.json")]
        self.controls[1] = self._seccion_pendientes()
        self.controls[2] = self._seccion_historico()
        self.update()


class NuevaEntregaDialog(ft.AlertDialog):
    def __init__(self, vista: EntregasView):
        super().__init__(modal=True)
        self.vista = vista
        self.destino_area = ft.TextField(label="Área destino")
        self.destino_depto = ft.TextField(label="Departamento destino")
        self.equipos = ft.TextField(label="SKUs (separados por coma)")
        self.responsable = ft.TextField(label="Responsable")
        self.usuario = ft.TextField(label="Usuario")
        self.actions = [flat_button("Cancelar", self._cerrar), primary_button("Guardar", self._guardar)]
        self.content = ft.Column(
            [self.destino_area, self.destino_depto, self.equipos, self.responsable, self.usuario],
            tight=True,
            spacing=8,
        )

    def _cerrar(self, e: ft.ControlEvent | None = None) -> None:  # noqa: ARG002
        self.open = False
        self.vista.page.update()

    def _guardar(self, e: ft.ControlEvent | None = None) -> None:  # noqa: ARG002
        try:
            equipos = [sku.strip() for sku in self.equipos.value.split(",") if sku.strip()]
            if not equipos:
                raise ValueError("Debe capturar al menos un SKU")
            idx = len(self.vista.entregas) + 1
            entrega_id = f"ENT-{date.today().year}-{idx:04d}"
            entrega = Entrega(
                id_entrega=entrega_id,
                fecha=date.today().isoformat(),
                destino_area=self.destino_area.value,
                destino_depto=self.destino_depto.value,
                equipos=equipos,
                estado_entrega="PENDIENTE",
                responsable=self.responsable.value,
                usuario=self.usuario.value,
            )
            data = [item for item in storage.read_json_list("entregas.json")]
            data.append(entrega.to_dict())
            storage.write_json(storage.DATA_DIR / "entregas.json", data)
            self.vista.recargar()
            self.vista.page.snack_bar = ft.SnackBar(ft.Text("Entrega registrada"))
            self.vista.page.snack_bar.open = True
        except Exception as exc:  # noqa: BLE001
            self.vista.page.snack_bar = ft.SnackBar(ft.Text(str(exc)))
            self.vista.page.snack_bar.open = True
        finally:
            self.open = False
            self.vista.page.update()


def build(page: ft.Page) -> ft.Control:
    return EntregasView(page)
