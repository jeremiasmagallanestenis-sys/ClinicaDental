"""Repositorio para historial médico, odontograma y pagos."""
import json
from dataclasses import dataclass, field, asdict
from typing import Optional
from .database import get_connection


# ── Historial médico ──────────────────────────────────────────────────────────

@dataclass
class HistorialMedico:
    paciente_id: int
    enf_cardiaca:        bool = False
    enf_circulatoria:    bool = False
    enf_respiratoria:    bool = False
    enf_hormonal:        bool = False
    enf_digestiva:       bool = False
    enf_infecciosa:      bool = False
    enf_renal:           bool = False
    enf_otras:           Optional[str] = None
    toma_medicacion:     bool = False
    alergico_medicacion: bool = False
    operado:             bool = False
    hemorragias:         bool = False
    embarazada:          bool = False
    fuma:                bool = False
    observaciones:       Optional[str] = None
    id: Optional[int] = None


def obtener_historial(paciente_id: int) -> HistorialMedico:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM historial_medico WHERE paciente_id = ?", (paciente_id,)
        ).fetchone()
    if row:
        return HistorialMedico(
            id=row["id"], paciente_id=row["paciente_id"],
            enf_cardiaca=bool(row["enf_cardiaca"]),
            enf_circulatoria=bool(row["enf_circulatoria"]),
            enf_respiratoria=bool(row["enf_respiratoria"]),
            enf_hormonal=bool(row["enf_hormonal"]),
            enf_digestiva=bool(row["enf_digestiva"]),
            enf_infecciosa=bool(row["enf_infecciosa"]),
            enf_renal=bool(row["enf_renal"]),
            enf_otras=row["enf_otras"],
            toma_medicacion=bool(row["toma_medicacion"]),
            alergico_medicacion=bool(row["alergico_medicacion"]),
            operado=bool(row["operado"]),
            hemorragias=bool(row["hemorragias"]),
            embarazada=bool(row["embarazada"]),
            fuma=bool(row["fuma"]),
            observaciones=row["observaciones"],
        )
    return HistorialMedico(paciente_id=paciente_id)


def guardar_historial(h: HistorialMedico) -> None:
    sql = """
        INSERT INTO historial_medico
            (paciente_id, enf_cardiaca, enf_circulatoria, enf_respiratoria,
             enf_hormonal, enf_digestiva, enf_infecciosa, enf_renal, enf_otras,
             toma_medicacion, alergico_medicacion, operado, hemorragias,
             embarazada, fuma, observaciones)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(paciente_id) DO UPDATE SET
            enf_cardiaca        = excluded.enf_cardiaca,
            enf_circulatoria    = excluded.enf_circulatoria,
            enf_respiratoria    = excluded.enf_respiratoria,
            enf_hormonal        = excluded.enf_hormonal,
            enf_digestiva       = excluded.enf_digestiva,
            enf_infecciosa      = excluded.enf_infecciosa,
            enf_renal           = excluded.enf_renal,
            enf_otras           = excluded.enf_otras,
            toma_medicacion     = excluded.toma_medicacion,
            alergico_medicacion = excluded.alergico_medicacion,
            operado             = excluded.operado,
            hemorragias         = excluded.hemorragias,
            embarazada          = excluded.embarazada,
            fuma                = excluded.fuma,
            observaciones       = excluded.observaciones
    """
    with get_connection() as conn:
        conn.execute(sql, (
            h.paciente_id,
            int(h.enf_cardiaca), int(h.enf_circulatoria), int(h.enf_respiratoria),
            int(h.enf_hormonal), int(h.enf_digestiva), int(h.enf_infecciosa),
            int(h.enf_renal), h.enf_otras,
            int(h.toma_medicacion), int(h.alergico_medicacion),
            int(h.operado), int(h.hemorragias), int(h.embarazada), int(h.fuma),
            h.observaciones,
        ))


# ── Odontograma ───────────────────────────────────────────────────────────────

def obtener_odontograma(paciente_id: int) -> dict:
    """Devuelve {numero_diente: estado_str}."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT datos FROM odontograma WHERE paciente_id = ?", (paciente_id,)
        ).fetchone()
    return json.loads(row["datos"]) if row else {}


def guardar_odontograma(paciente_id: int, datos: dict) -> None:
    sql = """
        INSERT INTO odontograma (paciente_id, datos) VALUES (?, ?)
        ON CONFLICT(paciente_id) DO UPDATE SET datos = excluded.datos
    """
    with get_connection() as conn:
        conn.execute(sql, (paciente_id, json.dumps(datos)))


# ── Pagos ─────────────────────────────────────────────────────────────────────

@dataclass
class Pago:
    paciente_id: int
    fecha: str
    tratamiento: str
    total: float = 0.0
    pagado: float = 0.0
    id: Optional[int] = None

    @property
    def saldo(self) -> float:
        return self.total - self.pagado


def listar_pagos(paciente_id: int) -> list[Pago]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM pagos WHERE paciente_id = ? ORDER BY fecha DESC, id DESC",
            (paciente_id,)
        ).fetchall()
    return [_row_pago(r) for r in rows]


def crear_pago(p: Pago) -> Pago:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO pagos (paciente_id, fecha, tratamiento, total, pagado) VALUES (?,?,?,?,?)",
            (p.paciente_id, p.fecha, p.tratamiento, p.total, p.pagado),
        )
        p.id = cur.lastrowid
    return p


def actualizar_pago(p: Pago) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE pagos SET fecha=?, tratamiento=?, total=?, pagado=? WHERE id=?",
            (p.fecha, p.tratamiento, p.total, p.pagado, p.id),
        )


def eliminar_pago(pago_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM pagos WHERE id = ?", (pago_id,))


def _row_pago(row) -> Pago:
    return Pago(id=row["id"], paciente_id=row["paciente_id"],
                fecha=row["fecha"], tratamiento=row["tratamiento"],
                total=row["total"], pagado=row["pagado"])
