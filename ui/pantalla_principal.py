"""Lista de pacientes — diseño SaaS premium."""
import tkinter as tk
import customtkinter as ctk
from .styles import COLORS, FONTS, PAD, RADIUS
from .widgets import (make_entry, make_separator, make_avatar,
                      scrollable_frame, empty_state, CTAButton, _font)
from .animations import animate_row_in
import db

C  = COLORS
FF = FONTS["body"][0]


def _draw_hero_tooth(cv, cx, cy):
    """Draw a large molar tooth silhouette for the hero banner."""
    s = 1.45
    raw = [
        -18, 10,
        -16, -2,
        -12, -12,
        -6,  -6,
        0,   -16,
        6,   -6,
        12,  -12,
        16,  -2,
        18,  10,
        14,  18,
        10,  30,
        4,   18,
        0,   16,
        -4,  18,
        -10, 30,
        -14, 18,
    ]
    pts = []
    for i in range(0, len(raw), 2):
        pts.append(cx + raw[i] * s)
        pts.append(cy + raw[i + 1] * s)
    cv.create_polygon(pts, fill=C["tooth_white"], outline=C["primary_medium"],
                      width=2, smooth=True)
    # Inner highlight line on crown
    hi = [cx - 8*s, cy - 10*s, cx, cy - 14*s, cx + 8*s, cy - 10*s]
    cv.create_line(hi, fill=C["primary_medium"], width=1, smooth=True)


class PantallaPrincipal(ctk.CTkFrame):
    def __init__(self, parent, nav):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self._nav        = nav
        self._inner      = None
        self._search_var = tk.StringVar()
        self._build()
        self._search_var.trace_add("write", self._on_search)

    # ── Hero dental ───────────────────────────────────────────────────────────

    def _build_hero(self):
        hero = ctk.CTkFrame(self, fg_color=C["dental_dark"], corner_radius=0)
        hero.pack(fill="x")

        inner = ctk.CTkFrame(hero, fg_color="transparent")
        inner.pack(fill="x", padx=PAD["page"], pady=(20, 18))

        # ── Izquierda: diente canvas + título ────────────────────
        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="y")

        tooth_cv = tk.Canvas(left, width=64, height=76,
                             bg=C["dental_dark"], highlightthickness=0)
        tooth_cv.pack(side="left", padx=(0, 20))
        _draw_hero_tooth(tooth_cv, 32, 38)

        brand = ctk.CTkFrame(left, fg_color="transparent")
        brand.pack(side="left", fill="y", pady=4)

        ctk.CTkLabel(brand, text="Sistema de Gestión",
                     font=ctk.CTkFont(family=FF, size=22, weight="bold"),
                     text_color="#FFFFFF",
                     fg_color="transparent").pack(anchor="w")
        ctk.CTkLabel(brand, text="Odontológica Profesional",
                     font=ctk.CTkFont(family=FF, size=14, weight="bold"),
                     text_color=C["primary_medium"],
                     fg_color="transparent").pack(anchor="w")
        ctk.CTkLabel(brand,
                     text="Registrá y gestioná el historial clínico de tus pacientes",
                     font=ctk.CTkFont(family=FF, size=12),
                     text_color="#64748B",
                     fg_color="transparent").pack(anchor="w", pady=(6, 0))

        # ── Derecha: estadísticas ─────────────────────────────────
        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.pack(side="right", fill="y")

        n_pac  = len(db.listar_pacientes())
        n_preg = len(db.listar_preguntas(solo_activas=True))

        stats = [
            ("🦷", str(n_pac),  "Pacientes"),
            ("📋", str(n_preg), "Preguntas activas"),
            ("✓",  "Online",    "Sistema"),
        ]
        for icon, value, label in stats:
            chip = ctk.CTkFrame(right, fg_color=C["dental_navy"],
                                corner_radius=10,
                                border_width=1, border_color="#1E3A6E")
            chip.pack(fill="x", pady=3)
            row = ctk.CTkFrame(chip, fg_color="transparent")
            row.pack(padx=14, pady=8)
            ctk.CTkLabel(row, text=icon,
                         font=ctk.CTkFont(family=FF, size=16),
                         fg_color="transparent",
                         text_color=C["primary_medium"]).pack(side="left", padx=(0, 8))
            ctk.CTkLabel(row, text=value,
                         font=ctk.CTkFont(family=FF, size=15, weight="bold"),
                         text_color="#FFFFFF",
                         fg_color="transparent").pack(side="left")
            ctk.CTkLabel(row, text=f"  {label}",
                         font=ctk.CTkFont(family=FF, size=11),
                         text_color="#475569",
                         fg_color="transparent").pack(side="left")

    # ── Construcción ──────────────────────────────────────────────────────────

    def _build(self):
        # ── Hero dental banner ────────────────────────────────────
        self._build_hero()

        # ── Header con fondo blanco ───────────────────────────────
        header = ctk.CTkFrame(self, fg_color=C["surface"],
                              corner_radius=0, border_width=0)
        header.pack(fill="x")

        header_inner = ctk.CTkFrame(header, fg_color="transparent")
        header_inner.pack(fill="x", padx=PAD["page"], pady=(20, 16))

        # Fila 1: título + botón
        top_row = ctk.CTkFrame(header_inner, fg_color="transparent")
        top_row.pack(fill="x")

        title_col = ctk.CTkFrame(top_row, fg_color="transparent")
        title_col.pack(side="left")
        ctk.CTkLabel(title_col, text="Pacientes",
                     font=_font("heading"),
                     text_color=C["text"],
                     fg_color="transparent").pack(anchor="w")
        self._subtitle = ctk.CTkLabel(title_col, text="Cargando…",
                                       font=_font("body"),
                                       text_color=C["text_muted"],
                                       fg_color="transparent")
        self._subtitle.pack(anchor="w", pady=(2, 0))

        CTAButton(top_row, text="  +  Nuevo paciente",
                  command=lambda: self._nav("form_paciente", None)).pack(side="right")

        # Fila 2: búsqueda
        search_row = ctk.CTkFrame(header_inner, fg_color="transparent")
        search_row.pack(fill="x", pady=(14, 0))

        search_wrap = ctk.CTkFrame(search_row, fg_color=C["input_bg"],
                                    border_width=1, border_color=C["border"],
                                    corner_radius=RADIUS["inner"])
        search_wrap.pack(side="left", fill="x", expand=True)

        # Ícono lupa
        ctk.CTkLabel(search_wrap, text="🔍",
                     font=ctk.CTkFont(family=FF, size=13),
                     fg_color="transparent",
                     text_color=C["text_faint"]).pack(side="left", padx=(12, 4))

        entry = ctk.CTkEntry(search_wrap,
                              textvariable=self._search_var,
                              placeholder_text="Buscar por nombre o DNI…",
                              fg_color="transparent",
                              border_width=0, height=42,
                              text_color=C["text"],
                              placeholder_text_color=C["text_faint"],
                              font=_font("body"))
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # Separador fino bajo el header
        make_separator(self, color=C["border"]).pack(fill="x")

        # ── Cuerpo scrollable ─────────────────────────────────────
        body_wrap = ctk.CTkFrame(self, fg_color="transparent")
        body_wrap.pack(fill="both", expand=True)

        _, self._inner = scrollable_frame(body_wrap)
        self._render_lista(db.listar_pacientes())

    # ── Lógica de búsqueda ────────────────────────────────────────────────────

    def _on_search(self, *_):
        t = self._search_var.get().strip()
        pacientes = db.buscar_pacientes(t) if t else db.listar_pacientes()
        self._render_lista(pacientes)

    # ── Render de lista ───────────────────────────────────────────────────────

    def _render_lista(self, pacientes):
        for w in self._inner.winfo_children():
            w.destroy()

        count = len(pacientes)
        if count == 0:
            txt = "Sin resultados"
        elif count == 1:
            txt = "1 paciente registrado"
        else:
            txt = f"{count} pacientes registrados"
        self._subtitle.configure(text=txt)

        if not pacientes:
            e = empty_state(
                self._inner,
                "No hay pacientes aún",
                "Hacé clic en '+ Nuevo paciente' para agregar el primero.",
                icon="👤",
            )
            e.pack(pady=80, fill="x")
            return

        # Cabecera de columnas
        hdr = ctk.CTkFrame(self._inner, fg_color="transparent")
        hdr.pack(fill="x", padx=PAD["page"], pady=(10, 4))

        cols = [("Nombre del paciente", True),
                ("DNI",                False),
                ("Teléfono",           False)]
        for label, expand in cols:
            ctk.CTkLabel(hdr, text=label.upper(),
                         font=ctk.CTkFont(family=FF, size=9, weight="bold"),
                         text_color=C["text_faint"],
                         fg_color="transparent").pack(
                             side="left",
                             expand=expand,
                             fill="x" if expand else None,
                             padx=(0, 60) if not expand else 0)

        make_separator(self._inner,
                       color=C["border"]).pack(fill="x",
                                                padx=PAD["page"], pady=(0, 6))

        # Filas
        for i, p in enumerate(pacientes):
            self._row(p, anim_delay=i * 25)

        # Pie
        ctk.CTkFrame(self._inner, height=24,
                     fg_color="transparent").pack()

    def _row(self, p, anim_delay: int = 0):
        PX = PAD["page"]

        # ── Tarjeta de fila ───────────────────────────────────────
        # Capa de sombra
        shadow = ctk.CTkFrame(self._inner,
                               fg_color=C["shadow_soft"],
                               corner_radius=RADIUS["inner"] + 1)
        shadow.pack(fill="x", padx=PX, pady=(0, 3))

        # Tarjeta blanca
        card = ctk.CTkFrame(shadow,
                             fg_color=C["surface"],
                             corner_radius=RADIUS["inner"],
                             border_width=1,
                             border_color=C["border"],
                             cursor="hand2")
        card.pack(fill="x", padx=1, pady=(1, 2))

        # Borde de acento izquierdo (se muestra en hover)
        accent_bar = ctk.CTkFrame(card,
                                   width=3,
                                   fg_color="transparent",
                                   corner_radius=0)
        accent_bar.pack(side="left", fill="y")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="x", expand=True,
                     padx=(PAD["xs"], PAD["sm"]), pady=8)

        # Avatar
        av_bg = C["surface"]
        av = make_avatar(content, p.nombre, size=34, bg_parent=av_bg)
        av.pack(side="left", padx=(0, 10))

        # Info (nombre + meta)
        info = ctk.CTkFrame(content, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(info, text=p.nombre,
                     font=_font("label"),
                     text_color=C["text"],
                     fg_color="transparent").pack(anchor="w")

        meta = ctk.CTkFrame(info, fg_color="transparent")
        meta.pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(meta,
                     text=f"DNI {p.dni}",
                     font=_font("caption"),
                     text_color=C["text_muted"],
                     fg_color="transparent").pack(side="left")
        if p.fecha_nacimiento:
            ctk.CTkLabel(meta, text=" · ",
                         font=_font("caption"),
                         text_color=C["text_faint"],
                         fg_color="transparent").pack(side="left")
            ctk.CTkLabel(meta, text=f"Nac. {p.fecha_nacimiento}",
                         font=_font("caption"),
                         text_color=C["text_muted"],
                         fg_color="transparent").pack(side="left")

        # Teléfono (columna derecha)
        if p.telefono:
            ctk.CTkLabel(content, text=p.telefono,
                         font=_font("body_sm"),
                         text_color=C["text_secondary"],
                         fg_color="transparent").pack(side="right", padx=(0, 24))

        # Flecha
        arrow = ctk.CTkLabel(card, text="›",
                              font=ctk.CTkFont(family=FF, size=22, weight="bold"),
                              text_color=C["border_strong"],
                              fg_color="transparent")
        arrow.pack(side="right", padx=(0, PAD["sm"]))

        # ── Hover / Click ─────────────────────────────────────────
        def _all(w):
            yield w
            for ch in w.winfo_children():
                yield from _all(ch)

        all_w = list(_all(card))

        def _go(_e, pid=p.id):
            self._nav("ficha_clinica", pid)

        def _enter(_e):
            card.configure(fg_color=C["row_hover"], border_color=C["primary_muted"])
            accent_bar.configure(fg_color=C["primary"])
            arrow.configure(text_color=C["primary"])
            shadow.configure(fg_color=C["primary_muted"])

        def _leave(_e):
            card.configure(fg_color=C["surface"], border_color=C["border"])
            accent_bar.configure(fg_color="transparent")
            arrow.configure(text_color=C["border_strong"])
            shadow.configure(fg_color=C["shadow_soft"])

        for w in all_w:
            try:
                w.bind("<Button-1>", _go)
                w.bind("<Enter>",    _enter)
                w.bind("<Leave>",    _leave)
            except Exception:
                pass

        animate_row_in(shadow, delay_ms=anim_delay)

    # ── Refresh ───────────────────────────────────────────────────────────────

    def on_show(self, _=None):
        self._search_var.set("")
        self._render_lista(db.listar_pacientes())
