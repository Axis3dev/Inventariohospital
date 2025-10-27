"""Modelos de datos principales del sistema."""
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import date
from typing import Any, ClassVar

SKU_REGEX = re.compile(r"^[A-Z]{3}-\d{4}-\d{4}$")
ESTADOS_DEFECTO = [
    "OPERATIVO",
    "EN_REPARACION",
    "BAJA",
    "PRESTADO",
    "RESGUARDO",
    "EXTRAVIADO",
]


@dataclass
class Ubicacion:
    area: str
    departamento: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Ubicacion":
        return cls(area=data.get("area", ""), departamento=data.get("departamento", ""))

    def to_dict(self) -> dict[str, str]:
        return {"area": self.area, "departamento": self.departamento}


@dataclass
class Asset:
    categoria: str
    marca: str
    modelo: str
    numero_serie: str
    descripcion: str
    estado: str
    ubicacion_actual: Ubicacion
    fecha_ingreso: str
    sku: str = ""
    id_interno: str = field(default_factory=lambda: str(uuid.uuid4()))
    fecha_ultimo_mto: str | None = None
    fecha_prox_mto: str | None = None
    etiqueta_impresa: bool = False

    catalogo_estados: ClassVar[list[str]] = ESTADOS_DEFECTO

    def validar(self) -> None:
        if self.estado not in self.catalogo_estados:
            raise ValueError("Estado inválido para el equipo.")
        if not self.categoria:
            raise ValueError("La categoría es obligatoria.")
        if not self.marca:
            raise ValueError("La marca es obligatoria.")
        if not self.modelo:
            raise ValueError("El modelo es obligatorio.")
        if not self.numero_serie:
            raise ValueError("El número de serie es obligatorio.")
        if self.sku and not SKU_REGEX.match(self.sku):
            raise ValueError("El SKU no cumple con el formato requerido.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "sku": self.sku,
            "id_interno": self.id_interno,
            "categoria": self.categoria,
            "marca": self.marca,
            "modelo": self.modelo,
            "numero_serie": self.numero_serie,
            "fecha_ingreso": self.fecha_ingreso,
            "descripcion": self.descripcion,
            "estado": self.estado,
            "ubicacion_actual": self.ubicacion_actual.to_dict(),
            "fecha_ultimo_mto": self.fecha_ultimo_mto,
            "fecha_prox_mto": self.fecha_prox_mto,
            "etiqueta_impresa": self.etiqueta_impresa,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Asset":
        return cls(
            sku=data.get("sku", ""),
            id_interno=data.get("id_interno", str(uuid.uuid4())),
            categoria=data.get("categoria", ""),
            marca=data.get("marca", ""),
            modelo=data.get("modelo", ""),
            numero_serie=data.get("numero_serie", ""),
            fecha_ingreso=data.get("fecha_ingreso", date.today().isoformat()),
            descripcion=data.get("descripcion", ""),
            estado=data.get("estado", ESTADOS_DEFECTO[0]),
            ubicacion_actual=Ubicacion.from_dict(data.get("ubicacion_actual", {})),
            fecha_ultimo_mto=data.get("fecha_ultimo_mto"),
            fecha_prox_mto=data.get("fecha_prox_mto"),
            etiqueta_impresa=data.get("etiqueta_impresa", False),
        )


@dataclass
class Entrega:
    id_entrega: str
    fecha: str
    destino_area: str
    destino_depto: str
    equipos: list[str]
    estado_entrega: str
    responsable: str
    usuario: str
    pdf: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id_entrega": self.id_entrega,
            "fecha": self.fecha,
            "destino_area": self.destino_area,
            "destino_depto": self.destino_depto,
            "equipos": self.equipos,
            "estado_entrega": self.estado_entrega,
            "pdf": self.pdf,
            "responsable": self.responsable,
            "usuario": self.usuario,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Entrega":
        return cls(
            id_entrega=data.get("id_entrega", ""),
            fecha=data.get("fecha", date.today().isoformat()),
            destino_area=data.get("destino_area", ""),
            destino_depto=data.get("destino_depto", ""),
            equipos=list(data.get("equipos", [])),
            estado_entrega=data.get("estado_entrega", "PENDIENTE"),
            pdf=data.get("pdf"),
            responsable=data.get("responsable", ""),
            usuario=data.get("usuario", ""),
        )


@dataclass
class Mantenimiento:
    id_mto: str
    sku: str
    tipo: str
    estado_inicial: str
    estado_final: str
    elementos_utilizados: str
    observaciones: str
    responsable: str
    usuario_registro: str
    fecha_programada: str | None = None
    fecha_realizado: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id_mto": self.id_mto,
            "sku": self.sku,
            "tipo": self.tipo,
            "fecha_programada": self.fecha_programada,
            "fecha_realizado": self.fecha_realizado,
            "estado_inicial": self.estado_inicial,
            "estado_final": self.estado_final,
            "elementos_utilizados": self.elementos_utilizados,
            "observaciones": self.observaciones,
            "responsable": self.responsable,
            "usuario_registro": self.usuario_registro,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Mantenimiento":
        return cls(
            id_mto=data.get("id_mto", ""),
            sku=data.get("sku", ""),
            tipo=data.get("tipo", "PREVENTIVO"),
            fecha_programada=data.get("fecha_programada"),
            fecha_realizado=data.get("fecha_realizado"),
            estado_inicial=data.get("estado_inicial", ""),
            estado_final=data.get("estado_final", ""),
            elementos_utilizados=data.get("elementos_utilizados", ""),
            observaciones=data.get("observaciones", ""),
            responsable=data.get("responsable", ""),
            usuario_registro=data.get("usuario_registro", ""),
        )
