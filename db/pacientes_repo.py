from typing import Optional
from .database import get_connection
from .models import Paciente


def _row_to_paciente(row) -> Paciente:
    return Paciente(
        id=row["id"],
        nombre=row["nombre"],
        dni=row["dni"],
        fecha_nacimiento=row["fecha_nacimiento"],
        telefono=row["telefono"],
        notas=row["notas"],
    )


def crear_paciente(p: Paciente) -> Paciente:
    sql = """
        INSERT INTO pacientes (nombre, dni, fecha_nacimiento, telefono, notas)
        VALUES (?, ?, ?, ?, ?)
    """
    with get_connection() as conn:
        cur = conn.execute(sql, (p.nombre, p.dni, p.fecha_nacimiento, p.telefono, p.notas))
        p.id = cur.lastrowid
    return p


def editar_paciente(p: Paciente) -> None:
    if p.id is None:
        raise ValueError("El paciente no tiene id asignado.")
    sql = """
        UPDATE pacientes
        SET nombre = ?, dni = ?, fecha_nacimiento = ?, telefono = ?, notas = ?
        WHERE id = ?
    """
    with get_connection() as conn:
        conn.execute(sql, (p.nombre, p.dni, p.fecha_nacimiento, p.telefono, p.notas, p.id))


def listar_pacientes() -> list[Paciente]:
    sql = "SELECT * FROM pacientes ORDER BY nombre COLLATE NOCASE"
    with get_connection() as conn:
        rows = conn.execute(sql).fetchall()
    return [_row_to_paciente(r) for r in rows]


def buscar_pacientes(termino: str) -> list[Paciente]:
    """Busca por nombre (parcial, case-insensitive) o por DNI exacto."""
    like = f"%{termino.lower()}%"
    sql = """
        SELECT * FROM pacientes
        WHERE LOWER(nombre) LIKE ? OR dni = ?
        ORDER BY nombre COLLATE NOCASE
    """
    with get_connection() as conn:
        rows = conn.execute(sql, (like, termino)).fetchall()
    return [_row_to_paciente(r) for r in rows]


def obtener_paciente(paciente_id: int) -> Optional[Paciente]:
    sql = "SELECT * FROM pacientes WHERE id = ?"
    with get_connection() as conn:
        row = conn.execute(sql, (paciente_id,)).fetchone()
    return _row_to_paciente(row) if row else None
