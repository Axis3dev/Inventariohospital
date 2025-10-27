"""Módulo de utilidades para persistencia en archivos JSON y CSV."""
from __future__ import annotations

import csv
import json
import os
import shutil
import threading
from contextlib import contextmanager
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
BACKUP_DIR = DATA_DIR / "_backups"
LOCK_FILE = DATA_DIR / ".lock"
REPORTS_DIR = Path(__file__).resolve().parents[2] / "reports"

_lock = threading.RLock()


def ensure_structure() -> None:
    """Crea carpetas y archivos base si no existen."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "entregas").mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "mantenimientos").mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "sesiones").mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


@contextmanager
def data_lock() -> Iterable[None]:
    """Context manager para evitar escrituras concurrentes usando un lockfile."""

    with _lock:
        fd = os.open(str(LOCK_FILE), os.O_CREAT | os.O_RDWR)
        try:
            os.write(fd, str(os.getpid()).encode("utf-8"))
            yield
        finally:
            os.close(fd)
            try:
                LOCK_FILE.unlink()
            except FileNotFoundError:
                pass


def timestamp() -> str:
    """Devuelve timestamp ISO 8601."""

    return datetime.utcnow().replace(microsecond=0).isoformat()


def backup_data() -> Path:
    """Genera un respaldo zip de la carpeta data."""

    ensure_structure()
    stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    target = BACKUP_DIR / f"{stamp}.zip"
    shutil.make_archive(str(target.with_suffix("")), "zip", DATA_DIR)
    return target


def read_json(path: Path) -> Any:
    """Lee un archivo JSON con codificación UTF-8."""

    ensure_structure()
    if not path.exists():
        return [] if path.suffix == ".json" else {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, data: Any) -> None:
    """Escribe un objeto en JSON (UTF-8)."""

    ensure_structure()
    serializable = data
    if is_dataclass(data):
        serializable = asdict(data)
    elif isinstance(data, list) and data and is_dataclass(data[0]):
        serializable = [asdict(item) for item in data]
    with data_lock():
        with path.open("w", encoding="utf-8") as fh:
            json.dump(serializable, fh, ensure_ascii=False, indent=2)


def read_json_list(name: str) -> list[dict[str, Any]]:
    return list(read_json(DATA_DIR / name))


def write_json_list(name: str, data: list[dict[str, Any]]) -> None:
    write_json(DATA_DIR / name, data)


def append_csv(name: str, row: dict[str, Any]) -> None:
    """Agrega una fila a un CSV existente, creando encabezado si no existe."""

    ensure_structure()
    path = DATA_DIR / name
    exists = path.exists()
    with data_lock():
        with path.open("a", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=row.keys())
            if not exists:
                writer.writeheader()
            writer.writerow(row)


def read_csv(name: str) -> list[dict[str, Any]]:
    path = DATA_DIR / name
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def ensure_file(path: Path, default: Any) -> None:
    """Garantiza que un archivo exista; si no, lo crea con default."""

    if not path.exists():
        if path.suffix == ".json":
            write_json(path, default)
        else:
            ensure_structure()
            with path.open("w", encoding="utf-8") as fh:
                if isinstance(default, str):
                    fh.write(default)
                else:
                    fh.write("")


def seed_files() -> None:
    """Asegura que existan los archivos con valores iniciales."""

    ensure_structure()
    defaults = {
        "areas.json": ["Urgencias", "Hospitalización", "Quirófano", "Administración", "Imagenología"],
        "categorias.json": [
            {"categoria": "CPU", "prefijo": "CPU"},
            {"categoria": "MONITOR", "prefijo": "MON"},
            {"categoria": "TELEFONO", "prefijo": "TEL"},
            {"categoria": "CAMARA", "prefijo": "CAM"},
            {"categoria": "NBK", "prefijo": "NBK"},
        ],
        "departamentos.json": [],
        "assets.json": [],
        "mantenimientos.json": [],
        "entregas.json": [],
    }
    for name, default in defaults.items():
        ensure_file(DATA_DIR / name, default)
    for name in ("ingresos.csv", "egresos.csv", "movimientos.csv"):
        ensure_file(DATA_DIR / name, "")


seed_files()
