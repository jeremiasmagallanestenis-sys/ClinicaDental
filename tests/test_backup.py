import sys
import json
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import db
import db.backup as backup
import db.database as _db


@pytest.fixture(autouse=True)
def db_limpia(tmp_path, monkeypatch):
    db_temp = tmp_path / "test.db"
    monkeypatch.setattr(_db, "DB_PATH", db_temp)
    monkeypatch.setattr(backup, "DB_PATH", db_temp)
    db.init_db()
    yield


def _seed():
    p = db.crear_paciente(db.Paciente(nombre="Ana", dni="111", fecha_nacimiento="1990-01-01"))
    c = db.crear_consulta(db.Consulta(paciente_id=p.id, fecha="2026-04-28", motivo="Dolor"))
    db.guardar_diagnostico(db.DiagnosticoRespuestas(consulta_id=c.id, dolor=True, zona_afectada="Molar"))
    return p, c


def test_exportar_json_genera_archivo(tmp_path):
    _seed()
    dest = tmp_path / "backup.json"
    n = db.exportar_json(dest)
    assert dest.exists()
    assert n == 1
    data = json.loads(dest.read_text())
    assert data["meta"]["version"] == 2
    assert len(data["pacientes"]) == 1
    assert len(data["consultas"]) == 1


def test_exportar_sqlite_genera_archivo_valido(tmp_path):
    _seed()
    dest = tmp_path / "backup.db"
    db.exportar_sqlite(dest)
    assert dest.exists()
    assert dest.read_bytes()[:16] == b"SQLite format 3\x00"


def test_restaurar_json_fusiona_sin_duplicados(tmp_path):
    p, _ = _seed()
    dest = tmp_path / "backup.json"
    db.exportar_json(dest)

    # Agrego un paciente nuevo DESPUÉS del backup
    db.crear_paciente(db.Paciente(nombre="Luis", dni="222", fecha_nacimiento="1985-05-05"))

    conteos = db.restaurar_json(dest, modo="fusionar")

    # El paciente del backup ya existe → 0 importados nuevos
    assert conteos["pacientes"] == 0
    # Luis sigue existiendo (no fue borrado)
    todos = db.listar_pacientes()
    nombres = {p.nombre for p in todos}
    assert "Ana" in nombres
    assert "Luis" in nombres


def test_restaurar_json_modo_reemplazar(tmp_path):
    _seed()
    dest = tmp_path / "backup.json"
    db.exportar_json(dest)

    db.crear_paciente(db.Paciente(nombre="Extra", dni="999", fecha_nacimiento="2000-01-01"))
    assert len(db.listar_pacientes()) == 2

    db.restaurar_json(dest, modo="reemplazar")

    pacientes = db.listar_pacientes()
    assert len(pacientes) == 1
    assert pacientes[0].nombre == "Ana"


def test_leer_meta_json(tmp_path):
    _seed()
    dest = tmp_path / "backup.json"
    db.exportar_json(dest)
    meta = db.leer_meta_json(dest)
    assert meta["version"] == 2
    assert meta["n_pacientes"] == 1
    assert meta["n_consultas"] == 1


def test_restaurar_json_archivo_invalido(tmp_path):
    bad = tmp_path / "malo.json"
    bad.write_text('{"meta": {"version": 99}}')
    with pytest.raises(ValueError, match="versión incompatible"):
        db.restaurar_json(bad)


def test_restaurar_sqlite_archivo_invalido(tmp_path):
    bad = tmp_path / "notadb.db"
    bad.write_bytes(b"esto no es sqlite")
    with pytest.raises(ValueError, match="no es una base de datos SQLite"):
        db.restaurar_sqlite(bad)


def test_restaurar_sqlite_reemplaza_db(tmp_path):
    _seed()
    snapshot = tmp_path / "snap.db"
    db.exportar_sqlite(snapshot)

    # Agrego datos después del snapshot
    db.crear_paciente(db.Paciente(nombre="Nuevo", dni="777", fecha_nacimiento="1995-01-01"))
    assert len(db.listar_pacientes()) == 2

    db.restaurar_sqlite(snapshot)
    assert len(db.listar_pacientes()) == 1
