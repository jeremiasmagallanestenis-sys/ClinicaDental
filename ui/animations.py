import tkinter as tk
from .styles import COLORS


# ── Easing ────────────────────────────────────────────────────────────────────

def _ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


def _ease_in_out(t: float) -> float:
    return t * t * (3 - 2 * t)


# ── Slide transition entre pantallas ─────────────────────────────────────────

def slide_screens(old_frame, new_frame, duration_ms: int = 210, steps: int = 14, on_done=None):
    interval = max(1, duration_ms // steps)

    # Posicionar nueva pantalla fuera de vista (derecha)
    new_frame.place(relx=1.0, rely=0, relwidth=1, relheight=1)
    new_frame.lift()

    def step(i: int):
        if i > steps:
            # Limpiar: dejar todo en posición final
            new_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            if old_frame is not None:
                old_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
                old_frame.lower()
            if on_done:
                on_done()
            return

        t = _ease_out_cubic(i / steps)
        new_frame.place(relx=1.0 - t, rely=0, relwidth=1, relheight=1)
        if old_frame is not None:
            old_frame.place(relx=-0.28 * t, rely=0, relwidth=1, relheight=1)

        new_frame.after(interval, lambda: step(i + 1))

    step(1)


# ── Spinner rotativo ──────────────────────────────────────────────────────────

class Spinner(tk.Canvas):
    _TRACK   = "#E2E8F0"
    _TICK_MS = 35

    def __init__(self, parent, size: int = 28, color: str = None, bg: str = None, **kwargs):
        _bg    = bg    or COLORS["bg"]
        _color = color or COLORS["primary"]
        super().__init__(parent, width=size, height=size,
                         bg=_bg, highlightthickness=0, **kwargs)
        self._size  = size
        self._color = _color
        self._angle = 0
        self._job   = None

    def start(self):
        if self._job is None:
            self._tick()

    def stop(self):
        if self._job:
            self.after_cancel(self._job)
            self._job = None
        self.delete("all")

    def _tick(self):
        self._draw()
        self._angle = (self._angle + 10) % 360
        self._job = self.after(self._TICK_MS, self._tick)

    def _draw(self):
        self.delete("all")
        s   = self._size
        pad = max(3, s * 0.14)
        w   = max(2, s // 9)
        # Pista (gris claro)
        self.create_arc(pad, pad, s - pad, s - pad,
                        start=0, extent=359,
                        outline=self._TRACK, width=w, style="arc")
        # Arco animado
        self.create_arc(pad, pad, s - pad, s - pad,
                        start=self._angle, extent=260,
                        outline=self._color, width=w, style="arc")


# ── Fade de un solo widget (opacidad simulada via color blend) ────────────────
# Nota: Tkinter no soporta transparencia en frames, pero podemos animar
# el color de fondo de labels y frames entre dos colores.

def _blend_hex(c1: str, c2: str, t: float) -> str:
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def fade_in_widget(widget, from_color: str, to_color: str,
                   duration_ms: int = 180, steps: int = 10):
    interval = max(1, duration_ms // steps)

    def step(i: int):
        if i > steps:
            try:
                widget.config(bg=to_color)
            except Exception:
                pass
            return
        t = _ease_out_cubic(i / steps)
        try:
            widget.config(bg=_blend_hex(from_color, to_color, t))
        except Exception:
            pass
        widget.after(interval, lambda: step(i + 1))

    step(1)


# ── Animación de aparición de fila (slide-down + fade desde arriba) ───────────

def animate_row_in(widget, delay_ms: int = 0, distance: int = 12,
                   duration_ms: int = 160, steps: int = 8):
    interval = max(1, duration_ms // steps)

    def run():
        def step(i: int):
            if i > steps:
                widget.place_forget() if False else None
                return
            t = _ease_out_cubic(i / steps)
            # Simulamos el efecto moviendo el pady inicial
            # En Tkinter no hay transform, así que usamos pack pady decreciente
            offset = int(distance * (1 - t))
            try:
                widget.pack_configure(pady=(offset, 3))
            except Exception:
                pass
            widget.after(interval, lambda: step(i + 1))

        step(1)

    if delay_ms > 0:
        widget.after(delay_ms, run)
    else:
        run()
