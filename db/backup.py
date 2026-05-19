"""
Backup y restauración de datos clínicos.

Formatos soportados:
  - .json  → exportación completa legible, restauración con merge-check
  - .db    → copia directa del archivo SQLite (snapshot binario)
"""
import json
import shutil
from datetime import datetime
from pathlib import Path

from .database import DB_PATH, get_connection, init_db


# ── Exportar ─────────────────────────────────────────────────────────────────

TABLAS_BACKUP = (
    "pacientes",
    "consultas",
    "preguntas_diagnostico",
    "respuestas_consulta",
    "diagnostico_respuestas",   # tabla legada — se incluye para no perder datos viejos
)


def exportar_json(destino: Path) -> int:
    """Exporta todas las tablas a JSON. Devuelve cantidad de pacientes exportados."""
    data = {
        "meta": {
            "version": 2,
            "exportado_en": datetime.now().isoformat(timespec="seconds"),
            "origen": str(DB_PATH),
        },
    }

    with get_connection() as conn:
        for tabla in TABLAS_BACKUP:
            rows = conn.execute(f"SELECT * FROM {tabla} ORDER BY id").fetchall()
            data[tabla] = [dict(r) for r in rows]

    destino.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(data["pacientes"])


def exportar_sqlite(destino: Path) -> None:
    """Copia el archivo .db directamente (backup binario instantáneo)."""
    shutil.copy2(DB_PATH, destino)


# ── Restaurar ─────────────────────────────────────────────────────────────────

class ConflictoBackup(Exception):
    """Se lanza cuando el backup tiene datos que colisionan con los existentes."""
    def __init__(self, mensaje: str, conflictos: list[str]):
        super().__init__(mensaje)
        self.conflictos = conflictos


def restaurar_json(origen: Path, modo: str = "fusionar") -> dict:
    """
    Restaura desde un archivo JSON exportado por esta app.

    modo:
      "fusionar"   → inserta solo los registros cuyo id no existe todavía.
      "reemplazar" → borra todo y recarga desde el backup (destructivo).

    Devuelve dict con conteos: {"pacientes": n, "consultas": n, "diagnostico_respuestas": n}
    """
    raw = json.loads(origen.read_text(encoding="utf-8"))

    if raw.get("meta", {}).get("version") not in (1, 2):
        raise ValueError("Formato de backup no reconocido o versión incompatible.")

    conteos = {"pacientes": 0, "consultas": 0, "diagnostico_respuestas": 0}

    with get_connection() as conn:
        if modo == "reemplazar":
            conn.executescript("""
                PRAGMA foreign_keys = OFF;
                DELETE FROM diagnostico_respuestas;
                DELETE FROM consultas;
                DELETE FROM pacientes;
                DELETE FROM sqlite_sequence;
                PRAGMA foreign_keys = ON;
            """)

        tablas_en_backup = [t for t in TABLAS_BACKUP if t in raw]
        for tabla in tablas_en_backup:
            rows = raw.get(tabla, [])
            if not rows:
                continue

            cols = list(rows[0].keys())
            placeholders = ", ".join("?" * len(cols))
            col_names = ", ".join(cols)

            for row in rows:
                try:
                    conn.execute(
                        f"INSERT OR IGNORE INTO {tabla} ({col_names}) VALUES ({placeholders})",
                        list(row.values()),
                    )
                    if conn.execute("SELECT changes()").fetchone()[0]:
                        conteos[tabla] += 1
                except Exception as exc:
                    raise RuntimeError(f"Error restaurando {tabla} id={row.get('id')}: {exc}") from exc

    return conteos


def restaurar_sqlite(origen: Path) -> None:
    """Reemplaza la base de datos activa con el archivo .db de backup."""
    if not _es_sqlite_valido(origen):
        raise ValueError("El archivo seleccionado no es una base de datos SQLite válida.")
    shutil.copy2(origen, DB_PATH)


def _es_sqlite_valido(path: Path) -> bool:
    try:
        header = path.read_bytes()[:16]
        return header == b"SQLite format 3\x00"
    except Exception:
        return False


# ── Metadata del backup ───────────────────────────────────────────────────────

def leer_meta_json(path: Path) -> dict:
    """Devuelve el bloque 'meta' de un backup JSON sin cargar todo el archivo."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        meta = raw.get("meta", {})
        meta["n_pacientes"]   = len(raw.get("pacientes", []))
        meta["n_consultas"]   = len(raw.get("consultas", []))
        meta["n_preguntas"]   = len(raw.get("preguntas_diagnostico", []))
        return meta
    except Exception:
        return {}
