"""Formulario de paciente — diseño premium."""
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from .styles import COLORS, PAD, RADIUS
from .widgets import (make_button, make_entry, make_text, make_separator,
                      make_card, scrollable_frame, SaveButton, _font)
import db

C = COLORS


class FormPaciente(ctk.CTkFrame):
    def __init__(self, parent, nav):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self._nav      = nav
        self._paciente = None
        self._entries: dict = {}
        self._build()

    def _build(self):
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
        SaveButton(right, "Guardar paciente",
                   command=self._guardar).pack(side="left")

        titles = ctk.CTkFrame(inner, fg_color="transparent")
        titles.pack(side="left", padx=(PAD["md"], 0))
        self._title_lbl = ctk.CTkLabel(titles, text="Nuevo paciente",
                                        font=_font("heading"),
                                        text_color=C["text"],
                                        fg_color="transparent")
        self._title_lbl.pack(anchor="w")

        make_separator(self).pack(fill="x")

        # ── Cuerpo scrollable ─────────────────────────────────────
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True)
        _, body = scrollable_frame(wrap)

        # ── Card principal ────────────────────────────────────────
        shadow, card = make_card(body, pad_x=PAD["xl"], pad_y=PAD["xl"])
        shadow.pack(fill="x", padx=PAD["xl"] * 2, pady=PAD["xl"])

        # Título de sección
        sec_head = ctk.CTkFrame(card, fg_color="transparent")
        sec_head.pack(fill="x", pady=(0, PAD["md"]))
        ctk.CTkLabel(sec_head, text="01",
                     font=ctk.CTkFont(family=C.get("FF", "Helvetica Neue"),
                                       size=11, weight="bold"),
                     text_color=C["primary"],
                     fg_color=C["primary_light"],
                     corner_radius=6,
                     width=28, height=22).pack(side="left")
        ctk.CTkLabel(sec_head, text="Datos personales",
                     font=_font("subheading"),
                     text_color=C["text"],
                     fg_color="transparent").pack(side="left", padx=(10, 0))

        make_separator(card, color=C["border"]).pack(fill="x", pady=(0, PAD["md"]))

        # Fila 1
        row1 = ctk.CTkFrame(card, fg_color="transparent")
        row1.pack(fill="x", pady=(0, PAD["sm"]))
        self._field(row1, "nombre", "Nombre completo *",
                    side="left", expand=True)
        ctk.CTkFrame(row1, width=PAD["sm"],
                     fg_color="transparent").pack(side="left")
        self._field(row1, "dni", "DNI *", side="left")

        # Fila 2
        row2 = ctk.CTkFrame(card, fg_color="transparent")
        row2.pack(fill="x", pady=(0, PAD["sm"]))
        self._field(row2, "fecha_nacimiento",
                    "Fecha de nacimiento (AAAA-MM-DD) *", side="left")
        ctk.CTkFrame(row2, width=PAD["sm"],
                     fg_color="transparent").pack(side="left")
        self._field(row2, "telefono", "Teléfono", side="left")

        # Notas full-width
        ctk.CTkLabel(card, text="Notas / Alergias",
                     font=_font("label"),
                     text_color=C["text_secondary"],
                     fg_color="transparent").pack(anchor="w",
                                                   pady=(PAD["xs"], 4))
        _, t = make_text(card, height=3)
        t.pack(fill="x")
        self._entries["notas"] = t

    def _field(self, parent, key, label, side="left", expand=False):
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(side=side, fill="x", expand=expand)
        ctk.CTkLabel(wrap, text=label,
                     font=_font("label"),
                     text_color=C["text_secondary"],
                     fg_color="transparent").pack(anchor="w", pady=(0, 4))
        var  = tk.StringVar()
        e, _ = make_entry(wrap, textvariable=var)
        e.pack(fill="x")
        self._entries[key] = var
        return var

    def on_show(self, paciente_id=None):
        if paciente_id:
            self._paciente = db.obtener_paciente(paciente_id)
            self._title_lbl.configure(text="Editar paciente")
            p = self._paciente
            for k, v in [("nombre", p.nombre), ("dni", p.dni),
                          ("fecha_nacimiento", p.fecha_nacimiento),
                          ("telefono", p.telefono or "")]:
                self._entries[k].set(v)
            t = self._entries["notas"]
            t.delete("1.0", "end")
            t.insert("1.0", p.notas or "")
        else:
            self._paciente = None
            self._title_lbl.configure(text="Nuevo paciente")
            for k, v in self._entries.items():
                if isinstance(v, tk.StringVar):
                    v.set("")
                else:
                    v.delete("1.0", "end")

    def _guardar(self):
        nombre = self._entries["nombre"].get().strip()
        dni    = self._entries["dni"].get().strip()
        fecha  = self._entries["fecha_nacimiento"].get().strip()
        if not nombre or not dni or not fecha:
            messagebox.showwarning("Campos requeridos",
                                   "Nombre, DNI y fecha de nacimiento son obligatorios.")
            return
        telefono = self._entries["telefono"].get().strip() or None
        notas    = self._entries["notas"].get("1.0", "end").strip() or None

        if self._paciente:
            self._paciente.nombre           = nombre
            self._paciente.dni              = dni
            self._paciente.fecha_nacimiento = fecha
            self._paciente.telefono         = telefono
            self._paciente.notas            = notas
            db.editar_paciente(self._paciente)
            pid = self._paciente.id
        else:
            p   = db.crear_paciente(db.Paciente(
                nombre=nombre, dni=dni, fecha_nacimiento=fecha,
                telefono=telefono, notas=notas))
            pid = p.id

        self._get_root().toast("Paciente guardado correctamente")
        self._nav("vista_paciente", pid)

    def _volver(self):
        if self._paciente:
            self._nav("vista_paciente", self._paciente.id)
        else:
            self._nav("principal", None)

    def _get_root(self):
        w = self
        while w.master:
            w = w.master
        return w
