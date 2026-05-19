"""
Widget de odontograma dibujado con Canvas.
Numeración FDI estándar (11-18, 21-28, 31-38, 41-48).
Clic izquierdo: avanza al siguiente estado.
Clic derecho: retrocede / muestra menú.
"""
import tkinter as tk
from tkinter import ttk
from .styles import COLORS, FONTS

# ── Estados y colores ────────────────────────────────────────────────────────
ESTADOS = ["normal", "caries", "extraccion", "corona", "tratado", "fractura", "ausente"]

ESTADO_COLOR = {
    "normal":    "#FFFFFF",
    "caries":    "#FF6B6B",
    "extraccion":"#9E9E9E",
    "corona":    "#64B5F6",
    "tratado":   "#81C784",
    "fractura":  "#FFB74D",
    "ausente":   "#E0E0E0",
}
ESTADO_LABEL = {
    "normal":    "Sano",
    "caries":    "Caries",
    "extraccion":"Extracción",
    "corona":    "Corona",
    "tratado":   "Tratado",
    "fractura":  "Fractura",
    "ausente":   "Ausente",
}
ESTADO_SYMBOL = {
    "extraccion": "✕",
    "corona":     "C",
    "fractura":   "/",
    "ausente":    "—",
}

# Filas de dientes (izq → der en la boca del paciente)
DIENTES_SUPERIOR = [18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28]
DIENTES_INFERIOR = [48, 47, 46, 45, 44, 43, 42, 41, 31, 32, 33, 34, 35, 36, 37, 38]

TW, TH = 26, 32   # tamaño de cada diente (px)
GAP     = 3        # separación entre dientes
MIDGAP  = 10       # separación en la línea media
VJAW    = 14       # separación vertical entre mandíbulas


class OdontogramaWidget:
    """
    Clase pura (no hereda de widget tk) que construye y gestiona el canvas.
    Usá .frame para empaquetarlo con pack/grid.
    """
    def __init__(self, parent, datos: dict = None, bg=None):
        self._estado: dict[int, str] = {}  # {numero: estado}
        self._bg = bg or COLORS["bg"]
        self._on_change = None

        if datos:
            self._estado = {int(k): v for k, v in datos.items()}

        # Canvas width: 16 dientes * TW + 15 gaps + 1 midgap
        total_w = 16 * TW + 15 * GAP + MIDGAP + 4
        # Canvas height: 2 filas + números arriba/abajo + separación
        total_h = 2 * (TH + 16) + VJAW + 8

        self.frame = tk.Frame(parent, bg=self._bg)
        self._cv = tk.Canvas(self.frame, width=total_w, height=total_h,
                              bg=self._bg, highlightthickness=0)
        self._cv.pack()

        self._build_leyenda()
        self._draw_all()

        self._cv.bind("<Button-1>",   self._on_click_left)
        self._cv.bind("<Button-2>",   self._on_click_right)
        self._cv.bind("<Button-3>",   self._on_click_right)

    # ── Coordenadas ──────────────────────────────────────────────────────────

    def _x_for(self, idx: int) -> int:
        """Coordenada x del borde izquierdo del diente en posición idx (0-15)."""
        extra_mid = MIDGAP if idx >= 8 else 0
        return 2 + idx * (TW + GAP) + extra_mid

    def _coords_superior(self, idx):
        x = self._x_for(idx)
        y = 18                        # deja espacio para número
        return x, y, x + TW, y + TH

    def _coords_inferior(self, idx):
        x = self._x_for(idx)
        y = 18 + TH + VJAW
        return x, y, x + TW, y + TH

    def _numero_superior(self, idx):
        return DIENTES_SUPERIOR[idx]

    def _numero_inferior(self, idx):
        return DIENTES_INFERIOR[idx]

    # ── Dibujo ────────────────────────────────────────────────────────────────

    def _draw_all(self):
        self._cv.delete("diente")
        for i in range(16):
            self._draw_diente(i, superior=True)
            self._draw_diente(i, superior=False)

    def _draw_diente(self, idx: int, superior: bool):
        if superior:
            x1, y1, x2, y2 = self._coords_superior(idx)
            num = self._numero_superior(idx)
            num_y = y1 - 4              # número encima
        else:
            x1, y1, x2, y2 = self._coords_inferior(idx)
            num = self._numero_inferior(idx)
            num_y = y2 + 12             # número debajo

        estado = self._estado.get(num, "normal")
        fill   = ESTADO_COLOR[estado]
        symbol = ESTADO_SYMBOL.get(estado, "")

        tag = f"d{num}"
        self._cv.delete(tag)

        self._cv.create_rectangle(x1, y1, x2, y2,
                                   fill=fill, outline="#9E9E9E", width=1,
                                   tags=("diente", tag))

        if symbol:
            self._cv.create_text((x1+x2)//2, (y1+y2)//2, text=symbol,
                                  font=(FONTS["tiny"][0], 9, "bold"),
                                  fill="#333333", tags=("diente", tag))

        # Número del diente
        self._cv.create_text((x1+x2)//2, num_y, text=str(num),
                              font=(FONTS["tiny"][0], 8),
                              fill=COLORS["text_muted"], tags=("diente", tag))

    # ── Interacción ───────────────────────────────────────────────────────────

    def _diente_en(self, event) -> int | None:
        """Devuelve el número de diente bajo el cursor, o None."""
        for i in range(16):
            for superior, coords_fn, num_fn in [
                (True,  self._coords_superior, self._numero_superior),
                (False, self._coords_inferior, self._numero_inferior),
            ]:
                x1, y1, x2, y2 = coords_fn(i)
                if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                    return num_fn(i)
        return None

    def _on_click_left(self, event):
        num = self._diente_en(event)
        if num is None:
            return
        actual = self._estado.get(num, "normal")
        idx_actual = ESTADOS.index(actual)
        nuevo = ESTADOS[(idx_actual + 1) % len(ESTADOS)]
        self._set_estado(num, nuevo)

    def _on_click_right(self, event):
        num = self._diente_en(event)
        if num is None:
            return
        menu = tk.Menu(self._cv, tearoff=0)
        for est in ESTADOS:
            menu.add_command(
                label=f"  {ESTADO_LABEL[est]}",
                command=lambda e=est, n=num: self._set_estado(n, e),
            )
        menu.tk_popup(event.x_root, event.y_root)

    def _set_estado(self, num: int, estado: str):
        if estado == "normal":
            self._estado.pop(num, None)
        else:
            self._estado[num] = estado

        # Redibujar solo el diente afectado
        if num in DIENTES_SUPERIOR:
            idx = DIENTES_SUPERIOR.index(num)
            self._draw_diente(idx, superior=True)
        else:
            idx = DIENTES_INFERIOR.index(num)
            self._draw_diente(idx, superior=False)

        if self._on_change:
            self._on_change()

    # ── API pública ───────────────────────────────────────────────────────────

    def get_datos(self) -> dict:
        return {str(k): v for k, v in self._estado.items()}

    def set_datos(self, datos: dict):
        self._estado = {int(k): v for k, v in datos.items()}
        self._draw_all()

    def set_on_change(self, fn):
        self._on_change = fn

    # ── Leyenda ───────────────────────────────────────────────────────────────

    def _build_leyenda(self):
        ley = tk.Frame(self.frame, bg=self._bg)
        ley.pack(anchor="w", pady=(0, 4))
        tk.Label(ley, text="Clic izquierdo: cambiar estado  ·  Clic derecho: elegir estado",
                 font=(FONTS["tiny"][0], 9), fg=COLORS["text_muted"], bg=self._bg).pack(side="left")

        row = tk.Frame(self.frame, bg=self._bg)
        row.pack(anchor="w", pady=(0, 6))
        for est in ESTADOS:
            chip = tk.Frame(row, bg=ESTADO_COLOR[est],
                            highlightbackground="#9E9E9E", highlightthickness=1)
            chip.pack(side="left", padx=3)
            tk.Label(chip, text=f" {ESTADO_LABEL[est]} ",
                     font=(FONTS["tiny"][0], 9),
                     bg=ESTADO_COLOR[est], fg="#333").pack()
