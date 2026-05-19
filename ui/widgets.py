"""
Componentes UI reutilizables — CustomTkinter + sombras reales.
"""
import tkinter as tk
import customtkinter as ctk
from .styles import COLORS, FONTS, PAD, RADIUS

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

C  = COLORS
FF = FONTS["body"][0]


# ── Helpers de fuente ─────────────────────────────────────────────────────────

def _font(key):
    t = FONTS[key]
    w = t[2] if len(t) > 2 else "normal"
    return ctk.CTkFont(family=t[0], size=t[1], weight=w)


# ── Tarjetas con sombra ───────────────────────────────────────────────────────

def make_card(parent, pad_x=None, pad_y=None, accent=None, **kwargs):
    px = pad_x if pad_x is not None else PAD["sm"]
    py = pad_y if pad_y is not None else PAD["sm"]

    shadow = ctk.CTkFrame(
        parent,
        fg_color=C["shadow_soft"],
        corner_radius=RADIUS["card"] + 2,
        **kwargs,
    )

    card = ctk.CTkFrame(
        shadow,
        fg_color=C["surface"],
        corner_radius=RADIUS["card"],
        border_width=1,
        border_color=C["border"],
    )
    card.pack(fill="both", expand=True, padx=1, pady=(1, 3))

    if accent:
        ctk.CTkFrame(card, height=3, fg_color=accent,
                     corner_radius=0).pack(fill="x")

    inner = ctk.CTkFrame(card, fg_color="transparent")
    inner.pack(fill="both", expand=True, padx=px, pady=py)

    return shadow, inner


def make_card_flat(parent, pad_x=None, pad_y=None, **kwargs):
    """Tarjeta sin sombra, con borde — para secciones secundarias."""
    px = pad_x if pad_x is not None else PAD["sm"]
    py = pad_y if pad_y is not None else PAD["sm"]

    card = ctk.CTkFrame(
        parent,
        fg_color=C["surface"],
        corner_radius=RADIUS["inner"],
        border_width=1,
        border_color=C["border"],
        **kwargs,
    )
    inner = ctk.CTkFrame(card, fg_color="transparent")
    inner.pack(fill="both", expand=True, padx=px, pady=py)
    return card, inner


# ── Botones ───────────────────────────────────────────────────────────────────

_BTN_STYLES = {
    "primary": dict(
        fg_color=C["primary"], hover_color=C["primary_hover"],
        text_color="white",
    ),
    "ghost": dict(
        fg_color="transparent", hover_color=C["primary_light"],
        text_color=C["primary"], border_width=0,
    ),
    "secondary": dict(
        fg_color=C["surface_2"], hover_color=C["border"],
        text_color=C["text_secondary"],
        border_width=1, border_color=C["border"],
    ),
    "danger": dict(
        fg_color=C["danger"], hover_color=C["danger_hover"],
        text_color="white",
    ),
    "danger_ghost": dict(
        fg_color="transparent", hover_color=C["danger_bg"],
        text_color=C["danger"], border_width=0,
    ),
    "success": dict(
        fg_color=C["success"], hover_color=C["success_hover"],
        text_color="white",
    ),
    "sidebar": dict(
        fg_color="transparent", hover_color=C["sidebar_hover"],
        text_color=C["text_sidebar"], border_width=0,
    ),
}


def make_button(parent, text, command, kind="primary", small=False, **kwargs):
    h = 32 if small else 40
    f = _font("body_sm") if small else _font("label")
    cfg = dict(_BTN_STYLES.get(kind, _BTN_STYLES["primary"]))
    return ctk.CTkButton(
        parent, text=text, command=command,
        font=f, height=h,
        corner_radius=RADIUS["btn"],
        cursor="hand2",
        **cfg,
        **kwargs,
    )


# ── Inputs ────────────────────────────────────────────────────────────────────

def make_entry(parent, textvariable=None, width=32, placeholder=None, **kwargs):
    e = ctk.CTkEntry(
        parent,
        textvariable=textvariable,
        placeholder_text=placeholder or "",
        fg_color=C["input_bg"],
        border_color=C["input_border"],
        border_width=1,
        corner_radius=RADIUS["inner"],
        height=44,
        text_color=C["text"],
        placeholder_text_color=C["text_faint"],
        font=_font("body"),
        **kwargs,
    )
    return e, e


def make_text(parent, height=4, width=40, **kwargs):
    tb = ctk.CTkTextbox(
        parent,
        height=max(70, height * 28),
        fg_color=C["input_bg"],
        border_color=C["input_border"],
        border_width=1,
        corner_radius=RADIUS["inner"],
        text_color=C["text"],
        font=_font("body"),
        wrap="word",
        **kwargs,
    )
    return tb, tb


# ── Separador ─────────────────────────────────────────────────────────────────

def make_separator(parent, color=None, **kwargs):
    return ctk.CTkFrame(
        parent, height=1,
        fg_color=color or C["border"],
        **kwargs,
    )


# ── Avatar con iniciales y color dinámico ─────────────────────────────────────

def make_avatar(parent, nombre: str, size=44, bg_parent=None):
    iniciales = _iniciales(nombre)
    bg_parent_color = bg_parent or C["surface"]

    # Color basado en primera letra
    av_colors = [C[f"av_{i}"] for i in range(8)]
    idx = ord(iniciales[0]) % len(av_colors)
    av_bg = av_colors[idx]

    c = tk.Canvas(parent, width=size, height=size,
                  bg=bg_parent_color, highlightthickness=0)
    r = size // 2
    # Círculo principal
    c.create_oval(2, 2, size - 2, size - 2, fill=av_bg, outline="")
    # Iniciales
    font_size = max(9, size // 3)
    c.create_text(r, r, text=iniciales,
                  font=(FF, font_size, "bold"),
                  fill="#FFFFFF")
    return c


def _iniciales(nombre: str) -> str:
    partes = nombre.strip().split()
    if not partes:
        return "?"
    if len(partes) == 1:
        return partes[0][0].upper()
    return (partes[0][0] + partes[-1][0]).upper()


# ── Tag / Badge / Chip ────────────────────────────────────────────────────────

def make_tag(parent, text, bg, fg, bg_parent=None, bold=False):
    outer = ctk.CTkFrame(parent, fg_color="transparent")
    pill  = ctk.CTkFrame(outer, fg_color=bg, corner_radius=RADIUS["pill"])
    pill.pack()
    ctk.CTkLabel(
        pill, text=text,
        font=_font("caption_bold") if bold else _font("caption"),
        text_color=fg, fg_color="transparent",
    ).pack(padx=10, pady=3)
    return outer


def make_status_dot(parent, color, bg_parent=None):
    """Punto de estado coloreado."""
    bg = bg_parent or C["surface"]
    c = tk.Canvas(parent, width=8, height=8, bg=bg, highlightthickness=0)
    c.create_oval(1, 1, 7, 7, fill=color, outline="")
    return c


# ── Scroll ────────────────────────────────────────────────────────────────────

def scrollable_frame(parent, bg=None):
    bg = bg or C["bg"]
    sf = ctk.CTkScrollableFrame(
        parent, fg_color=bg,
        scrollbar_button_color=C["border_strong"],
        scrollbar_button_hover_color=C["text_muted"],
    )
    sf.pack(fill="both", expand=True)
    _enable_trackpad_scroll(sf)
    return sf, sf


def _enable_trackpad_scroll(sf):
    """Fix CTkScrollableFrame trackpad scroll on macOS.

    CTk's built-in handler breaks because:
    1. check_if_master_is_canvas fails for CTk internal widgets
    2. yview()==(0,1) guard fires when scrollregion is stale

    Fix: position-based check against the visible parent frame + forced
    scrollregion refresh on every Configure.
    """
    import platform
    canvas = sf._parent_canvas
    is_mac = platform.system() == "Darwin"

    # Keep scrollregion in sync after every layout change
    def _refresh(_=None):
        sf.after_idle(lambda: canvas.configure(scrollregion=canvas.bbox("all")))
    sf.bind("<Configure>", _refresh, add="+")

    # Position-based scroll: works regardless of which child widget
    # is under the mouse — avoids the broken hierarchy check entirely
    def _scroll(event):
        try:
            pf = sf._parent_frame
            if not pf.winfo_ismapped():
                return
            x, y = event.x_root, event.y_root
            px, py = pf.winfo_rootx(), pf.winfo_rooty()
            pw, ph = pf.winfo_width(), pf.winfo_height()
            if px <= x <= px + pw and py <= y <= py + ph:
                if is_mac:
                    canvas.yview_scroll(int(-event.delta), "units")
                else:
                    canvas.yview_scroll(-1 if event.num == 4 else 1, "units")
        except Exception:
            pass

    sf.bind_all("<MouseWheel>", _scroll, add="+")
    if not is_mac:
        sf.bind_all("<Button-4>", _scroll, add="+")
        sf.bind_all("<Button-5>", _scroll, add="+")


# ── Sección con encabezado ────────────────────────────────────────────────────

def make_section_header(parent, title, subtitle=None, bg=None):
    bg = bg or C["bg"]
    wrap = ctk.CTkFrame(parent, fg_color="transparent")

    row = ctk.CTkFrame(wrap, fg_color="transparent")
    row.pack(fill="x")

    ctk.CTkLabel(row, text=title, font=_font("label"),
                 text_color=C["text_muted"],
                 fg_color="transparent").pack(side="left")

    if subtitle:
        ctk.CTkLabel(row, text=subtitle, font=_font("caption"),
                     text_color=C["text_faint"],
                     fg_color="transparent").pack(side="left", padx=(8, 0))

    return wrap


# ── Estado vacío ──────────────────────────────────────────────────────────────

def empty_state(parent, title, subtitle="", bg=None, icon="🦷"):
    bg = bg or C["bg"]
    frame = ctk.CTkFrame(parent, fg_color=bg)

    # Ícono en círculo suave
    icon_wrap = ctk.CTkFrame(frame, fg_color=C["primary_light"],
                              corner_radius=40, width=80, height=80)
    icon_wrap.pack(pady=(40, 0))
    icon_wrap.pack_propagate(False)
    ctk.CTkLabel(icon_wrap, text=icon,
                 font=ctk.CTkFont(family=FF, size=32),
                 fg_color="transparent").pack(expand=True)

    ctk.CTkLabel(frame, text=title, font=_font("subheading"),
                 text_color=C["text_secondary"],
                 fg_color="transparent").pack(pady=(16, 0))
    if subtitle:
        ctk.CTkLabel(frame, text=subtitle, font=_font("body"),
                     text_color=C["text_muted"],
                     fg_color="transparent",
                     wraplength=340, justify="center").pack(pady=(6, 40))
    return frame


# ── Toast animado ─────────────────────────────────────────────────────────────

class Toast:
    _SHOW_MS    = 2600
    _ANIM_MS    = 240
    _ANIM_STEPS = 16

    def __init__(self, root, message: str, kind: str = "success"):
        self._root = root
        self._win  = tk.Toplevel(root)
        self._win.overrideredirect(True)
        self._win.attributes("-topmost", True)

        _palette = {
            "success": (C["success_bg"],   C["success_text"], C["success"],  "✓"),
            "error":   (C["danger_bg"],    C["danger"],       C["danger"],   "✕"),
            "info":    (C["primary_light"], C["primary"],     C["primary"],  "ℹ"),
        }
        bg, fg, accent, icon = _palette.get(kind, _palette["success"])

        # Estructura visual
        outer_frame = tk.Frame(self._win, bg=C["shadow_color"], padx=1, pady=1)
        outer_frame.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 4))

        accent_frame = tk.Frame(outer_frame, bg=accent, padx=2, pady=0)
        accent_frame.pack(fill="both", expand=True)

        inner = tk.Frame(accent_frame, bg=bg, padx=20, pady=14)
        inner.pack(fill="both", expand=True, pady=(0, 0))

        # Icono + mensaje en la misma línea
        msg_row = tk.Frame(inner, bg=bg)
        msg_row.pack()

        icon_lbl = tk.Frame(msg_row, bg=accent, width=24, height=24)
        icon_lbl.pack(side="left", padx=(0, 10))
        icon_lbl.pack_propagate(False)
        tk.Label(icon_lbl, text=icon, font=(FF, 11, "bold"),
                 fg="white", bg=accent).place(relx=.5, rely=.5, anchor="center")

        tk.Label(msg_row, text=message, font=(FF, 13),
                 fg=fg, bg=bg).pack(side="left")

        # Barra de progreso
        bar_bg = tk.Frame(accent_frame, bg=accent, height=3)
        bar_bg.pack(fill="x", side="bottom")
        self._bar = tk.Frame(bar_bg, bg=accent, height=3)
        self._bar.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._win.update_idletasks()
        self._tx, self._ty = self._calc_pos()
        self._animate_in()

    def _calc_pos(self):
        rw = self._root.winfo_width()
        rx = self._root.winfo_x()
        ry = self._root.winfo_y()
        w  = self._win.winfo_width()
        return rx + (rw - w) // 2, ry + 32

    def _animate_in(self):
        tx, ty  = self._tx, self._ty
        start_y = ty - 52
        steps   = self._ANIM_STEPS
        iv      = max(1, self._ANIM_MS // steps)

        def step(i):
            t = 1 - (1 - i / steps) ** 3
            try:
                self._win.geometry(f"+{tx}+{int(start_y + (ty - start_y) * t)}")
            except Exception:
                return
            if i < steps:
                self._win.after(iv, lambda: step(i + 1))
            else:
                self._progress()

        self._win.geometry(f"+{tx}+{start_y}")
        step(1)

    def _progress(self):
        steps = 60
        iv    = self._SHOW_MS // steps

        def step(i):
            try:
                self._bar.place(relx=0, rely=0,
                                relwidth=max(0.0, 1.0 - i / steps),
                                relheight=1)
            except Exception:
                return
            if i < steps:
                self._win.after(iv, lambda: step(i + 1))
            else:
                self._animate_out()

        step(0)

    def _animate_out(self):
        tx, ty = self._tx, self._ty
        end_y  = ty - 52
        steps  = self._ANIM_STEPS
        iv     = max(1, self._ANIM_MS // steps)

        def step(i):
            t = (i / steps) ** 2
            try:
                self._win.geometry(f"+{tx}+{int(ty + (end_y - ty) * t)}")
            except Exception:
                return
            if i < steps:
                self._win.after(iv, lambda: step(i + 1))
            else:
                try:
                    self._win.destroy()
                except Exception:
                    pass

        step(1)


# ── CTA Button (acción principal) ─────────────────────────────────────────────

class CTAButton:
    def __init__(self, parent, text, command, bg_parent=None):
        self._btn = ctk.CTkButton(
            parent, text=text, command=command,
            fg_color=C["primary"], hover_color=C["primary_hover"],
            text_color="white", font=_font("label"),
            corner_radius=RADIUS["btn"], height=40, cursor="hand2",
        )

    def pack(self, **kw):  self._btn.pack(**kw)
    def grid(self, **kw):  self._btn.grid(**kw)
    def place(self, **kw): self._btn.place(**kw)


# ── SaveButton con estados feedback ──────────────────────────────────────────

class SaveButton:
    _SUCCESS_MS = 1400

    def __init__(self, parent, text: str, command, kind: str = "primary"):
        self._original_text = text
        self._real_command  = command
        self._busy          = False
        cfg = dict(_BTN_STYLES.get(kind, _BTN_STYLES["primary"]))
        self._fg_normal = cfg["fg_color"]

        self._btn = ctk.CTkButton(
            parent, text=text, command=self._on_click,
            font=_font("label"), height=38,
            corner_radius=RADIUS["btn"], cursor="hand2",
            **cfg,
        )

    def pack(self, **kw):  self._btn.pack(**kw)
    def grid(self, **kw):  self._btn.grid(**kw)
    def place(self, **kw): self._btn.place(**kw)

    def _on_click(self):
        if self._busy:
            return
        self._busy = True
        self._btn.configure(text="Guardando…",
                            fg_color=C["primary_hover"],
                            state="disabled", cursor="watch")
        self._btn.after(60, self._run)

    def _run(self):
        try:
            self._real_command()
        finally:
            self._show_ok()

    def _show_ok(self):
        try:
            self._btn.configure(text="✓ Guardado",
                                fg_color=C["success"],
                                text_color="white",
                                state="normal", cursor="hand2")
            self._btn.after(self._SUCCESS_MS, self._revert)
        except Exception:
            self._revert()

    def _revert(self):
        try:
            self._btn.configure(text=self._original_text,
                                fg_color=self._fg_normal)
        except Exception:
            pass
        self._busy = False


# ── Checkbox estilizado ───────────────────────────────────────────────────────

def make_checkbox(parent, text, variable, bg=None):
    return ctk.CTkCheckBox(
        parent, text=text, variable=variable,
        font=_font("body"), text_color=C["text"],
        fg_color=C["primary"], hover_color=C["primary_hover"],
        checkmark_color="white", corner_radius=5,
        border_color=C["border_strong"],
    )
