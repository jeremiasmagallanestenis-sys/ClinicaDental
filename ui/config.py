"""Pantalla de configuración de preguntas — diseño premium."""
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from .styles import COLORS, PAD, RADIUS
from .widgets import (make_button, make_entry, make_separator,
                      make_card, scrollable_frame, _font)
import db

C = COLORS


class PantallaConfig(ctk.CTkFrame):
    def __init__(self, parent, nav):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self._nav = nav
        self._build()

    def _build(self):
        # ── Header ───────────────────────────────────────────────
        topbar = ctk.CTkFrame(self, fg_color=C["surface"], corner_radius=0)
        topbar.pack(fill="x")
        inner  = ctk.CTkFrame(topbar, fg_color="transparent")
        inner.pack(fill="x", padx=PAD["page"], pady=PAD["md"])

        make_button(inner, "← Volver",
                    command=lambda: self._nav("principal", None),
                    kind="ghost").pack(side="left")
        ctk.CTkLabel(inner, text="Configuración",
                     font=_font("heading"),
                     text_color=C["text"],
                     fg_color="transparent").pack(side="left", padx=(PAD["md"], 0))

        make_separator(self).pack(fill="x")

        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True)
        _, body = scrollable_frame(wrap)

        # ── Cabecera de sección ───────────────────────────────────
        PX = PAD["page"]
        sec = ctk.CTkFrame(body, fg_color="transparent")
        sec.pack(fill="x", padx=PX, pady=(PAD["xl"], PAD["xs"]))

        col = ctk.CTkFrame(sec, fg_color="transparent")
        col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(col, text="Preguntas de diagnóstico",
                     font=_font("subheading"),
                     text_color=C["text"],
                     fg_color="transparent").pack(anchor="w")
        ctk.CTkLabel(col,
                     text="Estas preguntas aparecen al registrar cada nueva consulta.",
                     font=_font("body"),
                     text_color=C["text_muted"],
                     fg_color="transparent").pack(anchor="w", pady=(2, 0))

        make_button(sec, "+  Nueva pregunta",
                    command=lambda: self._abrir_editor(None),
                    kind="primary").pack(side="right", anchor="n")

        make_separator(body, color=C["border"]).pack(
            fill="x", padx=PX, pady=(PAD["xs"], PAD["sm"]))

        self._lista = ctk.CTkFrame(body, fg_color="transparent")
        self._lista.pack(fill="x", padx=PX)
        self._render_lista()

    def _render_lista(self):
        for w in self._lista.winfo_children():
            w.destroy()

        preguntas = db.listar_preguntas(solo_activas=False)
        if not preguntas:
            ctk.CTkLabel(self._lista,
                         text="No hay preguntas configuradas.",
                         font=_font("body"),
                         text_color=C["text_muted"],
                         fg_color="transparent").pack(pady=32)
            return

        for p in preguntas:
            self._pregunta_row(p)

    def _pregunta_row(self, p):
        is_active = p.activa

        shadow, inner = make_card(self._lista, pad_x=PAD["md"], pad_y=PAD["sm"])
        if not is_active:
            shadow.configure(fg_color=C["border"])

        shadow.pack(fill="x", pady=(0, 6))

        # Indicador de tipo
        tipo_icon  = "☑" if p.tipo == "boolean" else "⌨"
        tipo_label = "Sí / No" if p.tipo == "boolean" else "Texto"
        tipo_bg    = C["primary_light"] if is_active else C["tag_gray_bg"]
        tipo_fg    = C["primary"]       if is_active else C["text_muted"]
        txt_color  = C["text"]          if is_active else C["text_muted"]

        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        name_row = ctk.CTkFrame(left, fg_color="transparent")
        name_row.pack(anchor="w")

        # Badge de tipo
        badge = ctk.CTkFrame(name_row, fg_color=tipo_bg,
                              corner_radius=RADIUS["pill"])
        badge.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(badge, text=f"{tipo_icon} {tipo_label}",
                     font=_font("caption"),
                     text_color=tipo_fg,
                     fg_color="transparent").pack(padx=8, pady=3)

        ctk.CTkLabel(name_row, text=p.texto,
                     font=_font("label"),
                     text_color=txt_color,
                     fg_color="transparent").pack(side="left")

        if not is_active:
            inactive_badge = ctk.CTkFrame(name_row,
                                           fg_color=C["tag_gray_bg"],
                                           corner_radius=RADIUS["pill"])
            inactive_badge.pack(side="left", padx=(8, 0))
            ctk.CTkLabel(inactive_badge, text="Desactivada",
                         font=_font("caption"),
                         text_color=C["text_muted"],
                         fg_color="transparent").pack(padx=8, pady=3)

        # Botones
        btns = ctk.CTkFrame(inner, fg_color="transparent")
        btns.pack(side="right")

        make_button(btns, "Editar", small=True,
                    command=lambda pid=p.id: self._abrir_editor(pid),
                    kind="secondary").pack(side="left", padx=(0, 6))

        if is_active:
            make_button(btns, "Desactivar", small=True,
                        command=lambda pid=p.id: self._desactivar(pid),
                        kind="danger_ghost").pack(side="left")
        else:
            make_button(btns, "Reactivar", small=True,
                        command=lambda pid=p.id: self._reactivar(pid),
                        kind="ghost").pack(side="left")

    def _abrir_editor(self, pregunta_id):
        p = None
        if pregunta_id:
            todas = db.listar_preguntas(solo_activas=False)
            p = next((x for x in todas if x.id == pregunta_id), None)
        EditorPregunta(self.winfo_toplevel(), p, on_guardar=self._render_lista)

    def _desactivar(self, pid):
        ok = messagebox.askokcancel(
            "Desactivar pregunta",
            "No aparecerá en nuevas consultas.\n"
            "Las respuestas históricas se conservan.",
            parent=self.winfo_toplevel())
        if ok:
            db.eliminar_pregunta(pid)
            self._render_lista()

    def _reactivar(self, pid):
        todas = db.listar_preguntas(solo_activas=False)
        p = next((x for x in todas if x.id == pid), None)
        if p:
            p.activa = True
            db.actualizar_pregunta(p)
            self._render_lista()

    def on_show(self, _=None):
        self._render_lista()


class EditorPregunta(ctk.CTkToplevel):
    def __init__(self, parent, pregunta, on_guardar):
        super().__init__(parent)
        self._pregunta   = pregunta
        self._on_guardar = on_guardar
        self.title("Editar pregunta" if pregunta else "Nueva pregunta")
        self.resizable(False, False)
        self.configure(fg_color=C["bg"])
        self.grab_set()
        self._build()
        self._center()

    def _center(self):
        self.update_idletasks()
        pw, ph = self.master.winfo_width(), self.master.winfo_height()
        px, py = self.master.winfo_x(), self.master.winfo_y()
        w, h   = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{px + (pw - w) // 2}+{py + (ph - h) // 2}")

    def _build(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=C["surface"], corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header,
                     text="Editar pregunta" if self._pregunta else "Nueva pregunta",
                     font=_font("subheading"),
                     text_color=C["text"],
                     fg_color="transparent").pack(
                         anchor="w", padx=PAD["md"], pady=PAD["sm"])
        make_separator(self).pack(fill="x")

        body = ctk.CTkFrame(self, fg_color=C["surface"], corner_radius=0)
        body.pack(fill="both", padx=PAD["md"], pady=PAD["md"])

        ctk.CTkLabel(body, text="Texto de la pregunta",
                     font=_font("label"),
                     text_color=C["text_secondary"],
                     fg_color="transparent").pack(anchor="w", pady=(0, 4))
        self._texto_var = tk.StringVar(
            value=self._pregunta.texto if self._pregunta else "")
        e, _ = make_entry(body, textvariable=self._texto_var)
        e.pack(fill="x")

        ctk.CTkLabel(body, text="Tipo de respuesta",
                     font=_font("label"),
                     text_color=C["text_secondary"],
                     fg_color="transparent").pack(anchor="w",
                                                   pady=(PAD["sm"], 4))

        self._tipo_var = tk.StringVar(
            value=self._pregunta.tipo if self._pregunta else "boolean")

        for label, val in [("Sí / No (checkbox)", "boolean"),
                            ("Texto libre",        "text")]:
            ctk.CTkRadioButton(
                body, text=label, variable=self._tipo_var, value=val,
                font=_font("body"), text_color=C["text"],
                fg_color=C["primary"], hover_color=C["primary_hover"],
            ).pack(anchor="w", pady=3)

        make_separator(body).pack(fill="x", pady=PAD["sm"])

        btns = ctk.CTkFrame(body, fg_color="transparent")
        btns.pack(anchor="e")
        make_button(btns, "Cancelar", command=self.destroy,
                    kind="secondary").pack(side="left", padx=(0, 8))
        make_button(btns, "Guardar", command=self._guardar).pack(side="left")

    def _guardar(self):
        texto = self._texto_var.get().strip()
        if not texto:
            messagebox.showwarning("Campo requerido",
                                   "El texto no puede estar vacío.", parent=self)
            return
        tipo = self._tipo_var.get()
        if self._pregunta:
            self._pregunta.texto = texto
            self._pregunta.tipo  = tipo
            db.actualizar_pregunta(self._pregunta)
        else:
            todas = db.listar_preguntas(solo_activas=False)
            orden = max((p.orden for p in todas), default=-1) + 1
            db.crear_pregunta(db.Pregunta(texto=texto, tipo=tipo, orden=orden))
        self._on_guardar()
        self.destroy()
