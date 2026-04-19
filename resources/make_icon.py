#!/usr/bin/env python3
"""Generate NavRo launcher icons for all Android mipmap densities.

Design: dark metallic background, green bottom glow, blue light beams,
folded map with coloured quadrants, blue winding road, red location pin
with white sphere, gold star, 'NaVro' text.
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

DENSITIES = {
    'mdpi': 48, 'hdpi': 72, 'xhdpi': 96,
    'xxhdpi': 144, 'xxxhdpi': 192,
}
BASE = 'android/app/src/main/res'


def _star_polygon(cx, cy, r_out, r_in, n=5):
    """Return polygon point list for an n-pointed star."""
    pts = []
    for i in range(2 * n):
        angle = -math.pi / 2 + i * math.pi / n
        r = r_out if (i % 2 == 0) else r_in
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return pts


def _load_font(size):
    candidates = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def create_navro_icon(size=1024):
    s = size

    # 1. Vectorised background gradient
    y_f = np.linspace(0, 1, s).reshape(-1, 1) * np.ones((s, s))
    x_f = np.linspace(0, 1, s).reshape(1, -1) * np.ones((s, s))
    dist_c = np.sqrt((x_f - 0.5) ** 2 + (y_f - 0.5) ** 2)

    R = np.clip(8 + 14 * (1 - dist_c / 0.72), 4, 22).astype(float)
    G = np.clip(10 + 16 * (1 - dist_c / 0.72), 4, 26).astype(float)
    B = np.clip(28 + 52 * (1 - dist_c / 0.72), 12, 80).astype(float)

    # Green atmospheric glow (bottom-centre)
    dist_g = np.sqrt((x_f - 0.5) ** 2 + (y_f - 0.86) ** 2)
    g_glow = np.clip((0.42 - dist_g) / 0.42, 0, 1) ** 2 * 130
    G = np.clip(G + g_glow, 0, 255)
    R = np.clip(R + g_glow * 0.12, 0, 255)
    B = np.clip(B - g_glow * 0.25, 0, 255)

    # Blue halo behind the pin (top-centre)
    dist_b = np.sqrt((x_f - 0.5) ** 2 + (y_f - 0.27) ** 2)
    b_halo = np.clip((0.38 - dist_b) / 0.38, 0, 1) ** 1.5 * 110
    B = np.clip(B + b_halo, 0, 255)
    G = np.clip(G + b_halo * 0.35, 0, 255)
    R = np.clip(R + b_halo * 0.18, 0, 255)

    A = np.full((s, s), 255, dtype=np.uint8)
    arr = np.stack([R.astype(np.uint8), G.astype(np.uint8),
                    B.astype(np.uint8), A], axis=2)
    img = Image.fromarray(arr, 'RGBA')

    # 2. Rounded-square mask
    r_corner = int(s * 0.19)
    mask = Image.new('L', (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, s - 1, s - 1],
                                           radius=r_corner, fill=255)
    img.putalpha(mask)

    # 3. Light beams (radiating from pin centre)
    beam_cx, beam_cy = s // 2, int(s * 0.27)
    rays = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rays)
    ray_w = max(4, s // 70)
    for deg in range(0, 360, 20):
        angle = math.radians(deg)
        x2 = beam_cx + int(math.cos(angle) * s * 0.85)
        y2 = beam_cy + int(math.sin(angle) * s * 0.85)
        rd.line([(beam_cx, beam_cy), (x2, y2)],
                fill=(90, 150, 255, 30), width=ray_w)
    img = Image.alpha_composite(img,
                                rays.filter(ImageFilter.GaussianBlur(s // 38)))

    draw = ImageDraw.Draw(img)

    # 4. Map body
    ML = int(s * 0.112)
    MT = int(s * 0.190)
    MW = int(s * 0.776)
    MH = int(s * 0.555)
    MR = ML + MW
    MB = MT + MH
    MX = ML + MW // 2
    MY = MT + MH // 2

    draw.rectangle([ML, MT, MR, MB], fill=(245, 245, 245))
    draw.rectangle([ML, MT, MX, MY], fill=(58, 120, 215))
    draw.rectangle([MX, MT, MR, MY], fill=(68, 178, 70))
    draw.rectangle([ML, MY, MX, MB], fill=(88, 158, 52))
    draw.rectangle([MX, MY, MR, MB], fill=(218, 172, 40))

    lw = max(2, s // 105)
    bw = max(3, s // 80)
    draw.line([MX, MT, MX, MB], fill=(255, 255, 255), width=lw)
    draw.line([ML, MY, MR, MY], fill=(255, 255, 255), width=lw)
    draw.rectangle([ML, MT, MR, MB], outline=(255, 255, 255), width=bw)

    # 5. Winding road
    N = 60
    road_pts = []
    for i in range(N):
        t = i / (N - 1)
        ry = MT + int(t * MH)
        amp = MW * 0.13 * math.sin(t * math.pi)
        rx = MX + int(math.sin(t * math.pi * 1.9) * amp)
        road_pts.append((rx, ry))

    road_w = max(8, s // 38)
    for i in range(len(road_pts) - 1):
        draw.line([road_pts[i], road_pts[i + 1]],
                  fill=(180, 210, 255), width=road_w + max(4, s // 80))
    for i in range(len(road_pts) - 1):
        draw.line([road_pts[i], road_pts[i + 1]],
                  fill=(35, 95, 225), width=road_w)

    # 6. Gold star
    si = int(len(road_pts) * 0.62)
    scx, scy = road_pts[si]
    sR = int(s * 0.058)
    sr = int(sR * 0.40)
    draw.polygon(_star_polygon(scx, scy, sR, sr), fill=(255, 202, 0))
    draw.polygon(_star_polygon(scx, scy, sR, sr), outline=(200, 155, 0), fill=None)

    # 7. Location pin
    pcx = s // 2
    phr = int(s * 0.130)
    pcy = MT - int(phr * 0.55)
    tip_y = MT + int(s * 0.06)

    PIN_RED = (215, 28, 28)

    pin_pts = []
    for deg in range(210, 331, 5):
        angle = math.radians(deg)
        pin_pts.append((pcx + phr * math.cos(angle),
                        pcy + phr * math.sin(angle)))
    pin_pts.append((pcx, tip_y))
    draw.polygon(pin_pts, fill=PIN_RED)
    draw.ellipse([pcx - phr, pcy - phr, pcx + phr, pcy + phr], fill=PIN_RED)

    sp_r = int(phr * 0.44)
    sp_ox = -int(phr * 0.07)
    sp_oy = -int(phr * 0.07)
    draw.ellipse([pcx + sp_ox - sp_r, pcy + sp_oy - sp_r,
                  pcx + sp_ox + sp_r, pcy + sp_oy + sp_r],
                 fill=(255, 255, 255))
    hl_r = int(sp_r * 0.28)
    hl_ox, hl_oy = -int(sp_r * 0.30), -int(sp_r * 0.30)
    draw.ellipse([pcx + sp_ox + hl_ox - hl_r, pcy + sp_oy + hl_oy - hl_r,
                  pcx + sp_ox + hl_ox + hl_r, pcy + sp_oy + hl_oy + hl_r],
                 fill=(255, 255, 255))

    # 8. "NaVro" text
    text = "NaVro"
    font_sz = int(s * 0.128)
    font = _load_font(font_sz)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    tx = (s - tw) // 2
    ty = int(s * 0.831)
    sho = max(2, s // 115)
    draw.text((tx + sho, ty + sho), text, font=font, fill=(0, 0, 0, 150))
    draw.text((tx, ty), text, font=font, fill=(255, 255, 255, 255))

    # 9. Metallic border overlay
    border = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    bd = ImageDraw.Draw(border)
    bord_w = max(4, s // 40)
    bd.rounded_rectangle([0, 0, s - 1, s - 1],
                         radius=r_corner, outline=(100, 100, 100, 200),
                         width=bord_w)
    inner_inset = bord_w
    bd.rounded_rectangle([inner_inset, inner_inset,
                          s - 1 - inner_inset, s - 1 - inner_inset],
                         radius=max(10, r_corner - inner_inset),
                         outline=(25, 25, 25, 180),
                         width=bord_w // 2)
    img = Image.alpha_composite(img, border)

    return img


if __name__ == '__main__':
    print("Generating NavRo icon ...")
    icon1024 = create_navro_icon(1024)

    for density, px in DENSITIES.items():
        dir_path = os.path.join(BASE, f'mipmap-{density}')
        if not os.path.exists(dir_path):
            print(f"  skip {density} (directory not found)")
            continue
        resized = icon1024.resize((px, px), Image.LANCZOS)
        bg = Image.new('RGB', (px, px), (10, 12, 30))
        bg.paste(resized, mask=resized.split()[3])
        for name in ('ic_launcher.png',
                     'ic_launcher_round.png',
                     'ic_launcher_foreground.png'):
            out = os.path.join(dir_path, name)
            bg.save(out, 'PNG')
        print(f"  wrote {density} ({px}px)")

    print("Done!")
