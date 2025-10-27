"""Vista de configuración y catálogos."""
from __future__ import annotations

import flet as ft

from ..core import storage
from ..theme import card, primary_button


class ConfigView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(spacing=16, scroll=ft.ScrollMode.AUTO)
        self.page = page
        self.areas = storage.read_json_list("areas.json")
        self.categorias = storage.read_json_list("categorias.json")
        self.departamentos = storage.read_json_list("departamentos.json")
        self.controls = [
            card(ft.Text("Áreas", weight=ft.FontWeight.BOLD), self._lista_simple("areas")),
            card(ft.Text("Categorías", weight=ft.FontWeight.BOLD), self._lista_categorias()),
        ]

    def _lista_simple(self, tipo: str) -> ft.Control:
        lista = ft.ListView(expand=1, spacing=4)
        datos = getattr(self, tipo)
        for elemento in datos:
            lista.controls.append(ft.Text(elemento))
        campo = ft.TextField(label="Nuevo elemento")
        boton = primary_button("Agregar", lambda e, t=tipo, campo=campo: self._agregar_simple(t, campo))
        return ft.Column([lista, campo, boton], spacing=8)

    def _lista_categorias(self) -> ft.Control:
        lista = ft.ListView(expand=1, spacing=4)
        for cat in self.categorias:
            lista.controls.append(ft.Text(f"{cat['categoria']} ({cat['prefijo']})"))
        nombre = ft.TextField(label="Categoría")
        prefijo = ft.TextField(label="Prefijo")
        boton = primary_button("Agregar", lambda e: self._agregar_categoria(nombre, prefijo))
        return ft.Column([lista, nombre, prefijo, boton], spacing=8)

    def _agregar_simple(self, tipo: str, campo: ft.TextField) -> None:
        valor = campo.value.strip()
        if not valor:
            self._mensaje("Debe capturar un valor")
            return
        datos = getattr(self, tipo)
        if valor in datos:
            self._mensaje("Ya existe")
            return
        datos.append(valor)
        storage.write_json(storage.DATA_DIR / f"{tipo}.json", datos)
        campo.value = ""
        self._mensaje("Guardado")
        self.page.update()

    def _agregar_categoria(self, nombre: ft.TextField, prefijo: ft.TextField) -> None:
        if not nombre.value or not prefijo.value:
            self._mensaje("Debe capturar categoría y prefijo")
            return
        if any(cat["categoria"] == nombre.value for cat in self.categorias):
            self._mensaje("La categoría ya existe")
            return
        self.categorias.append({"categoria": nombre.value, "prefijo": prefijo.value})
        storage.write_json(storage.DATA_DIR / "categorias.json", self.categorias)
        nombre.value = ""
        prefijo.value = ""
        self._mensaje("Guardado")
        self.page.update()

    def _mensaje(self, texto: str) -> None:
        self.page.snack_bar = ft.SnackBar(ft.Text(texto))
        self.page.snack_bar.open = True
        self.page.update()


def build(page: ft.Page) -> ft.Control:
    return ConfigView(page)
