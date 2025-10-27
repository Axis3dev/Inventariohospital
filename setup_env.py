# setup_env.py
# Instalador automático de dependencias del sistema de inventario hospitalario

import subprocess
import sys


def install(package: str) -> None:
    print(f"🩺 Instalando {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def main() -> None:
    print("=== Instalador de entorno del Sistema de Inventario Hospitalario ===\n")
    required = [
        "flet>=0.24.0",
        "pandas>=2.0.0",
        "openpyxl>=3.1.0",
        "reportlab>=4.0.0",
        "python-slugify>=8.0.0",
    ]

    for pkg in required:
        try:
            install(pkg)
        except Exception as e:  # noqa: BLE001
            print(f"⚠️ Error instalando {pkg}: {e}")

    print("\n✅ Todas las dependencias han sido instaladas correctamente.")
    print("Para ejecutar el sistema usa:\n")
    print("    python start.py\n")


if __name__ == "__main__":
    main()
