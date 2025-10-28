"""Vista sencilla para importar sesiones desde TXT."""
from __future__ import annotations

import flet as ft

from ..core import importador


def importar_txt_view(page: ft.Page) -> ft.Control:
    """Permite seleccionar un archivo TXT y ejecutar la importación."""

    info = ft.Text("", selectable=True)
    area = ft.TextField(label="Área destino", width=260)
    depto = ft.TextField(label="Departamento destino", width=260)

    def _pick_result(event: ft.FilePickerResultEvent) -> None:
        if not event.files:
            return
        if not area.value or not depto.value:
            info.value = "Captura área y departamento antes de importar"
            page.update()
            return
        path = event.files[0].path
        ok, resumen = importador.importar_sesion(path, area.value, depto.value, usuario="sistemas")
        info.value = resumen if ok else f"Error: {resumen}"
        page.snack_bar = ft.SnackBar(ft.Text("Importación completada" if ok else "No se pudo importar"), open=True)
        page.update()

    picker = ft.FilePicker(on_result=_pick_result)
    if picker not in page.overlay:
        page.overlay.append(picker)
        page.update()

    def _abrir_picker(_: ft.ControlEvent) -> None:
        if not area.value or not depto.value:
            info.value = "Captura área y departamento antes de importar"
            page.update()
            return
        picker.pick_files(allow_multiple=False, allowed_extensions=["txt"])

    controls = ft.Column(
        spacing=12,
        controls=[
            ft.Row(spacing=12, controls=[area, depto, ft.FilledButton("Seleccionar TXT", icon=ft.Icons.UPLOAD_FILE, on_click=_abrir_picker)]),
            info,
        ],
    )

    return ft.Container(expand=True, padding=16, content=controls)
