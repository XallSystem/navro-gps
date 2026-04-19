#!/usr/bin/env python3
"""Generate NavRo app icons for all Android mipmap densities."""
import os, math
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    os.system('pip3 install Pillow --quiet')
    from PIL import Image, ImageDraw, ImageFont

def create_navro_icon(size=1024):
    img = Image.new('RGBA', (size, size), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    s = size

    def rrect(x1, y1, x2, y2, r, fill):
        draw.rectangle([x1+r, y1, x2-r, y2], fill=fill)
        draw.rectangle([x1, y1+r, x2, y2-r], fill=fill)
        draw.pieslice([x1, y1, x1+2*r, y1+2*r], 180, 270, fill=fill)
        draw.pieslice([x2-2*r, y1, x2, y1+2*r], 270, 360, fill=fill)
        draw.pieslice([x1, y2-2*r, x1+2*r, y2], 90, 180, fill=fill)
        draw.pieslice([x2-2*r, y2-2*r, x2, y2], 0, 90, fill=fill)

    # Blue background
    rrect(0, 0, s, s, int(s*0.18), (21, 101, 192, 255))
    # Lighter blue gradient top
    for i in range(int(s*0.45)):
        a = int(55 * (1 - i/(s*0.45)))
        draw.line([(0,i),(s,i)], fill=(30, 136, 229, a))

    # Green hill
    draw.ellipse([int(-s*.1), int(s*.66), int(s*1.1), int(s*1.22)], fill=(46,125,50,255))
    draw.ellipse([int(-s*.1), int(s*.63), int(s*1.1), int(s*1.16)], fill=(56,142,60,255))

    # White road
    cx = s//2
    rw = int(s*.09)
    draw.rectangle([cx-rw, int(s*.64), cx+rw, s], fill=(238,238,238,230))
    for dy in range(0, int(s*.28), int(s*.06)):
        draw.rectangle([cx-int(s*.008), int(s*.68)+dy, cx+int(s*.008), int(s*.68)+dy+int(s*.032)], fill=(255,255,255,200))

    # Red pin circle
    pc, pr = (cx, int(s*.37)), int(s*.162)
    draw.ellipse([pc[0]-pr+5, pc[1]-pr+8, pc[0]+pr+5, pc[1]+pr+8], fill=(0,0,0,50))
    draw.ellipse([pc[0]-pr, pc[1]-pr, pc[0]+pr, pc[1]+pr], fill=(229,57,53,255))
    draw.ellipse([pc[0]-pr, pc[1]-pr, pc[0]+pr, pc[1]+pr], outline=(255,255,255,255), width=int(s*.022))
    ir = int(pr*.40)
    draw.ellipse([pc[0]-ir, pc[1]-ir, pc[0]+ir, pc[1]+ir], fill=(255,255,255,255))
    # Pin tail
    ty = pc[1]+pr-int(pr*.18)
    draw.polygon([(pc[0], pc[1]+pr+int(pr*.95)), (pc[0]-int(pr*.5), ty), (pc[0]+int(pr*.5), ty)], fill=(229,57,53,255))

    # Yellow star
    scx, scy = int(s*.82), int(s*.16)
    sr_out, sr_in = int(s*.092), int(s*.038)
    pts = []
    for i in range(10):
        angle = -math.pi/2 + i*math.pi/5
        r = sr_out if i%2==0 else sr_in
        pts.append((scx + r*math.cos(angle), scy + r*math.sin(angle)))
    draw.polygon(pts, fill=(255,214,0,255))

    # NavRo text on hill
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', int(s*.082))
    except:
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', int(s*.082))
        except:
            font = ImageFont.load_default()
    txt = 'NavRo'
    bb = draw.textbbox((0,0), txt, font=font)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    tx, ty2 = (s-tw)//2, int(s*.69)
    draw.text((tx+2, ty2+3), txt, font=font, fill=(0,0,0,100))
    draw.text((tx, ty2), txt, font=font, fill=(255,255,255,255))

    return img

DENSITIES = {
    'mdpi':    48,
    'hdpi':    72,
    'xhdpi':   96,
    'xxhdpi':  144,
    'xxxhdpi': 192,
}
BASE = 'android/app/src/main/res'

icon1024 = create_navro_icon(1024)

for density, px in DENSITIES.items():
    resized = icon1024.resize((px, px), Image.LANCZOS)
    bg = Image.new('RGB', (px, px), (21, 101, 192))
    bg.paste(resized, mask=resized.split()[3])
    for name in ('ic_launcher.png', 'ic_launcher_round.png', 'ic_launcher_foreground.png'):
        path = os.path.join(BASE, f'mipmap-{density}', name)
        if os.path.exists(os.path.dirname(path)):
            bg.save(path, 'PNG')
            print(f'Wrote {path}')

print('Icon generation complete.')
