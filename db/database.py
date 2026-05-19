import sys
import sqlite3
from pathlib import Path

PREGUNTAS_DEFAULT = [
    ("Dolor",          "boolean", 0),
    ("Sensibilidad",   "boolean", 1),
    ("Sangrado",       "boolean", 2),
    ("Duración del dolor", "text", 3),
    ("Zona afectada",  "text",    4),
]


def _resolve_paths():
    import os
    frozen = getattr(sys, "frozen", False)
    if frozen:
        data_dir = Path.home() / "Library" / "Application Support" / "HistorialClinico"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir / "clinica.db", Path(sys._MEIPASS) / "db" / "schema.sql"
    # En Railway u otro hosting: usar variable de entorno DB_PATH
    if "DB_PATH" in os.environ:
        db_path = Path(os.environ["DB_PATH"])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return db_path, Path(__file__).parent / "schema.sql"
    return Path(__file__).parent / "clinica.db", Path(__file__).parent / "schema.sql"


DB_PATH, SCHEMA_PATH = _resolve_paths()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with get_connection() as conn:
        conn.executescript(schema)
        _seed_preguntas(conn)
        _migrar_diagnostico_legado(conn)


def _seed_preguntas(conn: sqlite3.Connection) -> None:
    """Inserta las preguntas por defecto solo si la tabla está vacía."""
    n = conn.execute("SELECT COUNT(*) FROM preguntas_diagnostico").fetchone()[0]
    if n == 0:
        conn.executemany(
            "INSERT INTO preguntas_diagnostico (texto, tipo, orden) VALUES (?, ?, ?)",
            PREGUNTAS_DEFAULT,
        )


def _migrar_diagnostico_legado(conn: sqlite3.Connection) -> None:
    """
    Convierte filas de diagnostico_respuestas (tabla legada) a respuestas_consulta.
    Se ejecuta una sola vez: las filas migradas no se tocan en ejecuciones futuras.
    """
    legadas = conn.execute("""
        SELECT dr.* FROM diagnostico_respuestas dr
        WHERE NOT EXISTS (
            SELECT 1 FROM respuestas_consulta rc WHERE rc.consulta_id = dr.consulta_id
        )
    """).fetchall()

    if not legadas:
        return

    preguntas = {
        row["texto"]: row["id"]
        for row in conn.execute("SELECT id, texto FROM preguntas_diagnostico").fetchall()
    }

    mapping = {
        "Dolor":               ("dolor",         "boolean"),
        "Sensibilidad":        ("sensibilidad",   "boolean"),
        "Sangrado":            ("sangrado",       "boolean"),
        "Duración del dolor":  ("duracion_dolor", "text"),
        "Zona afectada":       ("zona_afectada",  "text"),
    }

    for fila in legadas:
        for texto, (col, tipo) in mapping.items():
            pid = preguntas.get(texto)
            if pid is None:
                continue
            val = fila[col]
            if val is None:
                continue
            valor = str(int(val)) if tipo == "boolean" else str(val)
            conn.execute(
                "INSERT OR IGNORE INTO respuestas_consulta (consulta_id, pregunta_id, valor) VALUES (?,?,?)",
                (fila["consulta_id"], pid, valor),
            )


if __name__ == "__main__":
    init_db()
    print(f"Base de datos inicializada en: {DB_PATH}")
