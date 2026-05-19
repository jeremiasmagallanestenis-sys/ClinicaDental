import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import db as clinica


@pytest.fixture(autouse=True)
def db_limpia(tmp_path, monkeypatch):
    """Cada test usa una base de datos temporal vacía."""
    db_temp = tmp_path / "test.db"
    monkeypatch.setattr("db.database.DB_PATH", db_temp)
    # También parcheamos el módulo importado directamente
    import db.database as _db
    monkeypatch.setattr(_db, "DB_PATH", db_temp)
    clinica.init_db()
    yield


# ── Pacientes ────────────────────────────────────────────────────────────────

def test_crear_y_obtener_paciente():
    p = clinica.Paciente(nombre="Ana García", dni="12345678", fecha_nacimiento="1990-05-10")
    creado = clinica.crear_paciente(p)
    assert creado.id is not None

    obtenido = clinica.obtener_paciente(creado.id)
    assert obtenido.nombre == "Ana García"
    assert obtenido.dni == "12345678"


def test_editar_paciente():
    p = clinica.crear_paciente(
        clinica.Paciente(nombre="Juan Pérez", dni="87654321", fecha_nacimiento="1985-03-22")
    )
    p.telefono = "555-1234"
    p.notas = "Alérgico a la penicilina"
    clinica.editar_paciente(p)

    actualizado = clinica.obtener_paciente(p.id)
    assert actualizado.telefono == "555-1234"
    assert actualizado.notas == "Alérgico a la penicilina"


def test_listar_pacientes_ordenados():
    clinica.crear_paciente(clinica.Paciente(nombre="Zoe", dni="111", fecha_nacimiento="2000-01-01"))
    clinica.crear_paciente(clinica.Paciente(nombre="Ana", dni="222", fecha_nacimiento="2000-01-01"))
    clinica.crear_paciente(clinica.Paciente(nombre="Mario", dni="333", fecha_nacimiento="2000-01-01"))

    lista = clinica.listar_pacientes()
    nombres = [p.nombre for p in lista]
    assert nombres == sorted(nombres, key=str.lower)


def test_buscar_por_nombre_parcial():
    clinica.crear_paciente(clinica.Paciente(nombre="Carlos Ruiz", dni="001", fecha_nacimiento="1970-01-01"))
    clinica.crear_paciente(clinica.Paciente(nombre="Carolina Soto", dni="002", fecha_nacimiento="1980-01-01"))
    clinica.crear_paciente(clinica.Paciente(nombre="Luis Torres", dni="003", fecha_nacimiento="1990-01-01"))

    resultados = clinica.buscar_pacientes("car")
    assert len(resultados) == 2


def test_buscar_por_dni_exacto():
    clinica.crear_paciente(clinica.Paciente(nombre="Pedro", dni="99999999", fecha_nacimiento="1995-06-15"))
    resultados = clinica.buscar_pacientes("99999999")
    assert len(resultados) == 1
    assert resultados[0].nombre == "Pedro"


# ── Consultas ────────────────────────────────────────────────────────────────

def test_crear_consulta_y_diagnostico():
    p = clinica.crear_paciente(
        clinica.Paciente(nombre="María", dni="55555555", fecha_nacimiento="1992-08-20")
    )
    c = clinica.crear_consulta(
        clinica.Consulta(paciente_id=p.id, fecha="2026-04-28", motivo="Dolor molar")
    )
    assert c.id is not None

    d = clinica.guardar_diagnostico(
        clinica.DiagnosticoRespuestas(
            consulta_id=c.id,
            dolor=True,
            sensibilidad=False,
            sangrado=False,
            duracion_dolor="2 días",
            zona_afectada="Molar inferior derecho",
        )
    )
    assert d.id is not None

    recuperado = clinica.obtener_diagnostico(c.id)
    assert recuperado.dolor is True
    assert recuperado.zona_afectada == "Molar inferior derecho"


def test_diagnostico_upsert():
    p = clinica.crear_paciente(
        clinica.Paciente(nombre="Roberto", dni="44444444", fecha_nacimiento="1988-11-11")
    )
    c = clinica.crear_consulta(
        clinica.Consulta(paciente_id=p.id, fecha="2026-04-28", motivo="Revisión")
    )
    clinica.guardar_diagnostico(clinica.DiagnosticoRespuestas(consulta_id=c.id, sangrado=True))
    clinica.guardar_diagnostico(clinica.DiagnosticoRespuestas(consulta_id=c.id, sangrado=False, dolor=True))

    d = clinica.obtener_diagnostico(c.id)
    assert d.sangrado is False
    assert d.dolor is True


def test_historial_ordenado_por_fecha():
    p = clinica.crear_paciente(
        clinica.Paciente(nombre="Lucía", dni="33333333", fecha_nacimiento="2001-03-03")
    )
    clinica.crear_consulta(clinica.Consulta(paciente_id=p.id, fecha="2025-01-10", motivo="A"))
    clinica.crear_consulta(clinica.Consulta(paciente_id=p.id, fecha="2026-04-01", motivo="B"))
    clinica.crear_consulta(clinica.Consulta(paciente_id=p.id, fecha="2024-07-15", motivo="C"))

    historial = clinica.historial_paciente(p.id)
    fechas = [c.fecha for c in historial]
    assert fechas == sorted(fechas, reverse=True)


def test_cascade_delete_consulta_borra_diagnostico():
    p = clinica.crear_paciente(
        clinica.Paciente(nombre="Test", dni="00000001", fecha_nacimiento="2000-01-01")
    )
    c = clinica.crear_consulta(
        clinica.Consulta(paciente_id=p.id, fecha="2026-04-28", motivo="Test cascade")
    )
    clinica.guardar_diagnostico(clinica.DiagnosticoRespuestas(consulta_id=c.id, dolor=True))

    import db.database as _db
    with _db.get_connection() as conn:
        conn.execute("DELETE FROM consultas WHERE id = ?", (c.id,))

    assert clinica.obtener_diagnostico(c.id) is None
