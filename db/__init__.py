from .database import init_db, get_connection
from .backup import exportar_json, exportar_sqlite, restaurar_json, restaurar_sqlite, leer_meta_json
from .models import Paciente, Consulta, DiagnosticoRespuestas
from .pacientes_repo import (
    crear_paciente,
    editar_paciente,
    listar_pacientes,
    buscar_pacientes,
    obtener_paciente,
)
from .consultas_repo import (
    crear_consulta,
    eliminar_consulta,
    guardar_diagnostico,
    historial_paciente,
    obtener_consulta,
    obtener_diagnostico,
)
from .ficha_repo import (
    HistorialMedico, Pago,
    obtener_historial, guardar_historial,
    obtener_odontograma, guardar_odontograma,
    listar_pagos, crear_pago, actualizar_pago, eliminar_pago,
)
from .citas_repo import (
    Cita,
    crear_cita,
    actualizar_cita,
    eliminar_cita,
    listar_citas_mes,
    listar_citas_semana,
    listar_citas_paciente,
)
from .preguntas_repo import (
    Pregunta,
    listar_preguntas,
    crear_pregunta,
    actualizar_pregunta,
    eliminar_pregunta,
    reordenar,
    guardar_respuestas,
    obtener_respuestas,
)
