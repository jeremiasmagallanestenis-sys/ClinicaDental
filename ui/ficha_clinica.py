import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import date
from .styles import COLORS, PAD, RADIUS
from .widgets import (make_button, make_entry, make_text, make_separator,
                      make_card, make_avatar, make_tag, scrollable_frame,
                      SaveButton, _font)
from .odontograma_widget import OdontogramaWidget
import db

C = COLORS


class FichaClinica(ctk.CTkFrame):
    def __init__(self, parent, nav):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self._nav      = nav
        self._paciente = None
        self._vars     = {}
        self._odonto   = None
        self._build_shell()

    # ── Shell ────────────────────────────────────────────────────────────────

    def _build_shell(self):
        topbar = ctk.CTkFrame(self, fg_color=C["surface"], corner_radius=0)
        topbar.pack(fill="x")
        inner = ctk.CTkFrame(topbar, fg_color="transparent")
        inner.pack(fill="x", padx=PAD["x"], pady=PAD["sm"])

        make_button(inner, "← Pacientes", command=self._volver,
                    kind="ghost").pack(side="left")
        self._title = ctk.CTkLabel(inner, text="Ficha Clínica",
                                    font=_font("heading"),
                                    text_color=C["text"],
                                    fg_color="transparent")
        self._title.pack(side="left", padx=PAD["sm"])
        SaveButton(inner, "Guardar ficha", command=self._guardar).pack(side="right")
        make_button(inner, "Editar datos", command=self._editar_paciente,
                    kind="secondary").pack(side="right", padx=(0, 8))
        make_separator(self).pack(fill="x")

        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True)
        _, self._body = scrollable_frame(wrap)

    # ── Carga ────────────────────────────────────────────────────────────────

    def on_show(self, paciente_id):
        self._paciente = db.obtener_paciente(paciente_id)
        self._title.configure(text=f"Ficha Clínica — {self._paciente.nombre}")
        for w in self._body.winfo_children():
            w.destroy()
        self._vars   = {}
        self._odonto = None
        self._build_form()
        self._load_data()

    # ── Formulario ───────────────────────────────────────────────────────────

    def _build_form(self):
        PX = PAD["x"]

        # 0 ── Info paciente ──────────────────────────────────────────────────
        p = self._paciente
        outer_p, card_p = make_card(self._body, pad_x=PAD["sm"], pad_y=PAD["sm"])
        outer_p.pack(fill="x", padx=PX, pady=(PAD["y"], PAD["sm"]))
        row_p = ctk.CTkFrame(card_p, fg_color="transparent")
        row_p.pack(fill="x")
        make_avatar(row_p, p.nombre, size=44,
                    bg_parent=C["surface"]).pack(side="left", padx=(0, 14))
        info_p = ctk.CTkFrame(row_p, fg_color="transparent")
        info_p.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(info_p, text=p.nombre, font=_font("subheading"),
                     text_color=C["text"],
                     fg_color="transparent").pack(anchor="w")
        chips_p = ctk.CTkFrame(info_p, fg_color="transparent")
        chips_p.pack(anchor="w", pady=(4, 0))
        for lbl, val in [("DNI", p.dni), ("Tel.", p.telefono or "—")]:
            make_tag(chips_p, f"{lbl} {val}",
                     bg=C["primary_light"], fg=C["primary"],
                     bg_parent=C["surface"]).pack(side="left", padx=(0, 6))

        # 1 ── Odontograma ────────────────────────────────────────────────────
        self._section("Odontograma", PX)
        outer_o, card_o = make_card(self._body, pad_x=PAD["sm"], pad_y=PAD["sm"])
        outer_o.pack(fill="x", padx=PX, pady=(0, PAD["sm"]))
        self._odonto = OdontogramaWidget(card_o, bg=C["surface"])
        self._odonto.frame.pack(anchor="w")

        # 2 ── Enfermedades ───────────────────────────────────────────────────
        self._section("¿Tiene alguna enfermedad?", PX)
        outer_e, card_e = make_card(self._body, pad_x=PAD["sm"], pad_y=PAD["sm"])
        outer_e.pack(fill="x", padx=PX, pady=(0, PAD["sm"]))

        enfs = [
            ("enf_cardiaca",     "Cardíaca"),
            ("enf_circulatoria", "Circulatoria"),
            ("enf_respiratoria", "Respiratoria"),
            ("enf_hormonal",     "Hormonal"),
            ("enf_digestiva",    "Digestiva"),
            ("enf_infecciosa",   "Infecciosa"),
            ("enf_renal",        "Renal"),
        ]
        grid = ctk.CTkFrame(card_e, fg_color="transparent")
        grid.pack(anchor="w")
        for i, (key, label) in enumerate(enfs):
            var = tk.BooleanVar()
            self._vars[key] = var
            ctk.CTkCheckBox(
                grid, text=label, variable=var,
                font=_font("body"), text_color=C["text"],
                fg_color=C["primary"], hover_color=C["primary_hover"],
                checkmark_color="white", corner_radius=4,
            ).grid(row=i // 4, column=i % 4, sticky="w", padx=(0, 24), pady=3)

        otras_row = ctk.CTkFrame(card_e, fg_color="transparent")
        otras_row.pack(anchor="w", pady=(8, 0))
        ctk.CTkLabel(otras_row, text="Otras — especificar:",
                     font=_font("label"), text_color=C["text_secondary"],
                     fg_color="transparent").pack(side="left", padx=(0, 8))
        var_otras = tk.StringVar()
        self._vars["enf_otras"] = var_otras
        e, _ = make_entry(otras_row, textvariable=var_otras)
        e.pack(side="left")

        # 3 ── Preguntas Sí/No ────────────────────────────────────────────────
        self._section("Información médica general", PX)
        outer_m, card_m = make_card(self._body, pad_x=PAD["sm"], pad_y=PAD["sm"])
        outer_m.pack(fill="x", padx=PX, pady=(0, PAD["sm"]))

        preguntas_sino = [
            ("toma_medicacion",     "¿Toma alguna medicación?"),
            ("alergico_medicacion", "¿Es alérgico/a a alguna medicación?"),
            ("operado",             "¿Lo/la operaron alguna vez?"),
            ("hemorragias",         "¿Tuvo hemorragias?"),
            ("embarazada",          "¿Está embarazada?"),
            ("fuma",                "¿Fuma?"),
        ]
        for key, label in preguntas_sino:
            row = ctk.CTkFrame(card_m, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=label, font=_font("body"),
                         text_color=C["text"], fg_color="transparent",
                         width=300, anchor="w").pack(side="left")
            var = tk.StringVar(value="no")
            self._vars[key] = var
            for txt, val in [("Sí", "si"), ("No", "no")]:
                ctk.CTkRadioButton(
                    row, text=txt, variable=var, value=val,
                    font=_font("body"), text_color=C["text"],
                    fg_color=C["primary"], hover_color=C["primary_hover"],
                ).pack(side="left", padx=6)

        # 4 ── Observaciones ──────────────────────────────────────────────────
        self._section("Observaciones", PX)
        outer_obs, card_obs = make_card(self._body, pad_x=PAD["sm"], pad_y=PAD["sm"])
        outer_obs.pack(fill="x", padx=PX, pady=(0, PAD["sm"]))
        outer_t, t = make_text(card_obs, height=4)
        outer_t.pack(fill="x")
        self._vars["observaciones"] = t

        # 5 ── Cuenta corriente ───────────────────────────────────────────────
        self._section("Cuenta corriente", PX)
        self._build_tabla_pagos(PX)

        # 6 ── Registro de visitas ────────────────────────────────────────────
        self._section("Registro de visitas", PX)
        self._build_registro_visitas(PX)

    def _section(self, title, padx=0):
        wrap = ctk.CTkFrame(self._body, fg_color="transparent")
        wrap.pack(fill="x", pady=(PAD["sm"], 6), padx=padx)
        ctk.CTkFrame(wrap, width=3, fg_color=C["primary"],
                     corner_radius=2).pack(side="left", fill="y")
        ctk.CTkLabel(wrap, text=title, font=_font("label"),
                     text_color=C["text_secondary"],
                     fg_color="transparent").pack(side="left", padx=10)

    # ── Registro de visitas ──────────────────────────────────────────────────

    def _build_registro_visitas(self, padx=0):
        outer, card = make_card(self._body, pad_x=PAD["sm"], pad_y=PAD["sm"])
        outer.pack(fill="x", padx=padx, pady=(0, PAD["sm"]))
        self._visitas_card = card
        self._render_visitas()

    def _render_visitas(self):
        for w in self._visitas_card.winfo_children():
            w.destroy()

        consultas = db.historial_paciente(self._paciente.id)

        if consultas:
            for i, c in enumerate(consultas):
                tl = ctk.CTkFrame(self._visitas_card, fg_color="transparent")
                tl.pack(fill="x", pady=2)

                left = ctk.CTkFrame(tl, fg_color="transparent", width=40)
                left.pack(side="left", fill="y")
                left.pack_propagate(False)

                dot_cv = tk.Canvas(left, width=12, height=12,
                                   bg=C["surface"], highlightthickness=0)
                dot_cv.pack(pady=(4, 0))
                dot_cv.create_oval(1, 1, 11, 11,
                                   fill=C["primary"], outline=C["primary_hover"])

                if i < len(consultas) - 1:
                    tk.Frame(left, width=2, bg=C["border"]).pack(
                        fill="y", expand=True, pady=(2, 0))

                content = ctk.CTkFrame(tl, fg_color="transparent")
                content.pack(side="left", fill="x", expand=True,
                             padx=(6, 0), pady=(0, 10))

                date_chip = ctk.CTkFrame(content, fg_color=C["primary_light"],
                                          corner_radius=RADIUS["pill"])
                date_chip.pack(anchor="w")
                ctk.CTkLabel(date_chip, text=c.fecha, font=_font("caption"),
                             text_color=C["primary"],
                             fg_color="transparent").pack(padx=10, pady=3)

                texto = c.observaciones or c.tratamiento or c.motivo or ""
                ctk.CTkLabel(content, text=texto, font=_font("body"),
                             text_color=C["text_secondary"],
                             fg_color="transparent",
                             anchor="w", justify="left",
                             wraplength=540).pack(anchor="w", pady=(4, 0))

                def _del(cid=c.id):
                    db.eliminar_consulta(cid)
                    self._render_visitas()

                make_button(tl, "✕", command=_del,
                            kind="ghost", small=True).pack(side="right",
                                                           anchor="n", pady=2)

            make_separator(self._visitas_card, color=C["border"]).pack(
                fill="x", pady=(4, 14))

        # ── Nueva visita rápida ──────────────────────────────────
        new_section = ctk.CTkFrame(self._visitas_card, fg_color="transparent")
        new_section.pack(fill="x")

        ctk.CTkLabel(new_section, text="Nueva entrada", font=_font("label"),
                     text_color=C["text"],
                     fg_color="transparent").pack(anchor="w", pady=(0, 10))

        date_row = ctk.CTkFrame(new_section, fg_color="transparent")
        date_row.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(date_row, text="Fecha", font=_font("caption"),
                     text_color=C["text_muted"],
                     fg_color="transparent").pack(anchor="w", pady=(0, 4))
        self._visita_fecha_var = tk.StringVar(value=str(date.today()))
        e, _ = make_entry(date_row, textvariable=self._visita_fecha_var)
        e.pack(anchor="w")

        ctk.CTkLabel(new_section, text="¿Qué se hizo en la consulta?",
                     font=_font("caption"), text_color=C["text_muted"],
                     fg_color="transparent").pack(anchor="w", pady=(0, 4))
        outer_t, self._visita_text = make_text(new_section, height=4)
        outer_t.pack(fill="x", pady=(0, 10))

        make_button(new_section, "Agregar visita",
                    command=self._agregar_visita,
                    kind="secondary").pack(anchor="e")

    def _agregar_visita(self):
        fecha = self._visita_fecha_var.get().strip()
        texto = self._visita_text.get("1.0", "end").strip()
        if not fecha or not texto:
            return
        db.crear_consulta(db.Consulta(
            paciente_id=self._paciente.id,
            fecha=fecha, motivo="",
            diagnostico=None, tratamiento=None, observaciones=texto,
        ))
        self._render_visitas()

    # ── Tabla de pagos ───────────────────────────────────────────────────────

    def _build_tabla_pagos(self, padx=0):
        outer, card = make_card(self._body, pad_x=PAD["sm"], pad_y=PAD["sm"])
        outer.pack(fill="x", padx=padx, pady=(0, PAD["sm"]))

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", pady=(0, 6))
        make_button(btn_row, "+ Agregar fila", command=self._agregar_pago,
                    kind="ghost", small=True).pack(side="right")

        style = ttk.Style()
        style.configure("Ficha.Treeview",
                         font=("Helvetica Neue", 13), rowheight=32,
                         background=C["surface"],
                         fieldbackground=C["surface"],
                         foreground=C["text"])
        style.configure("Ficha.Treeview.Heading",
                         font=("Helvetica Neue", 12, "bold"),
                         background=C["bg"],
                         foreground=C["text_secondary"],
                         relief="flat", padding=(6, 6))
        style.map("Ficha.Treeview",
                  background=[("selected", C["primary_light"])],
                  foreground=[("selected", C["text"])])

        cols = ("fecha", "tratamiento", "total", "pagado", "saldo")
        tree_frame = tk.Frame(card, bg=C["border"], padx=1, pady=1)
        tree_frame.pack(fill="x")

        self._tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                                   style="Ficha.Treeview", height=8,
                                   selectmode="browse")
        self._tree.heading("fecha",       text="Fecha")
        self._tree.heading("tratamiento", text="Tratamiento")
        self._tree.heading("total",       text="Total")
        self._tree.heading("pagado",      text="Pagos")
        self._tree.heading("saldo",       text="Saldo")

        self._tree.column("fecha",        width=110, minwidth=90,  anchor="center", stretch=False)
        self._tree.column("tratamiento",  width=380, minwidth=200, anchor="w",      stretch=True)
        self._tree.column("total",        width=100, minwidth=80,  anchor="center", stretch=False)
        self._tree.column("pagado",       width=100, minwidth=80,  anchor="center", stretch=False)
        self._tree.column("saldo",        width=100, minwidth=80,  anchor="center", stretch=False)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self._tree.bind("<Button-1>", self._on_cell_click)
        self._entry_editor = None

        make_separator(card, color=C["border"]).pack(fill="x", pady=(8, 6))

        totales_row = ctk.CTkFrame(card, fg_color="transparent")
        totales_row.pack(fill="x")
        self._lbl_total  = self._total_chip(totales_row, "Total",
                                             C["tag_blue_bg"],   C["tag_blue_fg"])
        self._lbl_pagado = self._total_chip(totales_row, "Pagos",
                                             C["tag_green_bg"],  C["tag_green_fg"])
        self._lbl_saldo  = self._total_chip(totales_row, "Saldo",
                                             C["tag_yellow_bg"], C["tag_yellow_fg"])

    def _total_chip(self, parent, label, bg, fg):
        frame = ctk.CTkFrame(parent, fg_color=bg, corner_radius=RADIUS["pill"])
        frame.pack(side="right", padx=(8, 0))
        lbl = ctk.CTkLabel(frame, text=f"{label}: $0",
                            font=_font("label"), text_color=fg,
                            fg_color="transparent")
        lbl.pack(padx=12, pady=5)
        return lbl

    def _refresh_tabla(self):
        for row in self._tree.get_children():
            self._tree.delete(row)
        pagos = db.listar_pagos(self._paciente.id)
        total_t = total_p = 0.0
        for p in pagos:
            self._tree.insert("", "end", iid=str(p.id), values=(
                p.fecha, p.tratamiento,
                f"$ {p.total:,.0f}", f"$ {p.pagado:,.0f}", f"$ {p.saldo:,.0f}",
            ))
            total_t += p.total
            total_p += p.pagado
        saldo_t = total_t - total_p
        self._lbl_total.configure( text=f"Total: $ {total_t:,.0f}")
        self._lbl_pagado.configure(text=f"Pagos: $ {total_p:,.0f}")
        self._lbl_saldo.configure( text=f"Saldo: $ {saldo_t:,.0f}")

    def _agregar_pago(self):
        from datetime import date as _date
        p = db.crear_pago(db.Pago(
            paciente_id=self._paciente.id,
            fecha=str(_date.today()),
            tratamiento="", total=0, pagado=0,
        ))
        self._refresh_tabla()
        iid = str(p.id)
        self._tree.selection_set(iid)
        self._tree.see(iid)
        self._tree.after(50, lambda: self._abrir_editor_celda(iid, "fecha"))

    _COL_TIPOS = {"fecha": "texto", "tratamiento": "texto",
                  "total": "numero", "pagado": "numero"}
    _COLS = ("fecha", "tratamiento", "total", "pagado", "saldo")

    def _on_cell_click(self, event):
        region = self._tree.identify_region(event.x, event.y)
        if region != "cell":
            self._cerrar_editor()
            return
        col_id = self._tree.identify_column(event.x)
        iid    = self._tree.identify_row(event.y)
        if not iid:
            self._cerrar_editor()
            return
        col_idx  = int(col_id[1:]) - 1
        col_name = self._COLS[col_idx]
        if col_name == "saldo":
            return
        self._abrir_editor_celda(iid, col_name)

    def _abrir_editor_celda(self, iid, col_name):
        self._cerrar_editor(guardar=True)
        col_idx = self._COLS.index(col_name)
        col_id  = f"#{col_idx + 1}"
        bbox = self._tree.bbox(iid, col_id)
        if not bbox:
            return
        x, y, w, h = bbox
        raw_vals = self._tree.item(iid, "values")
        current  = raw_vals[col_idx]
        if col_name in ("total", "pagado"):
            current = current.replace("$ ", "").replace(",", "")
        var   = tk.StringVar(value=current)
        entry = tk.Entry(self._tree, textvariable=var,
                         font=("Helvetica Neue", 13), relief="flat",
                         bg=C["primary_light"], fg=C["text"],
                         insertbackground=C["primary"],
                         highlightthickness=1,
                         highlightbackground=C["primary"])
        entry.place(x=x, y=y, width=w, height=h)
        entry.select_range(0, "end")
        entry.focus_set()

        def _tab(_=None):
            cols_ed = list(self._COL_TIPOS.keys())
            idx     = cols_ed.index(col_name) if col_name in cols_ed else -1
            if idx < len(cols_ed) - 1:
                prox = cols_ed[idx + 1]
                self._cerrar_editor(guardar=True)
                self._tree.after(30, lambda: self._abrir_editor_celda(iid, prox))
            else:
                self._cerrar_editor(guardar=True)
            return "break"

        entry.bind("<Return>",   lambda _: self._cerrar_editor(guardar=True))
        entry.bind("<Escape>",   lambda _: self._cerrar_editor(guardar=False))
        entry.bind("<Tab>",      _tab)
        entry.bind("<FocusOut>", lambda e: self._tree.after(
            50, lambda: self._cerrar_editor(guardar=True)))
        self._entry_editor = (entry, iid, col_name, var)

    def _cerrar_editor(self, guardar=True):
        if self._entry_editor is None:
            return
        entry, iid, col_name, var = self._entry_editor
        self._entry_editor = None
        valor = var.get().strip()
        entry.destroy()
        if not guardar:
            return
        pagos = db.listar_pagos(self._paciente.id)
        pago  = next((p for p in pagos if str(p.id) == iid), None)
        if pago is None:
            return
        tipo = self._COL_TIPOS.get(col_name, "texto")
        if tipo == "numero":
            try:
                nuevo_num = float(valor.replace(",", ".")) if valor else 0.0
            except ValueError:
                nuevo_num = 0.0
            setattr(pago, col_name, nuevo_num)
        else:
            setattr(pago, col_name, valor)
        db.actualizar_pago(pago)
        self._refresh_tabla()

    # ── Carga / Guardado ─────────────────────────────────────────────────────

    def _load_data(self):
        h = db.obtener_historial(self._paciente.id)

        bool_keys = ["enf_cardiaca", "enf_circulatoria", "enf_respiratoria",
                     "enf_hormonal", "enf_digestiva", "enf_infecciosa", "enf_renal"]
        for k in bool_keys:
            self._vars[k].set(getattr(h, k))

        self._vars["enf_otras"].set(h.enf_otras or "")

        sino_keys = ["toma_medicacion", "alergico_medicacion", "operado",
                     "hemorragias", "embarazada", "fuma"]
        for k in sino_keys:
            self._vars[k].set("si" if getattr(h, k) else "no")

        obs = self._vars["observaciones"]
        obs.delete("1.0", "end")
        if h.observaciones:
            obs.insert("1.0", h.observaciones)

        datos_odonto = db.obtener_odontograma(self._paciente.id)
        if datos_odonto:
            self._odonto.set_datos(datos_odonto)

        self._refresh_tabla()

    def _guardar(self):
        bool_keys = ["enf_cardiaca", "enf_circulatoria", "enf_respiratoria",
                     "enf_hormonal", "enf_digestiva", "enf_infecciosa", "enf_renal"]
        sino_keys = ["toma_medicacion", "alergico_medicacion", "operado",
                     "hemorragias", "embarazada", "fuma"]

        h = db.HistorialMedico(paciente_id=self._paciente.id)
        for k in bool_keys:
            setattr(h, k, bool(self._vars[k].get()))
        h.enf_otras = self._vars["enf_otras"].get().strip() or None
        for k in sino_keys:
            setattr(h, k, self._vars[k].get() == "si")
        h.observaciones = self._vars["observaciones"].get("1.0", "end").strip() or None

        db.guardar_historial(h)
        db.guardar_odontograma(self._paciente.id, self._odonto.get_datos())
        self._get_root().toast("Ficha guardada correctamente")

    def _volver(self):
        self._nav("principal", None)

    def _editar_paciente(self):
        if self._paciente:
            self._nav("form_paciente", self._paciente.id)

    def _get_root(self):
        w = self
        while w.master:
            w = w.master
        return w
