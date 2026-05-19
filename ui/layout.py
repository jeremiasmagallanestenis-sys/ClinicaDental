"""Sidebar lateral — diseño SaaS premium."""
import tkinter as tk
import customtkinter as ctk
from .styles import COLORS, FONTS, SIDEBAR_W, RADIUS

C  = COLORS
FF = FONTS["body"][0]


def _draw_sidebar_tooth(cv, cx, cy):
    s   = 0.82
    raw = [
        -18, 10, -16, -2, -12, -12, -6, -6,
        0, -16, 6, -6, 12, -12, 16, -2, 18, 10,
        14, 18, 10, 30, 4, 18, 0, 16, -4, 18, -10, 30, -14, 18,
    ]
    pts = []
    for i in range(0, len(raw), 2):
        pts.append(cx + raw[i] * s)
        pts.append(cy + raw[i + 1] * s)
    cv.create_polygon(pts, fill="#EEF2FF", outline="#818CF8",
                      width=1.5, smooth=True)


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, nav, on_backup):
        super().__init__(parent, fg_color=C["sidebar"],
                         width=SIDEBAR_W, corner_radius=0)
        self.pack_propagate(False)
        self._nav       = nav
        self._on_backup = on_backup
        self._btns      = {}
        self._build()

    def _build(self):
        # ── Logo / Brand ──────────────────────────────────────────
        brand_wrap = ctk.CTkFrame(self, fg_color="transparent")
        brand_wrap.pack(fill="x", padx=20, pady=(28, 0))

        cv = tk.Canvas(brand_wrap, width=36, height=42,
                       bg=C["sidebar"], highlightthickness=0)
        cv.pack(side="left")
        _draw_sidebar_tooth(cv, 18, 21)

        brand_text = ctk.CTkFrame(brand_wrap, fg_color="transparent")
        brand_text.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(brand_text, text="Historial",
                     font=ctk.CTkFont(family=FF, size=15, weight="bold"),
                     text_color="#FFFFFF",
                     fg_color="transparent").pack(anchor="w")
        ctk.CTkLabel(brand_text, text="Clínico Dental",
                     font=ctk.CTkFont(family=FF, size=10),
                     text_color="#4B6080",
                     fg_color="transparent").pack(anchor="w")

        # Divisor
        ctk.CTkFrame(self, height=1, fg_color="#162236",
                     corner_radius=0).pack(fill="x", padx=18, pady=(24, 18))

        # ── Sección PRINCIPAL ─────────────────────────────────────
        self._section_label("PRINCIPAL")

        pac = ctk.CTkButton(
            self,
            text="  👥  Pacientes",
            command=lambda: self._nav("principal", None),
            anchor="w",
            font=ctk.CTkFont(family=FF, size=13),
            height=40,
            corner_radius=RADIUS["btn"],
            fg_color="transparent",
            hover_color=C["sidebar_hover"],
            text_color=C["text_sidebar"],
            cursor="hand2",
        )
        pac.pack(fill="x", padx=12, pady=(2, 2))
        self._btns["principal"] = pac

        cal = ctk.CTkButton(
            self,
            text="  📅  Calendario",
            command=lambda: self._nav("calendario", None),
            anchor="w",
            font=ctk.CTkFont(family=FF, size=13),
            height=40,
            corner_radius=RADIUS["btn"],
            fg_color="transparent",
            hover_color=C["sidebar_hover"],
            text_color=C["text_sidebar"],
            cursor="hand2",
        )
        cal.pack(fill="x", padx=12, pady=(0, 2))
        self._btns["calendario"] = cal

        # ── Sección SISTEMA ───────────────────────────────────────
        ctk.CTkFrame(self, height=1, fg_color="#162236",
                     corner_radius=0).pack(fill="x", padx=18, pady=(14, 14))

        self._section_label("SISTEMA")

        cfg = ctk.CTkButton(
            self,
            text="  ⚙  Configuración",
            command=lambda: self._nav("config", None),
            anchor="w",
            font=ctk.CTkFont(family=FF, size=13),
            height=40,
            corner_radius=RADIUS["btn"],
            fg_color="transparent",
            hover_color=C["sidebar_hover"],
            text_color=C["text_sidebar"],
            cursor="hand2",
        )
        cfg.pack(fill="x", padx=12, pady=(2, 2))
        self._btns["config"] = cfg

        bkp = ctk.CTkButton(
            self,
            text="  ⬆  Copia de seguridad",
            command=self._on_backup,
            anchor="w",
            font=ctk.CTkFont(family=FF, size=13),
            height=40,
            corner_radius=RADIUS["btn"],
            fg_color="transparent",
            hover_color=C["sidebar_hover"],
            text_color=C["text_sidebar"],
            cursor="hand2",
        )
        bkp.pack(fill="x", padx=12, pady=(0, 2))

        # ── Pie ───────────────────────────────────────────────────
        foot = ctk.CTkFrame(self, fg_color="transparent")
        foot.pack(side="bottom", fill="x", padx=18, pady=18)

        ctk.CTkFrame(foot, height=1, fg_color="#162236",
                     corner_radius=0).pack(fill="x", pady=(0, 14))

        status = ctk.CTkFrame(foot, fg_color="transparent")
        status.pack(fill="x")

        dot = tk.Canvas(status, width=8, height=8,
                        bg=C["sidebar"], highlightthickness=0)
        dot.pack(side="left", pady=4)
        dot.create_oval(1, 1, 7, 7, fill=C["success"], outline="")

        ctk.CTkLabel(status, text="  Sistema activo",
                     font=ctk.CTkFont(family=FF, size=10),
                     text_color="#3D5A7A",
                     fg_color="transparent").pack(side="left")

    def _section_label(self, text):
        ctk.CTkLabel(self, text=text,
                     font=ctk.CTkFont(family=FF, size=9, weight="bold"),
                     text_color="#2D4A66",
                     fg_color="transparent").pack(anchor="w", padx=20, pady=(0, 6))

    def set_active(self, screen: str):
        for name, btn in self._btns.items():
            if name == screen:
                btn.configure(fg_color=C["sidebar_active"], text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent", text_color=C["text_sidebar"])
