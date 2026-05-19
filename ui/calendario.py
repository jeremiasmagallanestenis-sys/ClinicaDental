"""Pantalla de calendario de citas — diseño SaaS moderno."""
import calendar
import tkinter as tk
import customtkinter as ctk
from datetime import date, timedelta
from .styles import COLORS, PAD, RADIUS, FONTS
from .widgets import make_button, make_separator, _font
import db

C  = COLORS
FF = FONTS["body"][0]

DIAS  = ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"]
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

CITA_PALETA = [
    ("#DBEAFE", "#1D4ED8"), ("#D1FAE5", "#065F46"),
    ("#FEF3C7", "#92400E"), ("#FCE7F3", "#9D174D"),
    ("#E0E7FF", "#3730A3"), ("#FFEDD5", "#C2410C"),
]

# Constantes vista semanal (canvas)
TIME_W  = 68
DAY_W   = 112
ROW_H   = 46
HEAD_H  = 56
START_H = 7
END_H   = 21
SLOTS   = (END_H - START_H) * 2


class PantallaCalendario(ctk.CTkFrame):
    def __init__(self, parent, nav):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self._nav   = nav
        self._vista = "semanal"
        self._hoy   = date.today()
        self._ref   = self._hoy - timedelta(days=self._hoy.weekday())
        self._build_shell()

    # ── Shell ─────────────────────────────────────────────────────────────────

    def _build_shell(self):
        # Topbar
        topbar = ctk.CTkFrame(self, fg_color=C["surface"], corner_radius=0)
        topbar.pack(fill="x")
        inner = ctk.CTkFrame(topbar, fg_color="transparent")
        inner.pack(fill="x", padx=PAD["page"], pady=PAD["md"])

        ctk.CTkLabel(inner, text="Calendario",
                     font=_font("heading"),
                     text_color=C["text"],
                     fg_color="transparent").pack(side="left")

        # Toggle mensual / semanal
        tog = ctk.CTkFrame(inner, fg_color=C["bg"],
                            corner_radius=RADIUS["btn"],
                            border_width=1, border_color=C["border"])
        tog.pack(side="right")

        self._btn_s = ctk.CTkButton(
            tog, text="Semanal", width=96, height=32,
            corner_radius=RADIUS["btn"] - 1,
            font=ctk.CTkFont(family=FF, size=13, weight="bold"),
            fg_color=C["primary"], text_color="white",
            hover_color=C["primary_hover"],
            command=lambda: self._set_vista("semanal"))
        self._btn_s.pack(side="left", padx=2, pady=2)

        self._btn_m = ctk.CTkButton(
            tog, text="Mensual", width=96, height=32,
            corner_radius=RADIUS["btn"] - 1, font=_font("body"),
            fg_color="transparent", text_color=C["text_secondary"],
            hover_color=C["row_hover"],
            command=lambda: self._set_vista("mensual"))
        self._btn_m.pack(side="left", padx=(0, 2), pady=2)

        make_separator(self).pack(fill="x")

        # ── Agenda de hoy ─────────────────────────────────────────
        self._agenda_frame = ctk.CTkFrame(self, fg_color=C["dental_dark"],
                                           corner_radius=0)
        self._agenda_frame.pack(fill="x")
        self._render_agenda_hoy()

        # Nav bar (mes/semana + flechas)
        nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        nav_bar.pack(fill="x", padx=PAD["page"], pady=(PAD["md"], PAD["xs"]))

        self._title = ctk.CTkLabel(nav_bar, text="",
                                    font=_font("subheading"),
                                    text_color=C["text"],
                                    fg_color="transparent")
        self._title.pack(side="left")

        make_button(nav_bar, " › ", command=self._siguiente,
                    kind="ghost", small=True).pack(side="right")
        make_button(nav_bar, " ‹ ", command=self._anterior,
                    kind="ghost", small=True).pack(side="right")
        make_button(nav_bar, "Hoy", command=self._ir_hoy,
                    kind="secondary", small=True).pack(side="right", padx=(0, 8))
        make_button(nav_bar, "+  Nueva cita",
                    command=lambda: self._abrir_dialogo(),
                    kind="primary", small=True).pack(side="right", padx=(0, 12))

        # Body (se re-renderiza)
        self._body = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self._body.pack(fill="both", expand=True,
                        padx=PAD["page"], pady=(0, PAD["page"]))

        self._render()

    # ── Navegación ────────────────────────────────────────────────────────────

    def _set_vista(self, vista):
        self._vista = vista
        if vista == "mensual":
            self._btn_m.configure(fg_color=C["primary"], text_color="white")
            self._btn_s.configure(fg_color="transparent",
                                   text_color=C["text_secondary"])
            self._ref = self._hoy.replace(day=1)
        else:
            self._btn_s.configure(fg_color=C["primary"], text_color="white")
            self._btn_m.configure(fg_color="transparent",
                                   text_color=C["text_secondary"])
            self._ref = self._hoy - timedelta(days=self._hoy.weekday())
        self._render()

    def _anterior(self):
        if self._vista == "mensual":
            m, y = self._ref.month - 1, self._ref.year
            if m == 0:
                m, y = 12, y - 1
            self._ref = date(y, m, 1)
        else:
            self._ref -= timedelta(weeks=1)
        self._render()

    def _siguiente(self):
        if self._vista == "mensual":
            m, y = self._ref.month + 1, self._ref.year
            if m == 13:
                m, y = 1, y + 1
            self._ref = date(y, m, 1)
        else:
            self._ref += timedelta(weeks=1)
        self._render()

    def _ir_hoy(self):
        if self._vista == "mensual":
            self._ref = self._hoy.replace(day=1)
        else:
            self._ref = self._hoy - timedelta(days=self._hoy.weekday())
        self._render()

    def _render(self):
        for w in self._body.winfo_children():
            w.destroy()
        if self._vista == "mensual":
            self._render_mensual()
        else:
            self._render_semanal()

    # ── Vista mensual ─────────────────────────────────────────────────────────

    def _render_mensual(self):
        y, m = self._ref.year, self._ref.month
        self._title.configure(text=f"{MESES[m - 1]}  {y}")

        citas = db.listar_citas_mes(y, m)
        por_fecha: dict = {}
        for c in citas:
            por_fecha.setdefault(c.fecha, []).append(c)

        # Contenedor con borde
        grid = ctk.CTkFrame(self._body, fg_color=C["surface"],
                             corner_radius=RADIUS["card"],
                             border_width=1, border_color=C["border"])
        grid.pack(fill="both", expand=True)

        # Cabecera de días
        for col, dia in enumerate(DIAS):
            grid.grid_columnconfigure(col, weight=1, uniform="col")
            hdr = ctk.CTkFrame(grid, fg_color=C["surface_2"], corner_radius=0)
            hdr.grid(row=0, column=col, sticky="nsew")
            ctk.CTkLabel(hdr, text=dia,
                         font=ctk.CTkFont(family=FF, size=10, weight="bold"),
                         text_color=C["text_faint"],
                         fg_color="transparent").pack(pady=9)

        # Separador
        sep = ctk.CTkFrame(grid, fg_color=C["border"], height=1, corner_radius=0)
        sep.grid(row=1, column=0, columnspan=7, sticky="ew")

        weeks = calendar.monthcalendar(y, m)
        for wi, week in enumerate(weeks):
            grid.grid_rowconfigure(wi + 2, weight=1, minsize=100)
            for col, day_num in enumerate(week):
                # Separadores de celda
                if col > 0:
                    ctk.CTkFrame(grid, fg_color=C["border"],
                                 width=1, corner_radius=0).grid(
                        row=wi + 2, column=col,
                        sticky="nws", padx=(0, 0))

                is_today = day_num != 0 and date(y, m, day_num) == self._hoy
                empty    = day_num == 0

                cell = ctk.CTkFrame(grid,
                                     fg_color=C["bg"] if empty else C["surface"],
                                     corner_radius=0, cursor="hand2" if not empty else "")
                cell.grid(row=wi + 2, column=col, sticky="nsew", padx=(1, 0), pady=(1, 0))

                if not empty:
                    top = ctk.CTkFrame(cell, fg_color="transparent")
                    top.pack(fill="x", padx=6, pady=(5, 2))

                    if is_today:
                        badge = ctk.CTkFrame(top, fg_color=C["primary"],
                                              corner_radius=14, width=26, height=26)
                        badge.pack(side="right")
                        badge.pack_propagate(False)
                        ctk.CTkLabel(badge, text=str(day_num),
                                     font=ctk.CTkFont(family=FF, size=11, weight="bold"),
                                     text_color="white",
                                     fg_color="transparent").pack(expand=True)
                    else:
                        ctk.CTkLabel(top, text=str(day_num),
                                     font=ctk.CTkFont(family=FF, size=11),
                                     text_color=C["text_secondary"],
                                     fg_color="transparent").pack(side="right")

                    fecha_str = date(y, m, day_num).isoformat()
                    for i, cita in enumerate(por_fecha.get(fecha_str, [])[:3]):
                        ci  = cita.paciente_id % len(CITA_PALETA)
                        bg, fg = CITA_PALETA[ci]
                        pill = ctk.CTkFrame(cell, fg_color=bg, corner_radius=4)
                        pill.pack(fill="x", padx=5, pady=1)
                        nombre = cita.paciente_nombre.split()[0]
                        ctk.CTkLabel(pill,
                                     text=f"  {cita.hora}  {nombre}",
                                     font=ctk.CTkFont(family=FF, size=10),
                                     text_color=fg, fg_color="transparent",
                                     anchor="w").pack(anchor="w", padx=3, pady=2)

                    extras = len(por_fecha.get(fecha_str, [])) - 3
                    if extras > 0:
                        ctk.CTkLabel(cell, text=f"+{extras} más",
                                     font=ctk.CTkFont(family=FF, size=9),
                                     text_color=C["text_faint"],
                                     fg_color="transparent").pack(anchor="w", padx=7)

                    # Hover + click
                    fecha_click = date(y, m, day_num)

                    def _hover_on(_, c=cell):
                        c.configure(fg_color=C["row_hover"])

                    def _hover_off(_, c=cell):
                        c.configure(fg_color=C["surface"])

                    def _click(_, f=fecha_click):
                        self._abrir_dialogo(fecha=f)

                    def _bind_all(w, enter, leave, click):
                        try:
                            w.bind("<Enter>",    enter, add="+")
                            w.bind("<Leave>",    leave, add="+")
                            w.bind("<Button-1>", click, add="+")
                        except Exception:
                            pass

                    for child in [cell] + list(self._descendants(cell)):
                        _bind_all(child, _hover_on, _hover_off, _click)

            # Separador horizontal entre semanas
            if wi < len(weeks) - 1:
                ctk.CTkFrame(grid, fg_color=C["border"],
                             height=1, corner_radius=0).grid(
                    row=wi + 3, column=0, columnspan=7, sticky="ew")

    # ── Vista semanal ─────────────────────────────────────────────────────────

    def _render_semanal(self):
        lunes = self._ref - timedelta(days=self._ref.weekday())
        dias  = [lunes + timedelta(days=i) for i in range(7)]
        fin   = dias[-1]

        if lunes.month == fin.month:
            title = f"{lunes.day} – {fin.day}  {MESES[lunes.month - 1]}  {lunes.year}"
        else:
            title = (f"{lunes.day} {MESES[lunes.month-1]} – "
                     f"{fin.day} {MESES[fin.month-1]}  {lunes.year}")
        self._title.configure(text=title)

        citas = db.listar_citas_semana(lunes.isoformat())
        por   = {}
        for c in citas:
            por.setdefault((c.fecha, c.hora), []).append(c)

        total_w = TIME_W + 7 * DAY_W
        total_h = HEAD_H + SLOTS * ROW_H

        wrap = ctk.CTkFrame(self._body, fg_color=C["surface"],
                             corner_radius=RADIUS["card"],
                             border_width=1, border_color=C["border"])
        wrap.pack(fill="both", expand=True)

        cv  = tk.Canvas(wrap, bg=C["surface"], highlightthickness=0,
                         width=total_w, height=total_h)
        vsb = tk.Scrollbar(wrap, orient="vertical", command=cv.yview)
        cv.configure(yscrollcommand=vsb.set,
                      scrollregion=(0, 0, total_w, total_h))
        vsb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)

        cv.bind("<MouseWheel>",
                lambda e: cv.yview_scroll(int(-e.delta), "units"))

        # ── Cabecera ──────────────────────────────────────────────
        cv.create_rectangle(0, 0, total_w, HEAD_H,
                             fill=C["surface_2"], outline="")
        cv.create_line(0, HEAD_H, total_w, HEAD_H,
                        fill=C["border"], width=1)
        cv.create_line(TIME_W, 0, TIME_W, total_h,
                        fill=C["border"], width=1)

        for col, dia in enumerate(dias):
            x     = TIME_W + col * DAY_W
            today = dia == self._hoy

            if today:
                cv.create_rectangle(x, 0, x + DAY_W, HEAD_H,
                                     fill=C["primary_light"], outline="")

            cv.create_text(x + DAY_W // 2, HEAD_H // 2 - 10,
                            text=DIAS[col],
                            fill=C["primary"] if today else C["text_faint"],
                            font=(FF, 10, "bold"))

            if today:
                r = 14
                cx_c, cy_c = x + DAY_W // 2, HEAD_H // 2 + 11
                cv.create_oval(cx_c - r, cy_c - r, cx_c + r, cy_c + r,
                                fill=C["primary"], outline="")
                cv.create_text(cx_c, cy_c, text=str(dia.day),
                                fill="white", font=(FF, 13, "bold"))
            else:
                cv.create_text(x + DAY_W // 2, HEAD_H // 2 + 11,
                                text=str(dia.day),
                                fill=C["text"], font=(FF, 13))

            if col < 6:
                cv.create_line(x + DAY_W, HEAD_H, x + DAY_W, total_h,
                                fill=C["border"], width=1)

        # ── Franjas horarias ──────────────────────────────────────
        for slot in range(SLOTS):
            h_num = START_H + slot // 2
            mins  = "00" if slot % 2 == 0 else "30"
            y     = HEAD_H + slot * ROW_H

            line_col = C["border"] if slot % 2 == 0 else "#F1F5F9"
            cv.create_line(TIME_W, y, total_w, y, fill=line_col, width=1)

            if slot % 2 == 0:
                cv.create_text(TIME_W - 8, y + 5,
                                text=f"{h_num:02d}:00",
                                fill=C["text_muted"],
                                font=(FF, 10), anchor="e")

            hora_str = f"{h_num:02d}:{mins}"

            for col, dia in enumerate(dias):
                x        = TIME_W + col * DAY_W
                fecha_s  = dia.isoformat()
                slot_key = (fecha_s, hora_str)
                citas_s  = por.get(slot_key, [])

                if citas_s:
                    c_obj = citas_s[0]
                    ci    = c_obj.paciente_id % len(CITA_PALETA)
                    bg, fg = CITA_PALETA[ci]
                    bx, by = x + 3, y + 3
                    bw, bh = DAY_W - 6, ROW_H - 5

                    cv.create_rectangle(bx, by, bx + bw, by + bh,
                                         fill=bg, outline=fg, width=1)
                    nombre = c_obj.paciente_nombre.split()[0]
                    cv.create_text(bx + 7, by + bh // 2,
                                    text=f"{hora_str}  {nombre}",
                                    fill=fg, font=(FF, 9, "bold"), anchor="w")

                    tag = f"c{c_obj.id}"
                    cv.create_rectangle(bx, by, bx + bw, by + bh,
                                         fill="", outline="", tags=tag)
                    cv.tag_bind(tag, "<Button-1>",
                                 lambda _, c=c_obj: self._abrir_dialogo(cita=c))
                else:
                    tag = f"s_{fecha_s}_{slot}"
                    cv.create_rectangle(x, y, x + DAY_W, y + ROW_H,
                                         fill="", outline="", tags=tag)
                    cv.tag_bind(tag, "<Button-1>",
                                 lambda _, f=dia, h=hora_str:
                                 self._abrir_dialogo(fecha=f, hora=h))

        # Scroll hasta las 8:00 al abrir
        cv.after(60, lambda: cv.yview_moveto(
            (HEAD_H + ROW_H) / total_h))

    # ── Agenda de hoy ─────────────────────────────────────────────────────────

    def _render_agenda_hoy(self):
        for w in self._agenda_frame.winfo_children():
            w.destroy()

        from datetime import date as _date
        hoy       = _date.today()
        citas_hoy = db.listar_citas_mes(hoy.year, hoy.month)
        citas_hoy = [c for c in citas_hoy if c.fecha == hoy.isoformat()]
        citas_hoy.sort(key=lambda c: c.hora)

        inner = ctk.CTkFrame(self._agenda_frame, fg_color="transparent")
        inner.pack(fill="x", padx=PAD["page"], pady=PAD["md"])

        # Título + fecha
        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="y")

        MESES_ES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
                    "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
        dia_sem  = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
        ctk.CTkLabel(left,
                     text=f"📅  Hoy — {dia_sem[hoy.weekday()]} {hoy.day} de {MESES_ES[hoy.month-1]}",
                     font=ctk.CTkFont(family=FF, size=13, weight="bold"),
                     text_color="#FFFFFF", fg_color="transparent").pack(anchor="w")

        if not citas_hoy:
            ctk.CTkLabel(left, text="Sin citas programadas para hoy.",
                         font=ctk.CTkFont(family=FF, size=11),
                         text_color="#64748B", fg_color="transparent").pack(anchor="w", pady=(3, 0))
        else:
            ctk.CTkLabel(left,
                         text=f"{len(citas_hoy)} cita{'s' if len(citas_hoy) > 1 else ''} agendada{'s' if len(citas_hoy) > 1 else ''}",
                         font=ctk.CTkFont(family=FF, size=11),
                         text_color="#94A3B8", fg_color="transparent").pack(anchor="w", pady=(2, 0))

        # Pills de citas del día
        if citas_hoy:
            pills = ctk.CTkFrame(inner, fg_color="transparent")
            pills.pack(side="left", fill="x", expand=True, padx=(PAD["lg"], 0))

            for cita in citas_hoy[:6]:
                ci     = cita.paciente_id % len(CITA_PALETA)
                bg, fg = CITA_PALETA[ci]
                pill   = ctk.CTkFrame(pills, fg_color=bg, corner_radius=RADIUS["pill"])
                pill.pack(side="left", padx=(0, 6))
                nombre = cita.paciente_nombre.split()[0]
                ctk.CTkLabel(pill, text=f"  {cita.hora}  {nombre}  ",
                             font=ctk.CTkFont(family=FF, size=11, weight="bold"),
                             text_color=fg, fg_color="transparent").pack(padx=2, pady=5)

        # Botón nueva cita
        make_button(inner, "+  Nueva cita",
                    command=lambda: self._abrir_dialogo(fecha=hoy),
                    kind="primary", small=True).pack(side="right", anchor="center")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _abrir_dialogo(self, fecha=None, hora=None, cita=None, paciente_id=None):
        from .dialogo_cita import DialogoCita
        def _refresh():
            self._render_agenda_hoy()
            self._render()
        DialogoCita(
            self.winfo_toplevel(),
            cita=cita, fecha=fecha, hora=hora,
            paciente_id=paciente_id,
            on_guardar=_refresh,
        )

    def _descendants(self, widget):
        for child in widget.winfo_children():
            yield child
            yield from self._descendants(child)

    def on_show(self, paciente_id=None):
        self._hoy = date.today()
        self._render_agenda_hoy()
        if paciente_id:
            self._abrir_dialogo(paciente_id=paciente_id, fecha=self._hoy)
        self._render()
