# Inventario TI Hospitalario

Aplicación de escritorio construida con [Flet](https://flet.dev/) para controlar el inventario de tecnología en un hospital. El sistema utiliza archivos JSON y CSV para la persistencia y puede empaquetarse mediante PyInstaller.

## Instalación rápida

1. Ejecuta el instalador de dependencias:
   ```bash
   python setup_env.py
   ```
2. Inicia la aplicación:
   ```bash
   python start.py
   ```

### O alternativamente:

```bash
python -m app.main
```

## Requisitos

- Python 3.11
- Pip

Instalación de dependencias manual:

```bash
pip install -r requirements.txt
```

La aplicación abre una ventana con la interfaz hospitalaria, navegación lateral y vistas para dashboard, inventario, entregas, mantenimientos, reportes y configuración.

## Empaquetado con PyInstaller

```bash
pip install pyinstaller
pyinstaller --name inventario_hospital --noconfirm --windowed app/main.py
```

## Estructura de datos

Los datos se guardan en la carpeta `data/` y se inicializan automáticamente si no existen.

- `assets.json`: catálogo de equipos.
- `categorias.json`, `areas.json`, `departamentos.json`: catálogos.
- `ingresos.csv`, `egresos.csv`, `movimientos.csv`: kardex.
- `mantenimientos.json`, `entregas.json`: registros operativos.
- `sesiones/`: resultados de importaciones TXT.
- `_backups/`: respaldos automáticos antes de importaciones.

Reportes y PDFs se generan en la carpeta `reports/`.

## Datos de prueba

Se incluyen catálogos base de áreas, departamentos y categorías en `data/`. Para agregar equipos de prueba utilice la vista **Inventario** con el botón “+ Alta”.

## Sesión de importación de ejemplo

Cree un archivo `data/sesiones/ejemplo.txt` con SKUs uno por línea y utilice la opción de importación dentro de la vista Inventario (la lógica de importación se encuentra en `app/core/importador.py`). Cada importación genera un respaldo (`data/_backups/<fecha>.zip`) y guarda un resumen en `data/sesiones/<fecha-area-depto>/` con `import.json` y `diferencias.csv`.

## Bloqueo y backups

Antes de escribir en archivos CSV/JSON se utiliza un lockfile (`data/.lock`) para evitar concurrencia. Las importaciones generan un respaldo automático de `data/` en `data/_backups/YYYYMMDD-HHMMSS.zip`.
