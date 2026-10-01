#!/usr/bin/env python3
"""Draws the NotchBuddy app icon in code (Pillow only) and writes every size the
macOS asset catalog, the menu bar, the website and the Windows (Tauri) build need.

    python3 scripts/gen-icons.py

Design: a dark rounded tile with a MacBook-style notch cut into its top edge, and
Buddy — a soft lavender superellipse with two pill eyes — peeking out from under
the notch. Colors match BuddyConst in BotEngine.swift / engine.ts.
"""
import os
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPICON = os.path.join(ROOT, "NotchBuddy/Assets.xcassets/AppIcon.appiconset")
MENUBAR = os.path.join(ROOT, "NotchBuddy/Assets.xcassets/MenuBarIcon.imageset")
WEB = os.path.join(ROOT, "docs/media")
WIN = os.path.join(ROOT, "windows/src-tauri/icons")

TILE_TOP = (30, 32, 40)        # #1E2028
TILE_BOTTOM = (14, 15, 20)     # #0E0F14
BODY_TOP = (242, 238, 255)     # #F2EEFF  BuddyConst.baseTop
BODY_BOTTOM = (201, 194, 230)  # #C9C2E6  BuddyConst.baseBottom
INK = (20, 24, 40)             # #141828  BuddyConst.ink
CHEEK = (255, 140, 170, 110)
GLOW = (138, 180, 255)         # #8AB4FF  site accent

SS = 4  # supersampling


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vgradient(size, top, bottom):
    img = Image.new("RGB", (size, size))
    px = img.load()
    for y in range(size):
        c = lerp(top, bottom, y / max(1, size - 1))
        for x in range(size):
            px[x, y] = c
    return img


def superellipse_mask(size, cx, cy, rx, ry, n=2.7):
    mask = Image.new("L", (size, size), 0)
    px = mask.load()
    x0, x1 = int(max(0, cx - rx - 1)), int(min(size, cx + rx + 2))
    y0, y1 = int(max(0, cy - ry - 1)), int(min(size, cy + ry + 2))
    for y in range(y0, y1):
        for x in range(x0, x1):
            u = abs((x + 0.5 - cx) / rx) ** n + abs((y + 0.5 - cy) / ry) ** n
            if u <= 1:
                px[x, y] = 255
    return mask


def render_icon(size):
    """Full app icon (macOS / Windows / web), transparent corners."""
    S = size * SS
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))

    # Tile: rounded square with a notch cut from the top edge
    inset = S * 0.08
    radius = S * 0.21
    tile_mask = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(tile_mask)
    d.rounded_rectangle([inset, inset, S - inset, S - inset], radius=radius, fill=255)
    notch_w, notch_h = S * 0.40, S * 0.12
    d.rounded_rectangle(
        [S / 2 - notch_w / 2, inset - 1, S / 2 + notch_w / 2, inset + notch_h],
        radius=notch_h * 0.45, fill=0,
    )
    d.rectangle([S / 2 - notch_w / 2, inset - 1, S / 2 + notch_w / 2, inset + notch_h * 0.5], fill=0)
    tile = vgradient(S, TILE_TOP, TILE_BOTTOM).convert("RGBA")
    img.paste(tile, (0, 0), tile_mask)

    # Soft glow behind Buddy
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([S * 0.22, S * 0.30, S * 0.78, S * 0.86], fill=GLOW + (110,))
    glow = glow.filter(ImageFilter.GaussianBlur(S * 0.07))
    glow_masked = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    glow_masked.paste(glow, (0, 0), tile_mask)
    img = Image.alpha_composite(img, glow_masked)

    # Buddy body: superellipse, lavender gradient
    cx, cy = S / 2, S * 0.58
    rx, ry = S * 0.27, S * 0.235
    body_mask = superellipse_mask(S, cx, cy, rx, ry)
    body = vgradient(S, BODY_TOP, BODY_BOTTOM).convert("RGBA")
    body_layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    body_layer.paste(body, (0, 0), body_mask)
    img = Image.alpha_composite(img, body_layer)

    # Face
    face = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    fd = ImageDraw.Draw(face)
    eye_w, eye_h = rx * 0.25, ry * 0.46
    eye_dx, eye_y = rx * 0.40, cy - ry * 0.10
    for sgn in (-1, 1):
        ex = cx + sgn * eye_dx
        fd.rounded_rectangle([ex - eye_w / 2, eye_y - eye_h / 2, ex + eye_w / 2, eye_y + eye_h / 2],
                             radius=eye_w / 2, fill=INK + (255,))
        # highlight
        fd.ellipse([ex - eye_w * 0.22, eye_y - eye_h * 0.36, ex + eye_w * 0.10, eye_y - eye_h * 0.08],
                   fill=(255, 255, 255, 220))
        # cheek
        ch_w, ch_h = rx * 0.30, ry * 0.16
        chx, chy = cx + sgn * rx * 0.66, cy + ry * 0.26
        fd.ellipse([chx - ch_w / 2, chy - ch_h / 2, chx + ch_w / 2, chy + ch_h / 2], fill=CHEEK)
    # small smile
    mw, mh = rx * 0.26, ry * 0.18
    fd.arc([cx - mw / 2, cy + ry * 0.22 - mh, cx + mw / 2, cy + ry * 0.22 + mh],
           start=20, end=160, fill=INK + (255,), width=max(1, int(S * 0.012)))
    img = Image.alpha_composite(img, face)

    return img.resize((size, size), Image.LANCZOS)


def render_menubar(w, h):
    """Monochrome template image: Buddy silhouette with cut-out eyes."""
    S_w, S_h = w * SS, h * SS
    img = Image.new("L", (S_w, S_h), 0)
    cx, cy = S_w / 2, S_h / 2
    rx, ry = S_w * 0.42, S_h * 0.40
    px = img.load()
    for y in range(S_h):
        for x in range(S_w):
            u = abs((x + 0.5 - cx) / rx) ** 2.7 + abs((y + 0.5 - cy) / ry) ** 2.7
            if u <= 1:
                px[x, y] = 255
    d = ImageDraw.Draw(img)
    eye_w, eye_h = rx * 0.22, ry * 0.50
    for sgn in (-1, 1):
        ex, ey = cx + sgn * rx * 0.40, cy - ry * 0.05
        d.rounded_rectangle([ex - eye_w / 2, ey - eye_h / 2, ex + eye_w / 2, ey + eye_h / 2],
                            radius=eye_w / 2, fill=0)
    alpha = img.resize((w, h), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    out.putalpha(alpha)
    return out


def main():
    for d in (APPICON, MENUBAR, WEB, WIN):
        os.makedirs(d, exist_ok=True)

    # macOS AppIcon.appiconset (filenames from Contents.json)
    for pt in (16, 32, 128, 256, 512):
        render_icon(pt).save(os.path.join(APPICON, f"icon_{pt}x{pt}.png"))
        render_icon(pt * 2).save(os.path.join(APPICON, f"icon_{pt}x{pt}@2x.png"))
    print("AppIcon.appiconset: 10 files")

    # Menu bar template (24x18 @1x/2x/3x)
    for scale, suffix in ((1, ""), (2, "@2x"), (3, "@3x")):
        render_menubar(24 * scale, 18 * scale).save(os.path.join(MENUBAR, f"menubar{suffix}.png"))
    print("MenuBarIcon.imageset: 3 files")

    # Website favicon / header
    render_icon(256).save(os.path.join(WEB, "icon.png"))
    print("docs/media/icon.png")

    # Windows (Tauri): PNG set + multi-size ICO
    for name, size in (("32x32.png", 32), ("128x128.png", 128), ("128x128@2x.png", 256), ("icon.png", 512)):
        render_icon(size).save(os.path.join(WIN, name))
    render_icon(256).save(os.path.join(WIN, "icon.ico"), format="ICO",
                          sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("windows/src-tauri/icons: 5 files")


if __name__ == "__main__":
    main()
