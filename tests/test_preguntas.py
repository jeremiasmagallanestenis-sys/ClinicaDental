import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import db
import db.database as _db
import db.backup as _backup


@pytest.fixture(autouse=True)
def db_limpia(tmp_path, monkeypatch):
    db_temp = tmp_path / "test.db"
    monkeypatch.setattr(_db, "DB_PATH", db_temp)
    monkeypatch.setattr(_backup, "DB_PATH", db_temp)
    db.init_db()
    yield


def test_seed_crea_preguntas_por_defecto():
    preguntas = db.listar_preguntas()
    assert len(preguntas) == 5
    tipos = {p.tipo for p in preguntas}
    assert "boolean" in tipos
    assert "text" in tipos


def test_crear_pregunta():
    p = db.crear_pregunta(db.Pregunta(texto="Inflamación", tipo="boolean", orden=10))
    assert p.id is not None
    lista = db.listar_preguntas()
    assert any(x.texto == "Inflamación" for x in lista)


def test_actualizar_pregunta():
    p = db.listar_preguntas()[0]
    p.texto = "Dolor modificado"
    db.actualizar_pregunta(p)
    actualizada = db.listar_preguntas()[0]
    assert actualizada.texto == "Dolor modificado"


def test_eliminar_es_logico():
    p = db.listar_preguntas()[0]
    db.eliminar_pregunta(p.id)
    activas = db.listar_preguntas(solo_activas=True)
    assert all(x.id != p.id for x in activas)
    todas = db.listar_preguntas(solo_activas=False)
    assert any(x.id == p.id for x in todas)


def test_guardar_y_obtener_respuestas():
    paciente = db.crear_paciente(db.Paciente(nombre="Test", dni="000", fecha_nacimiento="2000-01-01"))
    consulta = db.crear_consulta(db.Consulta(paciente_id=paciente.id, fecha="2026-04-28", motivo="Revisión"))
    preguntas = db.listar_preguntas()

    respuestas_in = {preguntas[0].id: "1", preguntas[3].id: "2 días"}
    db.guardar_respuestas(consulta.id, respuestas_in)

    respuestas_out = db.obtener_respuestas(consulta.id)
    assert respuestas_out[preguntas[0].id] == "1"
    assert respuestas_out[preguntas[3].id] == "2 días"


def test_respuestas_upsert():
    paciente = db.crear_paciente(db.Paciente(nombre="Test2", dni="001", fecha_nacimiento="2000-01-01"))
    consulta = db.crear_consulta(db.Consulta(paciente_id=paciente.id, fecha="2026-04-28", motivo="Control"))
    p = db.listar_preguntas()[0]

    db.guardar_respuestas(consulta.id, {p.id: "1"})
    db.guardar_respuestas(consulta.id, {p.id: "0"})

    assert db.obtener_respuestas(consulta.id)[p.id] == "0"


def test_migracion_legada():
    """Datos en diagnostico_respuestas deben migrarse a respuestas_consulta al init."""
    paciente = db.crear_paciente(db.Paciente(nombre="Legado", dni="999", fecha_nacimiento="1990-01-01"))
    consulta = db.crear_consulta(db.Consulta(paciente_id=paciente.id, fecha="2025-01-01", motivo="Viejo"))

    # Insertar en tabla legada directamente
    with _db.get_connection() as conn:
        conn.execute(
            "INSERT INTO diagnostico_respuestas (consulta_id, dolor, zona_afectada) VALUES (?,?,?)",
            (consulta.id, 1, "Molar superior"),
        )

    # Re-ejecutar init para disparar migración
    db.init_db()

    respuestas = db.obtener_respuestas(consulta.id)
    assert len(respuestas) > 0
    preguntas_idx = {p.texto: p for p in db.listar_preguntas(solo_activas=False)}
    pid_dolor = preguntas_idx["Dolor"].id
    assert respuestas.get(pid_dolor) == "1"
