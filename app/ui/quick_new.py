"""Formulario de alta rápida de equipos."""
from __future__ import annotations

from datetime import datetime

import flet as ft

from ..core import reglas, sku, storage
from ..core.modelos import Asset, Ubicacion

OBLIGATORIOS = [
    "categoria",
    "marca",
    "modelo",
    "numero_serie",
    "descripcion",
    "area",
    "departamento",
]


def quick_new_equipo(page: ft.Page) -> ft.Control:
    """Construye la vista para registrar rápidamente un equipo."""

    categorias_data = storage.read_json(storage.DATA_DIR / "categorias.json")
    categoria_nombres = [item.get("categoria", "") for item in categorias_data or [] if item.get("categoria")]
    if not categoria_nombres:
        categoria_nombres = ["CPU", "MONITOR", "TELEFONO", "CAMARA", "NBK"]

    areas = storage.read_json(storage.DATA_DIR / "areas.json") or [
        "Urgencias",
        "Hospitalización",
        "Quirófano",
        "Administración",
    ]
    departamentos = storage.read_json(storage.DATA_DIR / "departamentos.json") or [
        {"area": "Urgencias", "departamento": "Triage"},
    ]

    dd_categoria = ft.Dropdown(
        label="Categoría",
        options=[ft.dropdown.Option(valor) for valor in categoria_nombres],
        width=260,
    )
    in_marca = ft.TextField(label="Marca", width=260)
    in_modelo = ft.TextField(label="Modelo", width=260)
    in_serie = ft.TextField(label="Número de serie", width=260)
    in_descripcion = ft.TextField(label="Descripción", width=540, multiline=True, min_lines=2, max_lines=3)

    dd_area = ft.Dropdown(label="Área", options=[ft.dropdown.Option(area) for area in areas], width=260)
    dd_depto = ft.Dropdown(
        label="Departamento",
        options=[ft.dropdown.Option(item["departamento"]) for item in departamentos if item.get("departamento")],
        width=260,
    )

    mensaje = ft.Text("", color=ft.Colors.RED)

    def _actualizar_departamentos(area_sel: str | None) -> None:
        opciones = [
            ft.dropdown.Option(item["departamento"])
            for item in departamentos
            if item.get("area") == area_sel and item.get("departamento")
        ]
        if not opciones:
            opciones = [ft.dropdown.Option(item["departamento"]) for item in departamentos if item.get("departamento")]
        dd_depto.options = opciones
        if opciones:
            primera = opciones[0]
            dd_depto.value = primera.key if getattr(primera, "key", None) is not None else getattr(primera, "text", None)
        page.update()

    def _limpiar_campos() -> None:
        for control in (dd_categoria, in_marca, in_modelo, in_serie, in_descripcion, dd_area, dd_depto):
            if isinstance(control, ft.TextField):
                control.value = ""
            else:
                control.value = None
        mensaje.value = ""
        page.update()

    def _generar_sku(categoria: str) -> str:
        try:
            return sku.siguiente_sku(categoria)
        except Exception:  # noqa: BLE001
            prefijo = categoria[:3].upper() or "EQP"
            consecutivo = len(reglas.cargar_activos()) + 1
            return f"{prefijo}-{datetime.utcnow().year}-{consecutivo:04d}"

    def _guardar_equipo(_: ft.ControlEvent) -> None:
        datos = {
            "categoria": dd_categoria.value,
            "marca": in_marca.value,
            "modelo": in_modelo.value,
            "numero_serie": in_serie.value,
            "descripcion": in_descripcion.value,
            "area": dd_area.value,
            "departamento": dd_depto.value,
        }
        faltantes = [campo for campo in OBLIGATORIOS if not datos.get(campo)]
        if faltantes:
            mensaje.value = f"Faltan campos: {', '.join(faltantes)}"
            page.update()
            return

        activos = reglas.cargar_activos()
        if any(asset.numero_serie.lower() == datos["numero_serie"].lower() for asset in activos if datos["numero_serie"]):
            mensaje.value = "Número de serie duplicado. Confirma antes de continuar."
            page.update()
            return

        nuevo_asset = Asset(
            categoria=datos["categoria"],
            marca=datos["marca"],
            modelo=datos["modelo"],
            numero_serie=datos["numero_serie"],
            descripcion=datos["descripcion"],
            estado="OPERATIVO",
            ubicacion_actual=Ubicacion(area=datos["area"], departamento=datos["departamento"]),
            fecha_ingreso=datetime.utcnow().date().isoformat(),
            sku=_generar_sku(datos["categoria"]),
        )

        try:
            nuevo_asset.validar()
        except Exception as exc:  # noqa: BLE001
            mensaje.value = str(exc)
            page.update()
            return

        activos.append(nuevo_asset)
        reglas.guardar_activos(activos)
        reglas.registrar_ingreso(nuevo_asset, usuario="sistemas", nota="Alta rápida")

        page.snack_bar = ft.SnackBar(ft.Text(f"Equipo {nuevo_asset.sku} agregado correctamente"), open=True)
        _limpiar_campos()

    dd_area.on_change = lambda e: _actualizar_departamentos(e.control.value)

    formulario = ft.Column(
        spacing=12,
        controls=[
            ft.Row(spacing=12, controls=[dd_categoria, in_marca, in_modelo]),
            ft.Row(spacing=12, controls=[in_serie, dd_area, dd_depto]),
            in_descripcion,
            ft.Row(
                spacing=12,
                controls=[
                    ft.FilledButton("Guardar equipo", icon=ft.Icons.SAVE, on_click=_guardar_equipo),
                    ft.TextButton("Limpiar", on_click=lambda _e: _limpiar_campos()),
                ],
            ),
            mensaje,
        ],
    )

    return ft.Container(expand=True, padding=16, content=formulario)
