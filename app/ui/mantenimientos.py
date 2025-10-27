"""Vista de mantenimientos preventivos y correctivos."""
from __future__ import annotations

from datetime import date

import flet as ft

from ..core import reglas, reportes, storage
from ..core.modelos import Mantenimiento
from ..theme import card, flat_button, get_icon, primary_button


class MantenimientosView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(spacing=16, scroll=ft.ScrollMode.AUTO)
        self.page = page
        self.tab = ft.Tabs(
            tabs=[
                ft.Tab(text="Preventivos", content=self._preventivos()),
                ft.Tab(text="Correctivos", content=self._correctivos()),
                ft.Tab(text="Historial", content=self._historial()),
            ]
        )
        self.controls = [self.tab]

    def _cargar(self) -> list[Mantenimiento]:
        return [Mantenimiento.from_dict(item) for item in storage.read_json_list("mantenimientos.json")]

    def _preventivos(self) -> ft.Control:
        mantenimientos = [m for m in self._cargar() if m.tipo == "PREVENTIVO"]
        filas = []
        for mto in mantenimientos:
            texto = f"{mto.sku} - Programado: {mto.fecha_programada or 'Sin fecha'}"
            filas.append(
                ft.ListTile(
                    title=ft.Text(texto),
                    subtitle=ft.Text(mto.observaciones),
                    trailing=primary_button("PDF", lambda e, m=mto: self._pdf(m)),
                )
            )
        if not filas:
            filas = [ft.Text("Sin mantenimientos preventivos")]
        return card(*filas)

    def _correctivos(self) -> ft.Control:
        boton = primary_button("Nuevo correctivo", self._nuevo_correctivo, icon=get_icon("BUILD"))
        return card(boton)

    def _historial(self) -> ft.Control:
        filas = []
        for mto in self._cargar():
            filas.append(
                ft.ListTile(
                    title=ft.Text(f"{mto.id_mto} - {mto.sku}"),
                    subtitle=ft.Text(f"{mto.tipo} - {mto.fecha_realizado or mto.fecha_programada}"),
                    trailing=flat_button("PDF", lambda e, m=mto: self._pdf(m)),
                )
            )
        if not filas:
            filas = [ft.Text("No hay historial")]
        return card(*filas)

    def _pdf(self, mto: Mantenimiento) -> None:
        ruta = reportes.generar_pdf_mantenimiento(mto.id_mto, mto.to_dict())
        self.page.snack_bar = ft.SnackBar(ft.Text(f"PDF generado en {ruta}"))
        self.page.snack_bar.open = True
        self.page.update()

    def _nuevo_correctivo(self, _=None) -> None:
        dialog = CorrectivoDialog(self)
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def refrescar(self) -> None:
        self.tab.tabs[0].content = self._preventivos()
        self.tab.tabs[2].content = self._historial()
        self.update()


class CorrectivoDialog(ft.AlertDialog):
    def __init__(self, vista: MantenimientosView):
        super().__init__(modal=True)
        self.vista = vista
        self.sku = ft.TextField(label="SKU")
        self.estado_inicial = ft.TextField(label="Estado inicial")
        self.estado_final = ft.TextField(label="Estado final")
        self.elementos = ft.TextField(label="Elementos utilizados")
        self.observaciones = ft.TextField(label="Observaciones", multiline=True)
        self.responsable = ft.TextField(label="Responsable")
        self.usuario = ft.TextField(label="Usuario")
        self.actions = [flat_button("Cancelar", self._cerrar), primary_button("Guardar", self._guardar)]
        self.content = ft.Column(
            [
                self.sku,
                self.estado_inicial,
                self.estado_final,
                self.elementos,
                self.observaciones,
                self.responsable,
                self.usuario,
            ],
            tight=True,
            spacing=8,
        )

    def _cerrar(self, _=None) -> None:
        self.open = False
        self.vista.page.update()

    def _guardar(self, _=None) -> None:
        try:
            if not self.sku.value:
                raise ValueError("Debe indicar un SKU")
            data = storage.read_json_list("mantenimientos.json")
            consecutivo = len(data) + 1
            mto = Mantenimiento(
                id_mto=f"MTO-{date.today().year}-{consecutivo:03d}",
                sku=self.sku.value,
                tipo="CORRECTIVO",
                fecha_programada=None,
                fecha_realizado=date.today().isoformat(),
                estado_inicial=self.estado_inicial.value,
                estado_final=self.estado_final.value,
                elementos_utilizados=self.elementos.value,
                observaciones=self.observaciones.value,
                responsable=self.responsable.value,
                usuario_registro=self.usuario.value,
            )
            data.append(mto.to_dict())
            storage.write_json(storage.DATA_DIR / "mantenimientos.json", data)
            self.vista.refrescar()
            self.vista.page.snack_bar = ft.SnackBar(ft.Text("Correctivo registrado"))
            self.vista.page.snack_bar.open = True
        except Exception as exc:  # noqa: BLE001
            self.vista.page.snack_bar = ft.SnackBar(ft.Text(str(exc)))
            self.vista.page.snack_bar.open = True
        finally:
            self.open = False
            self.vista.page.update()


def build(page: ft.Page) -> ft.Control:
    return MantenimientosView(page)
