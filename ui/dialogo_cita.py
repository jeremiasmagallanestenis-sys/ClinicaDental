"""Diálogo para crear / editar una cita agendada."""
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from datetime import date
from .styles import COLORS, PAD, RADIUS
from .widgets import make_button, make_entry, make_separator, _font
import db

C = COLORS

HORAS = [f"{h:02d}:{m:02d}" for h in range(7, 21) for m in (0, 30)]


class DialogoCita(ctk.CTkToplevel):
    def __init__(self, parent, cita=None, fecha=None, hora=None,
                 paciente_id=None, on_guardar=None):
        super().__init__(parent)
        self._cita        = cita
        self._on_guardar  = on_guardar
        self._pre_fecha   = fecha or (date.fromisoformat(cita.fecha) if cita else date.today())
        self._pre_hora    = hora or (cita.hora if cita else "09:00")
        self._pre_pid     = paciente_id or (cita.paciente_id if cita else None)

        self.title("Editar cita" if cita else "Nueva cita")
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
        hdr = ctk.CTkFrame(self, fg_color=C["surface"], corner_radius=0)
        hdr.pack(fill="x")
        ctk.CTkLabel(hdr,
                     text="Editar cita" if self._cita else "Nueva cita",
                     font=_font("subheading"),
                     text_color=C["text"],
                     fg_color="transparent").pack(anchor="w",
                                                   padx=PAD["md"], pady=PAD["sm"])
        make_separator(self).pack(fill="x")

        body = ctk.CTkFrame(self, fg_color=C["surface"], corner_radius=0)
        body.pack(fill="both", padx=PAD["md"], pady=PAD["md"])

        # ── Paciente ──────────────────────────────────────────────
        ctk.CTkLabel(body, text="Paciente *",
                     font=_font("label"), text_color=C["text_secondary"],
                     fg_color="transparent").pack(anchor="w", pady=(0, 4))

        pacientes = db.listar_pacientes()
        self._pac_map = {f"{p.nombre}  ·  DNI {p.dni}": p.id for p in pacientes}
        opciones    = list(self._pac_map.keys())

        pre_option = opciones[0] if opciones else ""
        if self._pre_pid:
            for k, v in self._pac_map.items():
                if v == self._pre_pid:
                    pre_option = k
                    break

        self._pac_var = tk.StringVar(value=pre_option)
        self._pac_menu = ctk.CTkOptionMenu(
            body, values=opciones, variable=self._pac_var,
            fg_color=C["input_bg"], button_color=C["primary"],
            button_hover_color=C["primary_hover"],
            dropdown_fg_color=C["surface"],
            dropdown_hover_color=C["row_hover"],
            text_color=C["text"],
            font=_font("body"), dropdown_font=_font("body"),
            width=380,
        )
        self._pac_menu.pack(fill="x", pady=(0, PAD["sm"]))

        # ── Fecha y Hora ──────────────────────────────────────────
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x", pady=(0, PAD["sm"]))

        # Fecha
        f_col = ctk.CTkFrame(row, fg_color="transparent")
        f_col.pack(side="left", fill="x", expand=True, padx=(0, PAD["sm"]))
        ctk.CTkLabel(f_col, text="Fecha *",
                     font=_font("label"), text_color=C["text_secondary"],
                     fg_color="transparent").pack(anchor="w", pady=(0, 4))
        self._fecha_var = tk.StringVar(value=str(self._pre_fecha))
        e, _ = make_entry(f_col, textvariable=self._fecha_var)
        e.pack(fill="x")

        # Hora
        h_col = ctk.CTkFrame(row, fg_color="transparent")
        h_col.pack(side="left")
        ctk.CTkLabel(h_col, text="Hora *",
                     font=_font("label"), text_color=C["text_secondary"],
                     fg_color="transparent").pack(anchor="w", pady=(0, 4))

        hora_val = self._pre_hora if self._pre_hora in HORAS else "09:00"
        self._hora_var = tk.StringVar(value=hora_val)
        ctk.CTkOptionMenu(
            h_col, values=HORAS, variable=self._hora_var,
            fg_color=C["input_bg"], button_color=C["primary"],
            button_hover_color=C["primary_hover"],
            dropdown_fg_color=C["surface"],
            dropdown_hover_color=C["row_hover"],
            text_color=C["text"],
            font=_font("body"), dropdown_font=_font("body"),
            width=110,
        ).pack()

        # ── Motivo ────────────────────────────────────────────────
        ctk.CTkLabel(body, text="Motivo (opcional)",
                     font=_font("label"), text_color=C["text_secondary"],
                     fg_color="transparent").pack(anchor="w", pady=(0, 4))
        self._motivo_var = tk.StringVar(
            value=self._cita.motivo if self._cita else "")
        e2, _ = make_entry(body, textvariable=self._motivo_var)
        e2.pack(fill="x")

        make_separator(body).pack(fill="x", pady=PAD["sm"])

        # ── Botones ───────────────────────────────────────────────
        btns = ctk.CTkFrame(body, fg_color="transparent")
        btns.pack(anchor="e")

        if self._cita:
            make_button(btns, "Eliminar", small=True,
                        command=self._eliminar,
                        kind="danger_ghost").pack(side="left", padx=(0, PAD["md"]))

        make_button(btns, "Cancelar", command=self.destroy,
                    kind="secondary").pack(side="left", padx=(0, 8))
        make_button(btns, "Guardar", command=self._guardar).pack(side="left")

    def _guardar(self):
        pac_label = self._pac_var.get()
        pid       = self._pac_map.get(pac_label)
        fecha     = self._fecha_var.get().strip()
        hora      = self._hora_var.get().strip()

        if not pid or not fecha:
            messagebox.showwarning("Campos requeridos",
                                   "Seleccioná un paciente y completá la fecha.",
                                   parent=self)
            return

        motivo = self._motivo_var.get().strip()

        if self._cita:
            self._cita.paciente_id = pid
            self._cita.fecha       = fecha
            self._cita.hora        = hora
            self._cita.motivo      = motivo
            db.actualizar_cita(self._cita)
        else:
            db.crear_cita(db.Cita(
                paciente_id=pid, fecha=fecha, hora=hora, motivo=motivo))

        if self._on_guardar:
            self._on_guardar()
        self.destroy()

    def _eliminar(self):
        ok = messagebox.askokcancel(
            "Eliminar cita",
            "¿Eliminar esta cita del calendario?",
            parent=self)
        if ok:
            db.eliminar_cita(self._cita.id)
            if self._on_guardar:
                self._on_guardar()
            self.destroy()
