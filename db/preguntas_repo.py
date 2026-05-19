from dataclasses import dataclass
from typing import Optional
from .database import get_connection


@dataclass
class Pregunta:
    texto: str
    tipo: str           # 'boolean' | 'text'
    orden: int = 0
    activa: bool = True
    id: Optional[int] = None


def listar_preguntas(solo_activas: bool = True) -> list[Pregunta]:
    sql = "SELECT * FROM preguntas_diagnostico"
    if solo_activas:
        sql += " WHERE activa = 1"
    sql += " ORDER BY orden, id"
    with get_connection() as conn:
        rows = conn.execute(sql).fetchall()
    return [_row(r) for r in rows]


def crear_pregunta(p: Pregunta) -> Pregunta:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO preguntas_diagnostico (texto, tipo, orden, activa) VALUES (?,?,?,?)",
            (p.texto, p.tipo, p.orden, int(p.activa)),
        )
        p.id = cur.lastrowid
    return p


def actualizar_pregunta(p: Pregunta) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE preguntas_diagnostico SET texto=?, tipo=?, orden=?, activa=? WHERE id=?",
            (p.texto, p.tipo, p.orden, int(p.activa), p.id),
        )


def eliminar_pregunta(pregunta_id: int) -> None:
    """Borrado lógico: desactiva la pregunta sin eliminar respuestas históricas."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE preguntas_diagnostico SET activa = 0 WHERE id = ?",
            (pregunta_id,),
        )


def reordenar(ids_en_orden: list[int]) -> None:
    with get_connection() as conn:
        for i, pid in enumerate(ids_en_orden):
            conn.execute(
                "UPDATE preguntas_diagnostico SET orden = ? WHERE id = ?", (i, pid)
            )


def guardar_respuestas(consulta_id: int, respuestas: dict[int, str]) -> None:
    """respuestas = {pregunta_id: valor_str}. Upsert por consulta."""
    with get_connection() as conn:
        for pid, valor in respuestas.items():
            conn.execute(
                """INSERT INTO respuestas_consulta (consulta_id, pregunta_id, valor)
                   VALUES (?,?,?)
                   ON CONFLICT(consulta_id, pregunta_id) DO UPDATE SET valor = excluded.valor""",
                (consulta_id, pid, valor),
            )


def obtener_respuestas(consulta_id: int) -> dict[int, str]:
    """Devuelve {pregunta_id: valor_str}."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT pregunta_id, valor FROM respuestas_consulta WHERE consulta_id = ?",
            (consulta_id,),
        ).fetchall()
    return {r["pregunta_id"]: r["valor"] for r in rows}


def _row(r) -> Pregunta:
    return Pregunta(
        id=r["id"], texto=r["texto"], tipo=r["tipo"],
        orden=r["orden"], activa=bool(r["activa"]),
    )
