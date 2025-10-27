# start.py
# Arranque principal del sistema de inventario hospitalario (Flet)

import flet as ft

try:
    from app.main import main
except Exception as e:  # noqa: BLE001
    raise RuntimeError(
        "Error al importar app.main.main(page). "
        "Asegúrate de que el paquete 'app' tenga __init__.py y que la función main(page) exista."
    ) from e

if __name__ == "__main__":
    ft.app(target=main)
