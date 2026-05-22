import sys
from pathlib import Path

# Add project root to path so `import db` works
sys.path.insert(0, str(Path(__file__).parent.parent))

import db
from flask import Flask, render_template, redirect, url_for, request, jsonify, abort, session
from functools import wraps

db.init_db()

app = Flask(__name__)
app.secret_key = "guirlanda-dental-2024-xk92"

USUARIO = "Richard guirlanda"
CONTRASENA = "appdental"

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ──────────────────────────────────────────────
# Login
# ──────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form["usuario"] == USUARIO and request.form["contrasena"] == CONTRASENA:
            session["logged_in"] = True
            return redirect(url_for("pacientes"))
        error = "Usuario o contraseña incorrectos"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ──────────────────────────────────────────────
# HTML routes
# ──────────────────────────────────────────────

@app.route("/")
@login_required
def index():
    return redirect(url_for("pacientes"))


@app.route("/pacientes")
@login_required
def pacientes():
    q = request.args.get("q", "").strip()
    if q:
        lista = db.buscar_pacientes(q)
    else:
        lista = db.listar_pacientes()
    n_preguntas = len(db.listar_preguntas(solo_activas=True))
    return render_template("pacientes.html", pacientes=lista, q=q, n_preguntas=n_preguntas)


@app.route("/pacientes/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_paciente():
    if request.method == "POST":
        p = db.Paciente(
            nombre=request.form["nombre"].strip(),
            dni=request.form["dni"].strip(),
            fecha_nacimiento=request.form["fecha_nacimiento"].strip(),
            telefono=request.form.get("telefono", "").strip() or None,
            notas=request.form.get("notas", "").strip() or None,
        )
        db.crear_paciente(p)
        return redirect(url_for("ver_paciente", id=p.id))
    return render_template("form_paciente.html", paciente=None, titulo="Nuevo Paciente")


@app.route("/pacientes/<int:id>")
@login_required
def ver_paciente(id):
    paciente = db.obtener_paciente(id)
    if not paciente:
        abort(404)
    historial = db.historial_paciente(id)
    return render_template("vista_paciente.html", paciente=paciente, historial=historial)


@app.route("/pacientes/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar_paciente(id):
    paciente = db.obtener_paciente(id)
    if not paciente:
        abort(404)
    if request.method == "POST":
        paciente.nombre = request.form["nombre"].strip()
        paciente.dni = request.form["dni"].strip()
        paciente.fecha_nacimiento = request.form["fecha_nacimiento"].strip()
        paciente.telefono = request.form.get("telefono", "").strip() or None
        paciente.notas = request.form.get("notas", "").strip() or None
        db.editar_paciente(paciente)
        return redirect(url_for("ver_paciente", id=id))
    return render_template("form_paciente.html", paciente=paciente, titulo="Editar Paciente")


@app.route("/pacientes/<int:id>/ficha", methods=["GET", "POST"])
@login_required
def ficha_clinica(id):
    paciente = db.obtener_paciente(id)
    if not paciente:
        abort(404)
    if request.method == "POST":
        from datetime import date
        consulta = db.Consulta(
            paciente_id=id,
            fecha=request.form.get("fecha", date.today().isoformat()),
            motivo=request.form.get("motivo", "").strip(),
            diagnostico=request.form.get("diagnostico", "").strip() or None,
            tratamiento=request.form.get("tratamiento", "").strip() or None,
            observaciones=request.form.get("observaciones", "").strip() or None,
        )
        db.crear_consulta(consulta)
        return redirect(url_for("ver_paciente", id=id))
    from datetime import date
    historial = db.historial_paciente(id)
    return render_template("ficha_clinica.html", paciente=paciente,
                           historial=historial, today=date.today().isoformat())


@app.route("/api/odontograma/<int:id>")
@login_required
def api_get_odontograma(id):
    datos = db.obtener_odontograma(id)
    return jsonify(datos)

@app.route("/api/odontograma/<int:id>", methods=["POST"])
@login_required
def api_guardar_odontograma(id):
    datos = request.get_json(force=True)
    db.guardar_odontograma(id, datos)
    return jsonify({"ok": True})

@app.route("/api/historial_medico/<int:id>")
@login_required
def api_get_historial_medico(id):
    h = db.obtener_historial(id)
    return jsonify({
        "enf_cardiaca": h.enf_cardiaca, "enf_circulatoria": h.enf_circulatoria,
        "enf_respiratoria": h.enf_respiratoria, "enf_hormonal": h.enf_hormonal,
        "enf_digestiva": h.enf_digestiva, "enf_infecciosa": h.enf_infecciosa,
        "enf_renal": h.enf_renal, "enf_otras": h.enf_otras or "",
        "toma_medicacion": h.toma_medicacion, "alergico_medicacion": h.alergico_medicacion,
        "operado": h.operado, "hemorragias": h.hemorragias,
        "embarazada": h.embarazada, "fuma": h.fuma,
        "observaciones": h.observaciones or "",
    })

@app.route("/api/historial_medico/<int:id>", methods=["POST"])
@login_required
def api_guardar_historial_medico(id):
    data = request.get_json(force=True)
    h = db.HistorialMedico(
        paciente_id=id,
        enf_cardiaca=bool(data.get("enf_cardiaca")),
        enf_circulatoria=bool(data.get("enf_circulatoria")),
        enf_respiratoria=bool(data.get("enf_respiratoria")),
        enf_hormonal=bool(data.get("enf_hormonal")),
        enf_digestiva=bool(data.get("enf_digestiva")),
        enf_infecciosa=bool(data.get("enf_infecciosa")),
        enf_renal=bool(data.get("enf_renal")),
        enf_otras=data.get("enf_otras") or None,
        toma_medicacion=bool(data.get("toma_medicacion")),
        alergico_medicacion=bool(data.get("alergico_medicacion")),
        operado=bool(data.get("operado")),
        hemorragias=bool(data.get("hemorragias")),
        embarazada=bool(data.get("embarazada")),
        fuma=bool(data.get("fuma")),
        observaciones=data.get("observaciones") or None,
    )
    db.guardar_historial(h)
    return jsonify({"ok": True})

@app.route("/api/pagos/<int:id>")
@login_required
def api_listar_pagos(id):
    pagos = db.listar_pagos(id)
    return jsonify([{"id":p.id,"fecha":p.fecha,"tratamiento":p.tratamiento,
                     "total":p.total,"pagado":p.pagado,"saldo":p.saldo} for p in pagos])

@app.route("/api/pagos/<int:id>", methods=["POST"])
@login_required
def api_crear_pago(id):
    from datetime import date
    p = db.crear_pago(db.Pago(paciente_id=id, fecha=str(date.today()),
                               tratamiento="", total=0, pagado=0))
    return jsonify({"id":p.id,"fecha":p.fecha,"tratamiento":p.tratamiento,
                    "total":p.total,"pagado":p.pagado,"saldo":p.saldo}), 201

@app.route("/api/pagos/fila/<int:pago_id>", methods=["PUT"])
@login_required
def api_actualizar_pago(pago_id):
    data = request.get_json(force=True)
    pagos = db.listar_pagos(int(data.get("paciente_id", 0)))
    pago = next((p for p in pagos if p.id == pago_id), None)
    if not pago:
        abort(404)
    pago.fecha = data.get("fecha", pago.fecha)
    pago.tratamiento = data.get("tratamiento", pago.tratamiento)
    pago.total = float(data.get("total", pago.total) or 0)
    pago.pagado = float(data.get("pagado", pago.pagado) or 0)
    db.actualizar_pago(pago)
    return jsonify({"ok": True, "saldo": pago.saldo})

@app.route("/api/pagos/fila/<int:pago_id>", methods=["DELETE"])
@login_required
def api_eliminar_pago(pago_id):
    db.eliminar_pago(pago_id)
    return jsonify({"ok": True})

@app.route("/calendario")
@login_required
def calendario():
    return render_template("calendario.html")


# ──────────────────────────────────────────────
# API routes
# ──────────────────────────────────────────────

@app.route("/api/citas_semana")
@login_required
def api_citas_semana():
    from datetime import date, timedelta
    fecha_str = request.args.get("fecha")
    if fecha_str:
        d = date.fromisoformat(fecha_str)
        # Adjust to Monday
        lunes = d - timedelta(days=d.weekday())
    else:
        today = date.today()
        lunes = today - timedelta(days=today.weekday())
    citas = db.listar_citas_semana(lunes.isoformat())
    return jsonify([{
        "id": c.id,
        "paciente_id": c.paciente_id,
        "paciente_nombre": c.paciente_nombre,
        "fecha": c.fecha,
        "hora": c.hora,
        "motivo": c.motivo,
    } for c in citas])


@app.route("/api/citas_mes")
@login_required
def api_citas_mes():
    from datetime import date
    year = int(request.args.get("year", date.today().year))
    month = int(request.args.get("month", date.today().month))
    citas = db.listar_citas_mes(year, month)
    return jsonify([{
        "id": c.id,
        "paciente_id": c.paciente_id,
        "paciente_nombre": c.paciente_nombre,
        "fecha": c.fecha,
        "hora": c.hora,
        "motivo": c.motivo,
    } for c in citas])


@app.route("/api/citas", methods=["POST"])
@login_required
def api_crear_cita():
    data = request.get_json(force=True)
    cita = db.Cita(
        paciente_id=int(data["paciente_id"]),
        fecha=data["fecha"],
        hora=data["hora"],
        motivo=data.get("motivo", ""),
    )
    cita = db.crear_cita(cita)
    return jsonify({"id": cita.id}), 201


@app.route("/api/citas/<int:id>", methods=["PUT"])
@login_required
def api_actualizar_cita(id):
    data = request.get_json(force=True)
    cita = db.Cita(
        id=id,
        paciente_id=int(data["paciente_id"]),
        fecha=data["fecha"],
        hora=data["hora"],
        motivo=data.get("motivo", ""),
    )
    db.actualizar_cita(cita)
    return jsonify({"ok": True})


@app.route("/api/citas/<int:id>", methods=["DELETE"])
@login_required
def api_eliminar_cita(id):
    db.eliminar_cita(id)
    return jsonify({"ok": True})


@app.route("/api/pacientes")
@login_required
def api_pacientes():
    pacientes = db.listar_pacientes()
    return jsonify([{
        "id": p.id,
        "nombre": p.nombre,
        "dni": p.dni,
    } for p in pacientes])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
