"""Generación de reportes en CSV/XLSX y PDF."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from . import reglas, storage

try:  # pragma: no cover - pandas es opcional
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # type: ignore


def _write_csv(path: Path, headers: list[str], rows: Iterable[dict[str, str]]) -> Path:
    storage.ensure_structure()
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in headers})
    return path


def _write_xlsx(path: Path, headers: list[str], rows: Iterable[dict[str, str]]) -> Path:
    if pd is None:
        raise RuntimeError("pandas no está disponible para exportar XLSX")
    frame = pd.DataFrame(list(rows), columns=headers)
    frame.to_excel(path, index=False)
    return path


def exportar_listado_por_departamento(formato: str = "csv") -> Path:
    activos = [asset.to_dict() for asset in reglas.cargar_activos()]
    headers = ["area", "departamento", "categoria", "sku", "marca", "modelo", "estado"]
    rows = [
        {
            "area": item["ubicacion_actual"]["area"],
            "departamento": item["ubicacion_actual"]["departamento"],
            "categoria": item["categoria"],
            "sku": item["sku"],
            "marca": item["marca"],
            "modelo": item["modelo"],
            "estado": item["estado"],
        }
        for item in activos
    ]
    target = storage.REPORTS_DIR / f"listado_departamento.{formato}"
    if formato == "csv":
        return _write_csv(target, headers, rows)
    return _write_xlsx(target, headers, rows)


def generar_pdf_entrega(entrega_id: str, equipos: list[dict[str, str]], datos: dict[str, str]) -> Path:
    path = storage.REPORTS_DIR / "entregas" / f"{entrega_id}.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph("Hospital Central - Formato de entrega", styles["Title"])]
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Entrega: {entrega_id}", styles["Heading2"]))
    story.append(Paragraph(f"Fecha: {datos.get('fecha', '')}", styles["Normal"]))
    story.append(Paragraph(f"Destino: {datos.get('area', '')} / {datos.get('depto', '')}", styles["Normal"]))
    story.append(Paragraph(f"Responsable: {datos.get('responsable', '')}", styles["Normal"]))
    story.append(Spacer(1, 12))
    headers = ["SKU", "Categoría", "Marca", "Modelo"]
    table_data = [headers]
    for item in equipos:
        table_data.append([
            item.get("sku", ""),
            item.get("categoria", ""),
            item.get("marca", ""),
            item.get("modelo", ""),
        ])
    tabla = Table(table_data, hAlign="LEFT")
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A73E8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F5F6F8")),
            ]
        )
    )
    story.append(tabla)
    story.append(Spacer(1, 24))
    story.append(Paragraph("Firmas:", styles["Heading3"]))
    story.append(Spacer(1, 48))
    story.append(Paragraph("__________________________    __________________________", styles["Normal"]))
    story.append(Paragraph("Sistemas                        Responsable", styles["Normal"]))
    doc.build(story)
    return path


def generar_pdf_mantenimiento(mto_id: str, datos: dict[str, str]) -> Path:
    path = storage.REPORTS_DIR / "mantenimientos" / f"{mto_id}.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph("Reporte de mantenimiento", styles["Title"])]
    for key, label in (
        ("sku", "SKU"),
        ("tipo", "Tipo"),
        ("fecha_programada", "Fecha programada"),
        ("fecha_realizado", "Fecha realizado"),
        ("estado_inicial", "Estado inicial"),
        ("estado_final", "Estado final"),
        ("elementos_utilizados", "Elementos"),
        ("observaciones", "Observaciones"),
        ("responsable", "Responsable"),
    ):
        story.append(Paragraph(f"{label}: {datos.get(key, '')}", styles["Normal"]))
        story.append(Spacer(1, 6))
    doc.build(story)
    return path
