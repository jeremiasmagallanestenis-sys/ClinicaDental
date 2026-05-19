"""Vista de paciente con historial de consultas — diseño premium."""
import customtkinter as ctk
from .styles import COLORS, FONTS, PAD, RADIUS
from .widgets import (make_button, make_separator, make_avatar, make_tag,
                      make_card, scrollable_frame, empty_state, _font)
import db

C  = COLORS
FF = FONTS["body"][0]


class VistaPaciente(ctk.CTkFrame):
    def __init__(self, parent, nav):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self._nav      = nav
        self._paciente = None
        self._build()

    def _build(self):
        # ── Header ───────────────────────────────────────────────
        topbar = ctk.CTkFrame(self, fg_color=C["surface"], corner_radius=0)
        topbar.pack(fill="x")
        inner  = ctk.CTkFrame(topbar, fg_color="transparent")
        inner.pack(fill="x", padx=PAD["page"], pady=PAD["md"])

        make_button(inner, "← Pacientes",
                    command=lambda: self._nav("principal", None),
                    kind="ghost").pack(side="left")

        make_button(inner, "Editar datos",
                    command=self._editar, kind="secondary").pack(side="right")
        make_button(inner, "📅  Agendar consulta",
                    command=self._agendar,
                    kind="ghost").pack(side="right", padx=(0, 8))
        make_button(inner, "📋  Ficha clínica",
                    command=self._abrir_ficha,
                    kind="primary").pack(side="right", padx=(0, 8))

        make_separator(self, color=C["border"]).pack(fill="x")

        # ── Scroll ───────────────────────────────────────────────
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True)
        _, self._body = scrollable_frame(wrap)

    def on_show(self, paciente_id):
        self._paciente = db.obtener_paciente(paciente_id)
        for w in self._body.winfo_children():
            w.destroy()
        self._render_hero()
        self._render_historial()

    # ── Hero del paciente ─────────────────────────────────────────────────────

    def _render_hero(self):
        p   = self._paciente
        PX  = PAD["page"]

        shadow, card = make_card(self._body, pad_x=PAD["lg"], pad_y=PAD["lg"])
        shadow.pack(fill="x", padx=PX, pady=(PAD["xl"], PAD["md"]))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x")

        # Avatar grande
        make_avatar(row, p.nombre, size=64,
                    bg_parent=C["surface"]).pack(side="left", padx=(0, 20))

        # Info
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(info, text=p.nombre, font=_font("heading"),
                     text_color=C["text"],
                     fg_color="transparent").pack(anchor="w")

        # Chips de datos
        chips = ctk.CTkFrame(info, fg_color="transparent")
        chips.pack(anchor="w", pady=(8, 0))

        chip_data = [
            ("DNI", p.dni,              C["tag_blue_bg"],   C["tag_blue_fg"]),
            ("Nac.", p.fecha_nacimiento, C["tag_gray_bg"],   C["text_secondary"]),
            ("Tel.", p.telefono or "—", C["tag_gray_bg"],   C["text_secondary"]),
        ]
        for lbl, val, bg, fg in chip_data:
            f = ctk.CTkFrame(chips, fg_color=bg, corner_radius=RADIUS["pill"])
            f.pack(side="left", padx=(0, 6))
            ctk.CTkLabel(f, text=f"{lbl}  {val}",
                         font=_font("caption"),
                         text_color=fg,
                         fg_color="transparent").pack(padx=10, pady=4)

        if p.notas:
            make_separator(card, color=C["border"]).pack(fill="x", pady=PAD["xs"])
            ctk.CTkLabel(card, text="Notas / Alergias",
                         font=_font("caption_bold" if "caption_bold" in FONTS else "caption"),
                         text_color=C["text_muted"],
                         fg_color="transparent").pack(anchor="w")
            ctk.CTkLabel(card, text=p.notas,
                         font=_font("body"),
                         text_color=C["text_secondary"],
                         fg_color="transparent",
                         wraplength=680, justify="left").pack(anchor="w", pady=(4, 0))

    # ── Historial de consultas ────────────────────────────────────────────────

    def _render_historial(self):
        p  = self._paciente
        PX = PAD["page"]

        # Cabecera de sección
        sec = ctk.CTkFrame(self._body, fg_color="transparent")
        sec.pack(fill="x", padx=PX, pady=(0, PAD["sm"]))
        ctk.CTkLabel(sec, text="Historial de consultas",
                     font=_font("subheading"),
                     text_color=C["text"],
                     fg_color="transparent").pack(side="left")

        consultas = db.historial_paciente(p.id)
        if not consultas:
            e = empty_state(self._body,
                            "Sin consultas registradas",
                            "Las consultas se registran desde la ficha clínica.")
            e.pack(pady=40, fill="x")
            return

        for c in consultas:
            self._consulta_card(c)

        ctk.CTkFrame(self._body, height=32,
                     fg_color="transparent").pack()

    def _consulta_card(self, c):
        PX = PAD["page"]

        shadow, inner = make_card(self._body, pad_x=PAD["lg"], pad_y=PAD["md"])
        shadow.pack(fill="x", padx=PX, pady=(0, 8))

        # ── Fila superior: fecha + motivo + separador ─────────────
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")

        # Badge de fecha (prominente)
        date_box = ctk.CTkFrame(top, fg_color=C["primary"],
                                 corner_radius=RADIUS["pill"])
        date_box.pack(side="left")
        ctk.CTkLabel(date_box, text=c.fecha,
                     font=ctk.CTkFont(family=FF, size=11, weight="bold"),
                     text_color="white",
                     fg_color="transparent").pack(padx=12, pady=5)

        ctk.CTkLabel(top, text=c.motivo,
                     font=_font("subheading"),
                     text_color=C["text"],
                     fg_color="transparent").pack(side="left", padx=(14, 0))

        # ── Síntomas ──────────────────────────────────────────────
        respuestas = db.obtener_respuestas(c.id)
        sintomas_bool, textos = [], []

        if respuestas:
            idx = {p.id: p for p in db.listar_preguntas(solo_activas=False)}
            for pid, valor in respuestas.items():
                p = idx.get(pid)
                if not p:
                    continue
                if p.tipo == "boolean" and valor == "1":
                    sintomas_bool.append(p.texto)
                elif p.tipo == "text" and valor:
                    textos.append((p.texto, valor))
        else:
            diag = db.obtener_diagnostico(c.id)
            if diag:
                if diag.dolor:         sintomas_bool.append("Dolor")
                if diag.sensibilidad:  sintomas_bool.append("Sensibilidad")
                if diag.sangrado:      sintomas_bool.append("Sangrado")
                if diag.zona_afectada: textos.append(("Zona", diag.zona_afectada))

        if sintomas_bool:
            chips = ctk.CTkFrame(inner, fg_color="transparent")
            chips.pack(anchor="w", pady=(10, 0))
            for s in sintomas_bool:
                make_tag(chips, s,
                         bg=C["tag_yellow_bg"], fg=C["tag_yellow_fg"]).pack(
                             side="left", padx=(0, 6))

        for lbl, val in textos:
            ctk.CTkLabel(inner, text=f"{lbl}: {val}",
                         font=_font("body_sm"),
                         text_color=C["text_muted"],
                         fg_color="transparent").pack(anchor="w", pady=(4, 0))

        # ── Detalles clínicos ─────────────────────────────────────
        secciones = [
            ("Diagnóstico",  c.diagnostico),
            ("Tratamiento",  c.tratamiento),
            ("Observaciones",c.observaciones),
        ]
        hay = any(v for _, v in secciones)
        if hay:
            make_separator(inner, color=C["border"]).pack(fill="x", pady=(10, 8))
            grid = ctk.CTkFrame(inner, fg_color="transparent")
            grid.pack(fill="x")
            for lbl, val in secciones:
                if val:
                    row = ctk.CTkFrame(grid, fg_color="transparent")
                    row.pack(fill="x", pady=(0, 6))
                    ctk.CTkLabel(row, text=lbl,
                                 font=ctk.CTkFont(family=FF, size=10, weight="bold"),
                                 text_color=C["text_faint"],
                                 fg_color="transparent",
                                 width=100, anchor="w").pack(side="left")
                    ctk.CTkLabel(row, text=val,
                                 font=_font("body"),
                                 text_color=C["text_secondary"],
                                 fg_color="transparent",
                                 wraplength=580, justify="left",
                                 anchor="w").pack(side="left", fill="x", expand=True)

    def _editar(self):
        if self._paciente:
            self._nav("form_paciente", self._paciente.id)

    def _abrir_ficha(self):
        if self._paciente:
            self._nav("ficha_clinica", self._paciente.id)

    def _agendar(self):
        if self._paciente:
            self._nav("calendario", self._paciente.id)
