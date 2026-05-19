from dataclasses import dataclass
from typing import Optional, List
from datetime import date, timedelta
from .database import get_connection


@dataclass
class Cita:
    id: Optional[int] = None
    paciente_id: int = 0
    fecha: str = ""   # YYYY-MM-DD
    hora: str = ""    # HH:MM
    motivo: str = ""
    paciente_nombre: str = ""  # join field, read-only


def _row(r) -> Cita:
    return Cita(
        id=r["id"],
        paciente_id=r["paciente_id"],
        fecha=r["fecha"],
        hora=r["hora"],
        motivo=r["motivo"] or "",
        paciente_nombre=r["paciente_nombre"],
    )


def crear_cita(cita: Cita) -> Cita:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO citas (paciente_id, fecha, hora, motivo) VALUES (?,?,?,?)",
            (cita.paciente_id, cita.fecha, cita.hora, cita.motivo or ""),
        )
        cita.id = cur.lastrowid
    return cita


def actualizar_cita(cita: Cita) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE citas SET paciente_id=?, fecha=?, hora=?, motivo=? WHERE id=?",
            (cita.paciente_id, cita.fecha, cita.hora, cita.motivo or "", cita.id),
        )


def eliminar_cita(cita_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM citas WHERE id=?", (cita_id,))


def listar_citas_mes(year: int, month: int) -> List[Cita]:
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT c.*, p.nombre AS paciente_nombre
            FROM citas c JOIN pacientes p ON p.id = c.paciente_id
            WHERE strftime('%Y', c.fecha) = ? AND strftime('%m', c.fecha) = ?
            ORDER BY c.fecha, c.hora
        """, (str(year), f"{month:02d}")).fetchall()
    return [_row(r) for r in rows]


def listar_citas_semana(fecha_lunes: str) -> List[Cita]:
    domingo = (date.fromisoformat(fecha_lunes) + timedelta(days=6)).isoformat()
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT c.*, p.nombre AS paciente_nombre
            FROM citas c JOIN pacientes p ON p.id = c.paciente_id
            WHERE c.fecha BETWEEN ? AND ?
            ORDER BY c.fecha, c.hora
        """, (fecha_lunes, domingo)).fetchall()
    return [_row(r) for r in rows]


def listar_citas_paciente(paciente_id: int) -> List[Cita]:
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT c.*, p.nombre AS paciente_nombre
            FROM citas c JOIN pacientes p ON p.id = c.paciente_id
            WHERE c.paciente_id = ?
            ORDER BY c.fecha DESC, c.hora DESC
        """, (paciente_id,)).fetchall()
    return [_row(r) for r in rows]
