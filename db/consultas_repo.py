from typing import Optional
from .database import get_connection
from .models import Consulta, DiagnosticoRespuestas


def _row_to_consulta(row) -> Consulta:
    return Consulta(
        id=row["id"],
        paciente_id=row["paciente_id"],
        fecha=row["fecha"],
        motivo=row["motivo"],
        diagnostico=row["diagnostico"],
        tratamiento=row["tratamiento"],
        observaciones=row["observaciones"],
    )


def _row_to_diagnostico(row) -> DiagnosticoRespuestas:
    return DiagnosticoRespuestas(
        id=row["id"],
        consulta_id=row["consulta_id"],
        dolor=bool(row["dolor"]),
        sensibilidad=bool(row["sensibilidad"]),
        sangrado=bool(row["sangrado"]),
        duracion_dolor=row["duracion_dolor"],
        zona_afectada=row["zona_afectada"],
    )


def crear_consulta(c: Consulta) -> Consulta:
    sql = """
        INSERT INTO consultas (paciente_id, fecha, motivo, diagnostico, tratamiento, observaciones)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    with get_connection() as conn:
        cur = conn.execute(sql, (
            c.paciente_id, c.fecha, c.motivo,
            c.diagnostico, c.tratamiento, c.observaciones,
        ))
        c.id = cur.lastrowid
    return c


def guardar_diagnostico(d: DiagnosticoRespuestas) -> DiagnosticoRespuestas:
    """Inserta o reemplaza el diagnóstico de una consulta (upsert)."""
    sql = """
        INSERT INTO diagnostico_respuestas
            (consulta_id, dolor, sensibilidad, sangrado, duracion_dolor, zona_afectada)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(consulta_id) DO UPDATE SET
            dolor         = excluded.dolor,
            sensibilidad  = excluded.sensibilidad,
            sangrado      = excluded.sangrado,
            duracion_dolor = excluded.duracion_dolor,
            zona_afectada = excluded.zona_afectada
    """
    with get_connection() as conn:
        cur = conn.execute(sql, (
            d.consulta_id, int(d.dolor), int(d.sensibilidad), int(d.sangrado),
            d.duracion_dolor, d.zona_afectada,
        ))
        if d.id is None:
            d.id = cur.lastrowid
    return d


def historial_paciente(paciente_id: int) -> list[Consulta]:
    """Devuelve todas las consultas de un paciente ordenadas por fecha descendente."""
    sql = """
        SELECT * FROM consultas
        WHERE paciente_id = ?
        ORDER BY fecha DESC
    """
    with get_connection() as conn:
        rows = conn.execute(sql, (paciente_id,)).fetchall()
    return [_row_to_consulta(r) for r in rows]


def obtener_consulta(consulta_id: int) -> Optional[Consulta]:
    sql = "SELECT * FROM consultas WHERE id = ?"
    with get_connection() as conn:
        row = conn.execute(sql, (consulta_id,)).fetchone()
    return _row_to_consulta(row) if row else None


def eliminar_consulta(consulta_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM consultas WHERE id = ?", (consulta_id,))


def obtener_diagnostico(consulta_id: int) -> Optional[DiagnosticoRespuestas]:
    sql = "SELECT * FROM diagnostico_respuestas WHERE consulta_id = ?"
    with get_connection() as conn:
        row = conn.execute(sql, (consulta_id,)).fetchone()
    return _row_to_diagnostico(row) if row else None
