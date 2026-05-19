from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Paciente:
    nombre: str
    dni: str
    fecha_nacimiento: str
    telefono: Optional[str] = None
    notas: Optional[str] = None
    id: Optional[int] = None


@dataclass
class Consulta:
    paciente_id: int
    fecha: str
    motivo: str
    diagnostico: Optional[str] = None
    tratamiento: Optional[str] = None
    observaciones: Optional[str] = None
    id: Optional[int] = None


@dataclass
class DiagnosticoRespuestas:
    consulta_id: int
    dolor: bool = False
    sensibilidad: bool = False
    sangrado: bool = False
    duracion_dolor: Optional[str] = None
    zona_afectada: Optional[str] = None
    id: Optional[int] = None
