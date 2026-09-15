"""Genera el icono propio de REPTOSX (REPTOSX.ico) y una vista previa PNG.

Diseno: cuadrado redondeado con degradado azul (acento de la app), una 'R'
blanca en negrita y un pequeno interruptor verde (la app va de activar ajustes).

Ejecutar:  python generate_icon.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

S = 512                      # lienzo de alta resolucion (luego se reduce)
RADIUS = int(S * 0.22)       # esquinas redondeadas
TOP = (59, 130, 246)         # #3b82f6
BOTTOM = (29, 78, 216)       # #1d4ed8
GREEN = (34, 197, 94)        # #22c55e


def _load_font(size):
    # Arial Black: gruesa y redonda, con presencia de icono de app
    for name in ("ariblk.ttf", "seguibl.ttf", "segoeuib.ttf", "arialbd.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _vertical_gradient(size, top, bottom):
    grad = Image.new("RGB", (1, size))
    for y in range(size):
        t = y / (size - 1)
        grad.putpixel((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return grad.resize((size, size))


def build(size=S):
    # fondo con degradado y esquinas redondeadas
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    grad = _vertical_gradient(size, TOP, BOTTOM).convert("RGBA")
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1],
                                           radius=RADIUS, fill=255)
    img.paste(grad, (0, 0), mask)

    draw = ImageDraw.Draw(img)

    # sombra/brillo sutil arriba a la izquierda
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle(
        [int(size * 0.06), int(size * 0.06), int(size * 0.94), int(size * 0.5)],
        radius=int(RADIUS * 0.7), fill=(255, 255, 255, 26))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # letra R centrada (un poco hacia arriba)
    font = _load_font(int(size * 0.64))
    text = "R"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (size - tw) / 2 - bbox[0]
    ty = (size - th) / 2 - bbox[1] - int(size * 0.09)
    # letra plana, sin sombra
    draw.text((tx, ty), text, font=font, fill=(255, 255, 255, 255))

    # interruptor (toggle) verde en la parte inferior, mas grande (plano)
    pill_w, pill_h = int(size * 0.46), int(size * 0.205)
    px = (size - pill_w) // 2
    py = int(size * 0.70)
    draw.rounded_rectangle([px, py, px + pill_w, py + pill_h],
                           radius=pill_h // 2, fill=GREEN)
    knob_r = int(pill_h * 0.36)
    kcx = px + pill_w - pill_h // 2
    kcy = py + pill_h // 2
    draw.ellipse([kcx - knob_r, kcy - knob_r, kcx + knob_r, kcy + knob_r],
                 fill=(255, 255, 255, 255))
    return img


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    master = build(S)

    # vista previa PNG
    master.resize((256, 256), Image.LANCZOS).save(os.path.join(here, "REPTOSX_preview.png"))

    # .ico multi-tamano
    sizes = [256, 128, 64, 48, 32, 16]
    icons = [master.resize((s, s), Image.LANCZOS) for s in sizes]
    icons[0].save(os.path.join(here, "REPTOSX.ico"), format="ICO",
                  sizes=[(s, s) for s in sizes])
    print("Generado REPTOSX.ico y REPTOSX_preview.png en", here)


if __name__ == "__main__":
    main()
