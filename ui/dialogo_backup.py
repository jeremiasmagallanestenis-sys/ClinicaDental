import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from datetime import datetime
from .styles import COLORS, PAD, RADIUS
from .widgets import make_button, make_separator, _font
from db.backup import (
    exportar_json, exportar_sqlite,
    restaurar_json, restaurar_sqlite,
    leer_meta_json,
)

C = COLORS


class DialogoBackup(ctk.CTkToplevel):
    def __init__(self, parent, on_restauracion=None):
        super().__init__(parent)
        self._on_restauracion = on_restauracion
        self.title("Backup de datos")
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
        header = ctk.CTkFrame(self, fg_color=C["surface"], corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="Backup de datos", font=_font("subheading"),
                     text_color=C["text"],
                     fg_color="transparent").pack(anchor="w",
                                                   padx=PAD["sm"], pady=PAD["xs"])
        make_separator(self).pack(fill="x")

        body = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        body.pack(fill="both", padx=PAD["sm"], pady=PAD["sm"])

        self._bloque(body,
            titulo="Exportar datos",
            desc="Guarda todos los pacientes y consultas en un archivo externo.",
            botones=[
                ("Exportar JSON",       self._exportar_json,   "primary"),
                ("Exportar copia .db",  self._exportar_sqlite, "secondary"),
            ],
        )

        make_separator(body, color=C["border"]).pack(fill="x", pady=PAD["xs"])

        self._bloque(body,
            titulo="Restaurar datos",
            desc="Carga datos desde un backup anterior.",
            warning="Restaurar .db reemplaza todos los datos actuales.",
            botones=[
                ("Restaurar desde JSON", self._restaurar_json,   "ghost"),
                ("Restaurar copia .db",  self._restaurar_sqlite, "danger_ghost"),
            ],
        )

        make_separator(self).pack(fill="x")
        foot = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        foot.pack(fill="x", padx=PAD["sm"], pady=PAD["xs"])
        make_button(foot, "Cerrar", command=self.destroy,
                    kind="secondary").pack(side="right")

    def _bloque(self, parent, titulo, desc, botones, warning=None):
        ctk.CTkLabel(parent, text=titulo, font=_font("label"),
                     text_color=C["text"],
                     fg_color="transparent").pack(anchor="w", pady=(0, 2))
        ctk.CTkLabel(parent, text=desc, font=_font("small"),
                     text_color=C["text_muted"],
                     fg_color="transparent",
                     wraplength=360, justify="left").pack(anchor="w")
        if warning:
            w_frame = ctk.CTkFrame(parent, fg_color=C["warning_bg"],
                                    corner_radius=RADIUS["btn"])
            w_frame.pack(anchor="w", pady=(4, 0))
            ctk.CTkLabel(w_frame, text=f"⚠  {warning}", font=_font("small"),
                         text_color=C["warning_text"],
                         fg_color="transparent").pack(padx=10, pady=6)

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(anchor="w", pady=(8, 0))
        for label, cmd, kind in botones:
            make_button(row, label, command=cmd, kind=kind,
                        small=True).pack(side="left", padx=(0, 8))

    def _exportar_json(self):
        nombre = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = filedialog.asksaveasfilename(
            parent=self, title="Guardar backup JSON",
            defaultextension=".json", initialfile=nombre,
            filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            n = exportar_json(Path(path))
            messagebox.showinfo("Exportación exitosa",
                                f"{n} paciente(s) exportados a:\n{path}", parent=self)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _exportar_sqlite(self):
        nombre = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        path = filedialog.asksaveasfilename(
            parent=self, title="Guardar copia .db",
            defaultextension=".db", initialfile=nombre,
            filetypes=[("SQLite", "*.db")])
        if not path:
            return
        try:
            exportar_sqlite(Path(path))
            messagebox.showinfo("Exportación exitosa",
                                f"Copia guardada en:\n{path}", parent=self)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _restaurar_json(self):
        path = filedialog.askopenfilename(
            parent=self, title="Seleccionar backup JSON",
            filetypes=[("JSON", "*.json")])
        if not path:
            return
        meta = leer_meta_json(Path(path))
        if not meta:
            messagebox.showerror("Archivo inválido",
                                  "El archivo no es un backup válido.", parent=self)
            return
        ok = messagebox.askokcancel(
            "Confirmar restauración",
            f"Backup del {meta.get('exportado_en', '?')}\n"
            f"{meta.get('n_pacientes','?')} paciente(s) · "
            f"{meta.get('n_consultas','?')} consulta(s)\n\n"
            "Los registros se fusionarán con los actuales. ¿Continuar?",
            parent=self)
        if not ok:
            return
        try:
            conteos = restaurar_json(Path(path), modo="fusionar")
            messagebox.showinfo("Restauración exitosa",
                                f"Importados: {conteos['pacientes']} pacientes, "
                                f"{conteos['consultas']} consultas.", parent=self)
            if self._on_restauracion:
                self._on_restauracion()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _restaurar_sqlite(self):
        path = filedialog.askopenfilename(
            parent=self, title="Seleccionar copia .db",
            filetypes=[("SQLite", "*.db")])
        if not path:
            return
        ok = messagebox.askokcancel(
            "Confirmar restauración",
            "⚠ Esta operación reemplazará TODOS los datos actuales.\n\n¿Deseás continuar?",
            parent=self, icon="warning")
        if not ok:
            return
        try:
            restaurar_sqlite(Path(path))
            messagebox.showinfo("Restauración exitosa",
                                "Base de datos restaurada.", parent=self)
            if self._on_restauracion:
                self._on_restauracion()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)
