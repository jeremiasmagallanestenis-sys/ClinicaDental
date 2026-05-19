"""Generate placeholder tooth icons for the PWA."""
import struct, zlib, os

def make_png(size, bg=(79, 70, 229), fg=(255, 255, 255)):
    """Create a minimal PNG with a colored square and a simple cross."""
    import struct, zlib

    w = h = size
    raw = []
    for y in range(h):
        row = [0]  # filter byte
        for x in range(w):
            # Draw a rounded-ish tooth shape (simple approach: filled square)
            # Slightly lighter border
            margin = size // 12
            in_inner = (margin <= x < w - margin) and (margin <= y < h - margin)
            # Simple tooth symbol: cross in center
            center = size // 2
            thick = max(2, size // 20)
            on_h = (center - thick <= y <= center + thick) and (margin*2 <= x <= w - margin*2)
            on_v = (center - thick <= x <= center + thick) and (margin*2 <= y <= h - margin*2)
            if on_h or on_v:
                row += list(fg) + [255]
            elif in_inner:
                row += list(bg) + [255]
            else:
                # Darker border
                row += [max(0, c - 30) for c in bg] + [255]
        raw.append(bytes(row))

    def png_chunk(tag, data):
        chunk = tag + data
        return struct.pack('>I', len(data)) + chunk + struct.pack('>I', zlib.crc32(chunk) & 0xFFFFFFFF)

    signature = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)  # 8-bit RGB
    # Actually use RGBA (color type 6)
    ihdr_data = struct.pack('>II', w, h) + bytes([8, 6, 0, 0, 0])

    raw_bytes = b''.join(raw)
    compressed = zlib.compress(raw_bytes, 9)

    png = (
        signature
        + png_chunk(b'IHDR', ihdr_data)
        + png_chunk(b'IDAT', compressed)
        + png_chunk(b'IEND', b'')
    )
    return png

def save(path, size):
    data = make_png(size)
    with open(path, 'wb') as f:
        f.write(data)
    print(f"Saved {path} ({size}x{size})")

out_dir = os.path.join(os.path.dirname(__file__), 'static', 'icons')
os.makedirs(out_dir, exist_ok=True)

try:
    from PIL import Image, ImageDraw, ImageFont

    def make_icon_pil(size, path):
        img = Image.new('RGBA', (size, size), (79, 70, 229, 255))
        draw = ImageDraw.Draw(img)
        m = size // 8
        # White rounded tooth outline
        tooth_pts = [
            (size*0.3, size*0.2), (size*0.7, size*0.2),
            (size*0.8, size*0.4), (size*0.75, size*0.7),
            (size*0.65, size*0.85), (size*0.55, size*0.75),
            (size*0.5, size*0.75), (size*0.45, size*0.75),
            (size*0.35, size*0.85), (size*0.25, size*0.7),
            (size*0.2, size*0.4),
        ]
        draw.polygon(tooth_pts, fill=(255, 255, 255, 230))
        img.save(path, 'PNG')
        print(f"Saved {path} ({size}x{size}) [PIL]")

    make_icon_pil(192, os.path.join(out_dir, 'icon-192.png'))
    make_icon_pil(512, os.path.join(out_dir, 'icon-512.png'))

except ImportError:
    # Fallback: minimal PNG
    save(os.path.join(out_dir, 'icon-192.png'), 192)
    save(os.path.join(out_dir, 'icon-512.png'), 512)
