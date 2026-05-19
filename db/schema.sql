PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS pacientes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT    NOT NULL,
    dni             TEXT    NOT NULL UNIQUE,
    fecha_nacimiento TEXT   NOT NULL,
    telefono        TEXT,
    notas           TEXT
);

CREATE TABLE IF NOT EXISTS consultas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id     INTEGER NOT NULL,
    fecha           TEXT    NOT NULL,
    motivo          TEXT    NOT NULL,
    diagnostico     TEXT,
    tratamiento     TEXT,
    observaciones   TEXT,
    FOREIGN KEY (paciente_id) REFERENCES consultas(id) ON DELETE CASCADE
);

-- Tabla legada: se conserva para no perder datos históricos.
-- Las nuevas consultas usan respuestas_consulta.
CREATE TABLE IF NOT EXISTS diagnostico_respuestas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    consulta_id     INTEGER NOT NULL UNIQUE,
    dolor           INTEGER NOT NULL DEFAULT 0 CHECK (dolor IN (0, 1)),
    sensibilidad    INTEGER NOT NULL DEFAULT 0 CHECK (sensibilidad IN (0, 1)),
    sangrado        INTEGER NOT NULL DEFAULT 0 CHECK (sangrado IN (0, 1)),
    duracion_dolor  TEXT,
    zona_afectada   TEXT,
    FOREIGN KEY (consulta_id) REFERENCES consultas(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS preguntas_diagnostico (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    texto   TEXT    NOT NULL,
    tipo    TEXT    NOT NULL DEFAULT 'boolean' CHECK (tipo IN ('boolean', 'text')),
    orden   INTEGER NOT NULL DEFAULT 0,
    activa  INTEGER NOT NULL DEFAULT 1 CHECK (activa IN (0, 1))
);

CREATE TABLE IF NOT EXISTS respuestas_consulta (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    consulta_id INTEGER NOT NULL,
    pregunta_id INTEGER NOT NULL,
    valor       TEXT    NOT NULL DEFAULT '',
    FOREIGN KEY (consulta_id) REFERENCES consultas(id) ON DELETE CASCADE,
    FOREIGN KEY (pregunta_id) REFERENCES preguntas_diagnostico(id) ON DELETE CASCADE,
    UNIQUE (consulta_id, pregunta_id)
);

CREATE TABLE IF NOT EXISTS historial_medico (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id         INTEGER NOT NULL UNIQUE,
    enf_cardiaca        INTEGER NOT NULL DEFAULT 0,
    enf_circulatoria    INTEGER NOT NULL DEFAULT 0,
    enf_respiratoria    INTEGER NOT NULL DEFAULT 0,
    enf_hormonal        INTEGER NOT NULL DEFAULT 0,
    enf_digestiva       INTEGER NOT NULL DEFAULT 0,
    enf_infecciosa      INTEGER NOT NULL DEFAULT 0,
    enf_renal           INTEGER NOT NULL DEFAULT 0,
    enf_otras           TEXT,
    toma_medicacion     INTEGER NOT NULL DEFAULT 0,
    alergico_medicacion INTEGER NOT NULL DEFAULT 0,
    operado             INTEGER NOT NULL DEFAULT 0,
    hemorragias         INTEGER NOT NULL DEFAULT 0,
    embarazada          INTEGER NOT NULL DEFAULT 0,
    fuma                INTEGER NOT NULL DEFAULT 0,
    observaciones       TEXT,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS odontograma (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER NOT NULL UNIQUE,
    datos       TEXT    NOT NULL DEFAULT '{}',
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pagos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER NOT NULL,
    fecha       TEXT    NOT NULL,
    tratamiento TEXT    NOT NULL,
    total       REAL    NOT NULL DEFAULT 0,
    pagado      REAL    NOT NULL DEFAULT 0,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS citas (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER NOT NULL,
    fecha       TEXT    NOT NULL,
    hora        TEXT    NOT NULL,
    motivo      TEXT    DEFAULT '',
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_consultas_paciente_id   ON consultas(paciente_id);
CREATE INDEX IF NOT EXISTS idx_consultas_fecha          ON consultas(fecha);
CREATE INDEX IF NOT EXISTS idx_respuestas_consulta_id  ON respuestas_consulta(consulta_id);
CREATE INDEX IF NOT EXISTS idx_citas_fecha              ON citas(fecha);
