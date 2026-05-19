"""Formulario de nueva consulta — diseño premium."""
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from datetime import date
from .styles import COLORS, PAD
from .widgets import (make_button, make_entry, make_text, make_separator,
                      make_card, make_checkbox, scrollable_frame, SaveButton, _font)
import db

C = COLORS


class FormConsulta(ctk.CTkFrame):
    def __init__(self, parent, nav):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self._nav         = nav
        self._paciente_id = None
        self._campos: dict  = {}
        self._dinamicos: list = []
        self._build_shell()

    def _build_shell(self):
        # ── Header ───────────────────────────────────────────────
        topbar = ctk.CTkFrame(self, fg_color=C["surface"], corner_radius=0)
        topbar.pack(fill="x")
        inner  = ctk.CTkFrame(topbar, fg_color="transparent")
        inner.pack(fill="x", padx=PAD["page"], pady=PAD["md"])

        make_button(inner, "← Volver", command=self._volver,
                    kind="ghost").pack(side="left")

        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.pack(side="right")
        make_button(right, "Cancelar", command=self._volver,
                    kind="secondary").pack(side="left", padx=(0, 8))
        SaveButton(right, "Guardar consulta",
                   command=self._guardar).pack(side="left")

        self._title_lbl = ctk.CTkLabel(inner, text="Nueva consulta",
                                        font=_font("heading"),
                                        text_color=C["text"],
                                        fg_color="transparent")
        self._title_lbl.pack(side="left", padx=(PAD["md"], 0))

        make_separator(self).pack(fill="x")

        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True)
        _, self._body = scrollable_frame(wrap)

    def on_show(self, paciente_id):
        self._paciente_id = paciente_id
        p = db.obtener_paciente(paciente_id)
        self._title_lbl.configure(text=f"Nueva consulta  —  {p.nombre}")
        self._rebuild_form()

    def _rebuild_form(self):
        for w in self._body.winfo_children():
            w.destroy()
        self._campos    = {}
        self._dinamicos = []
        PX = PAD["page"]

        # ── Sección 1: Datos básicos ─────────────────────────────
        self._section_num("01", "Datos de la consulta")

        shadow1, card1 = make_card(self._body, pad_x=PAD["lg"], pad_y=PAD["lg"])
        shadow1.pack(fill="x", padx=PX, pady=(0, PAD["md"]))

        row = ctk.CTkFrame(card1, fg_color="transparent")
        row.pack(fill="x")

        # Fecha
        f_wrap = ctk.CTkFrame(row, fg_color="transparent")
        f_wrap.pack(side="left", padx=(0, PAD["sm"]))
        ctk.CTkLabel(f_wrap, text="Fecha *", font=_font("label"),
                     text_color=C["text_secondary"],
                     fg_color="transparent").pack(anchor="w", pady=(0, 4))
        fecha_var = tk.StringVar(value=str(date.today()))
        self._campos["fecha"] = fecha_var
        e1, _ = make_entry(f_wrap, textvariable=fecha_var)
        e1.pack(anchor="w")

        # Motivo
        m_wrap = ctk.CTkFrame(row, fg_color="transparent")
        m_wrap.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(m_wrap, text="Motivo de consulta *", font=_font("label"),
                     text_color=C["text_secondary"],
                     fg_color="transparent").pack(anchor="w", pady=(0, 4))
        motivo_var = tk.StringVar()
        self._campos["motivo"] = motivo_var
        e2, _ = make_entry(m_wrap, textvariable=motivo_var)
        e2.pack(fill="x")

        # ── Sección 2: Síntomas dinámicos ────────────────────────
        preguntas = db.listar_preguntas(solo_activas=True)
        if preguntas:
            self._section_num("02", "Síntomas del paciente")
            shadow2, card2 = make_card(self._body,
                                        pad_x=PAD["lg"], pad_y=PAD["lg"])
            shadow2.pack(fill="x", padx=PX, pady=(0, PAD["md"]))

            bool_qs = [p for p in preguntas if p.tipo == "boolean"]
            text_qs = [p for p in preguntas if p.tipo == "text"]

            if bool_qs:
                cb_grid = ctk.CTkFrame(card2, fg_color="transparent")
                cb_grid.pack(anchor="w")
                for i, p in enumerate(bool_qs):
                    var = tk.BooleanVar()
                    make_checkbox(card2, text=p.texto, variable=var).grid(
                        row=i // 3, column=i % 3,
                        sticky="w", padx=(0, PAD["lg"]), pady=4)
                    self._dinamicos.append((p, var))

            if text_qs:
                make_separator(card2, color=C["border"]).pack(
                    fill="x", pady=PAD["xs"])
                txt_row = ctk.CTkFrame(card2, fg_color="transparent")
                txt_row.pack(fill="x")
                for p in text_qs:
                    col = ctk.CTkFrame(txt_row, fg_color="transparent")
                    col.pack(side="left", fill="x", expand=True,
                             padx=(0, PAD["sm"]))
                    ctk.CTkLabel(col, text=p.texto, font=_font("label"),
                                 text_color=C["text_secondary"],
                                 fg_color="transparent").pack(anchor="w",
                                                               pady=(0, 4))
                    var = tk.StringVar()
                    e3, _ = make_entry(col, textvariable=var)
                    e3.pack(fill="x")
                    self._dinamicos.append((p, var))

        # ── Sección 3: Evaluación clínica ────────────────────────
        sec_num = "03" if preguntas else "02"
        self._section_num(sec_num, "Evaluación clínica")
        shadow3, card3 = make_card(self._body, pad_x=PAD["lg"], pad_y=PAD["lg"])
        shadow3.pack(fill="x", padx=PX, pady=(0, PAD["md"]))

        for key, label, h in [
            ("diagnostico",   "Diagnóstico",   3),
            ("tratamiento",   "Tratamiento",   3),
            ("observaciones", "Observaciones", 2),
        ]:
            ctk.CTkLabel(card3, text=label, font=_font("label"),
                         text_color=C["text_secondary"],
                         fg_color="transparent").pack(anchor="w",
                                                       pady=(PAD["xs"], 4))
            _, t = make_text(card3, height=h)
            t.pack(fill="x")
            self._campos[key] = t

        ctk.CTkFrame(self._body, height=32, fg_color="transparent").pack()

    def _section_num(self, num, title):
        wrap = ctk.CTkFrame(self._body, fg_color="transparent")
        wrap.pack(fill="x", padx=PAD["page"], pady=(PAD["md"], PAD["xs"]))

        badge = ctk.CTkFrame(wrap, fg_color=C["primary_light"],
                              corner_radius=6, width=28, height=22)
        badge.pack(side="left")
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text=num,
                     font=ctk.CTkFont(family="Helvetica Neue",
                                       size=11, weight="bold"),
                     text_color=C["primary"],
                     fg_color="transparent").pack(expand=True)

        ctk.CTkLabel(wrap, text=title, font=_font("label"),
                     text_color=C["text_secondary"],
                     fg_color="transparent").pack(side="left", padx=(10, 0))

    def _guardar(self):
        fecha  = self._campos["fecha"].get().strip()
        motivo = self._campos["motivo"].get().strip()
        if not fecha or not motivo:
            messagebox.showwarning("Campos requeridos",
                                   "Fecha y motivo son obligatorios.")
            return

        def txt(key):
            return self._campos[key].get("1.0", "end").strip() or None

        consulta = db.crear_consulta(db.Consulta(
            paciente_id=self._paciente_id, fecha=fecha, motivo=motivo,
            diagnostico=txt("diagnostico"), tratamiento=txt("tratamiento"),
            observaciones=txt("observaciones"),
        ))

        respuestas = {}
        for pregunta, widget in self._dinamicos:
            if isinstance(widget, tk.BooleanVar):
                valor = "1" if widget.get() else "0"
            else:
                valor = widget.get().strip()
            respuestas[pregunta.id] = valor
        if respuestas:
            db.guardar_respuestas(consulta.id, respuestas)

        self._get_root().toast("Consulta guardada correctamente")
        self._nav("vista_paciente", self._paciente_id)

    def _volver(self):
        self._nav("vista_paciente", self._paciente_id)

    def _get_root(self):
        w = self
        while w.master:
            w = w.master
        return w
