"""
Genera el ícono de la app (diente estilizado) y lo convierte a .icns para macOS.
"""
import math
import subprocess
import shutil
from pathlib import Path
from PIL import Image, ImageDraw

SIZE = 512
OUT_DIR = Path("icon.iconset")
ICNS_PATH = Path("icon.icns")


def dibujar_icono(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size

    # Fondo redondeado azul
    BG = "#1A56DB"
    r = s * 0.22
    d.rounded_rectangle([0, 0, s, s], radius=r, fill=BG)

    # Diente — forma simplificada con polígono + arcos
    W = s * 0.72   # ancho total del diente
    pad_x = (s - W) / 2
    top_y = s * 0.14
    mid_y = s * 0.52
    bot_y = s * 0.86

    white = "#FFFFFF"
    # Cuerpo superior (corona)
    corona = [
        pad_x,              mid_y,          # izq base
        pad_x,              top_y + s*0.12, # izq sube
        pad_x + W*0.18,     top_y,          # hombro izq
        pad_x + W*0.38,     top_y + s*0.08, # valle centro
        pad_x + W*0.62,     top_y + s*0.08, # valle centro der
        pad_x + W*0.82,     top_y,          # hombro der
        pad_x + W,          top_y + s*0.12, # der sube
        pad_x + W,          mid_y,          # der base
    ]
    d.polygon(corona, fill=white)

    # Raíces (dos)
    raiz_w = W * 0.30
    gap    = W * 0.08
    raiz_l_x = pad_x + W * 0.10
    raiz_r_x = pad_x + W - W * 0.10 - raiz_w

    for rx in (raiz_l_x, raiz_r_x):
        d.rounded_rectangle(
            [rx, mid_y - s*0.02, rx + raiz_w, bot_y],
            radius=raiz_w / 2,
            fill=white,
        )

    # Sombra sutil interior en corona
    d.polygon(corona, outline="#D1E4FF", width=max(1, int(s * 0.008)))

    return img


def main():
    OUT_DIR.mkdir(exist_ok=True)

    sizes = [16, 32, 64, 128, 256, 512]
    for sz in sizes:
        img = dibujar_icono(sz)
        img.save(OUT_DIR / f"icon_{sz}x{sz}.png")
        # retina (@2x) — mismo archivo escalado al doble
        if sz <= 256:
            img2 = dibujar_icono(sz * 2)
            img2.save(OUT_DIR / f"icon_{sz}x{sz}@2x.png")

    # Renombrar al formato que espera iconutil
    mapping = {
        "icon_16x16.png":      "icon_16x16.png",
        "icon_32x32@2x.png":   "icon_16x16@2x.png",
        "icon_32x32.png":      "icon_32x32.png",
        "icon_64x64@2x.png":   "icon_32x32@2x.png",
        "icon_128x128.png":    "icon_128x128.png",
        "icon_256x256@2x.png": "icon_128x128@2x.png",
        "icon_256x256.png":    "icon_256x256.png",
        "icon_512x512@2x.png": "icon_256x256@2x.png",
        "icon_512x512.png":    "icon_512x512.png",
    }

    # Limpiar y recrear con nombres correctos
    for f in OUT_DIR.iterdir():
        f.unlink()

    sizes_needed = [16, 32, 128, 256, 512]
    for sz in sizes_needed:
        img   = dibujar_icono(sz)
        img2x = dibujar_icono(sz * 2)
        img.save(OUT_DIR / f"icon_{sz}x{sz}.png")
        img2x.save(OUT_DIR / f"icon_{sz}x{sz}@2x.png")

    result = subprocess.run(
        ["iconutil", "-c", "icns", str(OUT_DIR), "-o", str(ICNS_PATH)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print("Error iconutil:", result.stderr)
        return False

    shutil.rmtree(OUT_DIR)
    print(f"Ícono generado: {ICNS_PATH} ({ICNS_PATH.stat().st_size // 1024} KB)")
    return True


if __name__ == "__main__":
    main()
