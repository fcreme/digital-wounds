"""Stand-in tattoo designs, part one. Each function draws one design."""

import math

from ink import (
    arc,
    circle,
    leaf,
    mirror,
    ngon,
    petal,
    place,
    polar,
    resample,
    ribbon,
    spline,
    star,
    sym,
    taper,
)

# --- Shared parts ---------------------------------------------------------

SKULL = sym(
    [(0, -1.0), (0.42, -0.94), (0.72, -0.62), (0.76, -0.22), (0.62, 0.1), (0.46, 0.2), (0.42, 0.44), (0.3, 0.68), (0, 0.72)]
)
SOCKET = spline([(-0.1, -0.2), (0.12, -0.24), (0.22, -0.06), (0.14, 0.12), (-0.1, 0.12), (-0.2, -0.04)], closed=True)
NOSE = [(0, 0.08), (0.1, 0.3), (0.02, 0.28), (0, 0.33), (-0.02, 0.28), (-0.1, 0.3)]
HEART = sym([(0, -0.5), (0.32, -0.92), (0.78, -0.86), (0.96, -0.42), (0.72, 0.12), (0.34, 0.56), (0, 0.95)])


def curl(x, y, degrees, size, turn=540.0, sign=1, count=48):
    """A turtle spiral: runs out straight, and tightens as it goes."""
    pts = [(x, y)]
    for i in range(count):
        t = i / count
        heading = degrees + sign * turn * t ** 1.8
        step = size / count * (1.7 * (1 - t) + 0.2)
        x, y = polar(step, heading, x, y)
        pts.append((x, y))
    return pts


def branch(c, x, y, degrees, length, width, depth, rng, ink=1):
    """A bare tree limb, bent as it grows, forking until it is twigs."""
    pts = [(x, y)]
    heading = degrees
    for _ in range(5):
        heading += rng.uniform(-14, 14)
        x, y = polar(length / 5, heading, x, y)
        pts.append((x, y))
    c.line(pts, lambda t: width * (1 - 0.4 * t), ink)
    if depth <= 0:
        return
    forks = 2 if rng.random() < 0.75 else 3
    for i in range(forks):
        spread = (i - (forks - 1) / 2) * rng.uniform(34, 52)
        branch(c, x, y, heading + spread, length * rng.uniform(0.62, 0.8), width * 0.62, depth - 1, rng, ink)


def thorn_line(c, spine, width, every, size, rng, ink=1):
    c.line(spine, width, ink)
    pts = resample(spine, max(int(len(spine) / every), 2))
    for i, p in enumerate(pts[1:-1]):
        a, b = pts[i], pts[i + 2]
        heading = math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1])))
        side = 90 if i % 2 else -90
        tip = polar(size, heading + side * 0.6, p[0], p[1])
        left = polar(size * 0.3, heading + 180, p[0], p[1])
        right = polar(size * 0.3, heading, p[0], p[1])
        c.fill([left, tip, right], ink)


# --- 1. Dark Ink Studio: occult blackwork, huge black masses, cut-out detail --


def _black_feather(c, x, y, degrees, length, width):
    c.fill(leaf(x, y, degrees, length, width, belly=0.58))
    tip = polar(length * 0.94, degrees, x, y)
    c.line([(x, y), tip], taper(0.012, 0.012, 0.002), 0)
    for i in range(3, 12):
        t = i / 13
        px, py = polar(length * t, degrees, x, y)
        half = width * 0.4 * math.sin(math.pi * t ** 0.75)
        for side in (1, -1):
            c.line([(px, py), polar(half, degrees + side * 52, px, py)], taper(0.007, 0.007, 0.002), 0)


def ravens_eye(c, rng):
    for i in range(16):
        _black_feather(c, *polar(0.3, 22.5 * i + 11), 22.5 * i + 11, 0.72, 0.28)
    for i in range(16):
        _black_feather(c, *polar(0.22, 22.5 * i), 22.5 * i, 0.62, 0.3)
    c.fill(circle(0, 0, 0.58), 1)
    c.ring(0, 0, 0.53, 0.012, 0)
    almond = leaf(-0.48, 0, 90, 0.96, 0.62)
    c.fill(almond, 0)
    c.fill(circle(0, 0, 0.27))
    for i in range(36):
        c.line([polar(0.13, i * 10), polar(0.245, i * 10)], taper(0.01, 0.006, 0.002), 0)
    c.fill(circle(0, 0, 0.12))
    c.fill(circle(-0.06, -0.07, 0.04), 0)
    for i in range(9):
        c.line([polar(0.28 + 0.02 * abs(i - 4), 180 + 28 * (i - 4) * 0.8, 0, 0.05),
                polar(0.47, 180 + 28 * (i - 4) * 0.8, 0, 0.05)], taper(0.012, 0.008, 0.002), 0)


def _thorn_rose(c, x, y, s, rng, rot=0.0):
    c.fill(circle(x, y, s * 1.08))
    for ring, (radius, count) in enumerate(((0.92, 7), (0.66, 6), (0.42, 5))):
        for i in range(count):
            a = rot + (i + ring * 0.5) * 360 / count
            c.line(arc(*polar(radius * 0.55 * s, a, x, y), radius * 0.62 * s, a - 62, a + 62, 18),
                   taper(0.004, 0.016 * (s / 0.3) ** 0.5, 0.004), 0)
    c.line(curl(*polar(s * 0.26, rot + 40, x, y), rot + 130, s * 0.62, 560), taper(0.016, 0.012, 0.004), 0)


def bone_garden(c, rng):
    vine = [(-0.96, 0.82), (-0.72, 0.1), (-0.8, -0.5), (-0.28, -0.92), (0.28, -0.92), (0.8, -0.5), (0.72, 0.1), (0.96, 0.82)]
    thorn_line(c, spline(vine), 0.024, 2.2, 0.075, rng)
    for sx in (-1, 1):
        lower = [(sx * 0.1, 0.92), (sx * 0.5, 0.72), (sx * 0.86, 0.34)]
        thorn_line(c, spline(lower), 0.022, 1.2, 0.07, rng)
    for x, y, a, l in ((-0.86, -0.1, 300, 0.2), (0.86, -0.1, 60, 0.2), (-0.6, -0.9, 320, 0.28), (0.6, -0.9, 40, 0.28), (-0.7, 0.86, 250, 0.3), (0.7, 0.86, 110, 0.3)):
        c.fill(leaf(x, y, a, l, 0.15))
    skull = place(SKULL, 0, 0.0, 0.56)
    c.shape(skull, 0.03, solid=True)
    for sx in (-1, 1):
        c.fill(place(SOCKET, sx * 0.175, -0.05, 0.56, flip=sx < 0), 0)
        for i in range(5):
            c.fill(petal(sx * 0.175, -0.05, 72 * i, 0.075, 0.06))
        c.fill(circle(sx * 0.175, -0.05, 0.017), 0)
    c.fill(place(NOSE, 0, 0.0, 0.56), 0)
    for i in range(-3, 4):
        c.line([(i * 0.055, 0.25), (i * 0.05, 0.38)], 0.014, 0)
    c.line(spline([(-0.2, 0.23), (0, 0.255), (0.2, 0.23)]), 0.01, 0)
    for i, (x, y, r) in enumerate(((-0.58, -0.56, 0.27), (0.58, -0.56, 0.27), (-0.5, 0.56, 0.3), (0.5, 0.56, 0.3), (0, -0.82, 0.21))):
        c.ring(x, y, r * 1.08, 0.024, 0)
        _thorn_rose(c, x, y, r, rng, rot=i * 47)


def serpents_embrace(c, rng):
    inner_star = [star(0, 0, 0.5, 0.29, 6, rot=0), circle(0, 0, 0.19, 60)]
    mask = c.mask_of(inner_star)
    field = mask.field()
    c.stipple(mask, lambda x, y: min(1.0, 1.05 - field(x, y) / 0.1), 0.0135, 0.0055, rng)
    c.line(star(0, 0, 0.5, 0.29, 6), 0.014, closed=True)
    c.ring(0, 0, 0.19, 0.014)
    c.fill(circle(0, 0, 0.09))
    for i in range(6):
        c.disc(*polar(0.565, 30 + 60 * i), 0.016)
    # The tail runs clockwise from the head all the way round into its mouth.
    ring_pts = arc(0, 0, 0.76, 24, 358, 200)
    width = lambda t: 0.035 + 0.2 * min((1 - t) * 2.2, 1.0) ** 0.8
    c.line(ring_pts, width)
    pts = resample(ring_pts, 72)
    for i in range(2, 70):
        t = i / 71
        size = width(t) * 0.26
        c.fill(ngon(pts[i][0], pts[i][1], size, 4, rot=i * 334 / 71 + 24), 0)
        c.disc(pts[i][0], pts[i][1], size * 0.36)
    head = spline([(-0.2, -0.13), (0.02, -0.17), (0.2, -0.11), (0.3, 0.0), (0.2, 0.11), (0.02, 0.17), (-0.2, 0.13)], closed=True)
    head = place(head, *polar(0.76, 22), rot=24)
    c.shape(head, 0.02, solid=True)
    # The tail's tip goes in at the jaw, under the head.
    x, y = polar(0.78, 22)
    c.fill(circle(*polar(0.71, 36), 0.032, 30), 0)
    c.disc(*polar(0.71, 36), 0.016)
    c.line([polar(0.85, 41), polar(0.8, 24)], 0.012, 0)
    for i in range(5):
        c.fill(leaf(*polar(0.7 + 0.03 * i, 12 - i), 300 + i * 12, 0.05, 0.02), 0)


def shadow_forest(c, rng):
    c.fill(circle(0, 0, 1.0, 180))
    moon = circle(0, -0.1, 0.68, 150)
    c.fill(moon, 0)
    for x, y, r in ((-0.26, -0.42, 0.13), (0.24, -0.34, 0.09), (0.04, -0.04, 0.11), (0.38, -0.56, 0.06), (-0.4, -0.08, 0.06)):
        crater = c.mask_of(circle(x, y, r, 40))
        c.stipple(crater, lambda a, b: 0.55, 0.016, 0.0055, rng)
    layer = type(c)()
    for x, height, width, lean in ((-0.46, 0.66, 0.08, -8), (0.36, 0.78, 0.095, 7), (-0.05, 0.46, 0.05, 2), (0.76, 0.44, 0.06, 12), (-0.8, 0.46, 0.06, -14)):
        layer.line([(x, 1.0), (x, 0.66)], taper(width * 1.9, width), 1)
        branch(layer, x, 0.68, lean, height * 0.68, width, 6, rng)
    layer.fill(spline([(-1.1, 1.1), (-1.1, 0.76), (-0.5, 0.68), (0.1, 0.76), (0.6, 0.66), (1.1, 0.76), (1.1, 1.1)], closed=True))
    c.stamp(layer, c.mask_of(circle(0, 0, 1.0, 180)))
    for i in range(30):
        a, r = rng.uniform(0, 360), rng.uniform(0.72, 0.94)
        x, y = polar(r, a)
        if y < 0.3 and math.hypot(x, y + 0.1) > 0.73:
            c.disc(x, y, rng.uniform(0.005, 0.012), 0)
    c.ring(0, 0, 0.965, 0.009, 0)


def _moth_wings(c, ink, line_ink):
    fore = spline([(0.03, -0.32), (0.34, -0.72), (0.76, -0.86), (1.0, -0.66), (0.9, -0.3), (0.56, -0.04), (0.14, -0.02)], closed=True)
    hind = spline([(0.05, 0.0), (0.46, 0.02), (0.74, 0.22), (0.64, 0.62), (0.34, 0.8), (0.12, 0.46)], closed=True)
    for wing in (hind, fore):
        for shape in (wing, mirror(wing)):
            c.shape(shape, 0.018, solid=ink)
    return fore, hind


def moth_sigil(c, rng):
    fore, hind = _moth_wings(c, 1, 0)
    for sx in (1, -1):
        for a, l in ((42, 0.72), (56, 0.82), (72, 0.78), (90, 0.66), (108, 0.5)):
            c.line(place(spline([(0.06, -0.22), polar(l * 0.55, a - 6, 0.06, -0.22), polar(l, a, 0.06, -0.22)]), flip=sx < 0),
                   taper(0.012, 0.01, 0.003), 0)
        for a, l in ((88, 0.6), (112, 0.68), (136, 0.72), (160, 0.66)):
            c.line(place([(0.08, 0.06), polar(l * 0.5, a - 5, 0.08, 0.06), polar(l, a, 0.08, 0.06)], flip=sx < 0),
                   taper(0.01, 0.01, 0.003), 0)
        for i in range(7):
            c.disc(sx * (0.28 + i * 0.1), -0.72 + 0.02 * (i - 3) ** 2 + i * 0.075, 0.018, 0)
        c.fill(place(circle(0.54, -0.42, 0.07, 40), flip=sx < 0), 0)
        c.fill(place(circle(0.54, -0.42, 0.035, 30), flip=sx < 0))
        c.fill(place(star(0.42, 0.4, 0.09, 0.03, 4), flip=sx < 0), 0)
        c.line(spline([(sx * 0.04, -0.44), (sx * 0.16, -0.68), (sx * 0.36, -0.86)]), 0.014)
    c.shape(sym([(0, -0.5), (0.11, -0.42), (0.15, -0.16), (0.14, 0.2), (0.08, 0.6), (0, 0.84)]), 0.016, solid=True)
    for i in range(5):
        y = 0.22 + i * 0.11
        c.line([(-0.13 + i * 0.015, y), (0.13 - i * 0.015, y)], 0.01, 0)
    skull = place(SKULL, 0, -0.2, 0.15)
    c.fill(skull, 0)
    for sx in (-1, 1):
        c.fill(place(SOCKET, sx * 0.046, -0.22, 0.15, flip=sx < 0))
    c.fill(place(NOSE, 0, -0.21, 0.15))


def hollow_crown(c, rng):
    for i in range(32):
        a = 11.25 * i
        l = 0.26 if i % 2 else 0.38
        c.fill(leaf(*polar(0.5, a, 0, 0.18), a, l, 0.1 if i % 2 else 0.14))
    c.fill([circle(0, 0.18, 0.56, 150), circle(0, 0.18, 0.28, 90)])
    for i in range(24):
        a = 15 * i
        c.line([polar(0.33, a, 0, 0.18), polar(0.5, a, 0, 0.18)], taper(0.008, 0.012, 0.002), 0)
    c.fill(circle(0, 0.18, 0.13))
    crown = [(-0.62, -0.28), (-0.74, -0.76), (-0.44, -0.52), (-0.27, -0.9), (-0.09, -0.56), (0, -1.0),
             (0.09, -0.56), (0.27, -0.9), (0.44, -0.52), (0.74, -0.76), (0.62, -0.28)]
    band = spline([(-0.63, -0.3), (0, -0.16), (0.63, -0.3)])
    c.line(crown + band[::-1], 0.05, 0, closed=True)
    c.fill(crown + band[::-1])
    for x, y in ((-0.74, -0.8), (-0.27, -0.94), (0, -1.03), (0.27, -0.94), (0.74, -0.8)):
        c.disc(x, y, 0.036)
    for x, r in ((-0.36, 0.05), (0, 0.075), (0.36, 0.05)):
        y = -0.36 + abs(x) * 0.02
        c.fill(circle(x, y, r, 50), 0)
        c.fill(circle(x, y, r * 0.52, 30))


# --- 2. Thimble Moonwhisker: fine-line botanicals, single thin line, no fill --

FINE = 0.012


def _fine_leaf(c, x, y, a, l, w, veins=4):
    c.fill(leaf(x, y, a, l, w), 0)
    c.line(leaf(x, y, a, l, w), FINE, closed=True)
    c.line([(x, y), polar(l * 0.86, a, x, y)], FINE * 0.8)
    for i in range(1, veins + 1):
        t = i / (veins + 1)
        p = polar(l * t * 0.82, a, x, y)
        half = w * 0.42 * math.sin(math.pi * t)
        for side in (1, -1):
            c.line([p, polar(half, a + side * 45, *p)], FINE * 0.7)


def fern_frond(c, rng):
    spine = spline([(-0.34, 1.0), (-0.28, 0.45), (-0.08, -0.15), (0.2, -0.65), (0.48, -0.98)], steps=24)
    pts = resample(spine, 60)
    c.line(pts, taper(FINE * 1.8, FINE * 1.2, FINE * 0.6))
    for i in range(50, 3, -2):
        t = i / 60
        a, b = pts[i - 1], pts[i + 1]
        heading = math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1])))
        length = 0.08 + 0.46 * math.sin(math.pi * min((t + 0.06) * 0.98, 1.0)) ** 1.1 * (1 - t * 0.35)
        for side in (1, -1):
            out = heading + side * 62
            base = pts[i]
            frond = leaf(base[0], base[1], out, length, length * 0.24, belly=0.36)
            c.fill(frond, 0)
            c.line(frond, FINE * 0.9, closed=True)
            c.line([base, polar(length * 0.86, out, *base)], FINE * 0.65)
            for j in range(1, int(length * 16)):
                p = polar(length * j / int(length * 16) * 0.82, out, *base)
                half = length * 0.1 * math.sin(math.pi * (j / int(length * 16)) ** 0.7)
                for s2 in (1, -1):
                    c.line([p, polar(half, out + s2 * 56, *p)], FINE * 0.6)
    for i in range(52, 60, 2):
        a, b = pts[i - 1], pts[min(i + 1, 59)]
        heading = math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1])))
        for side in (1, -1):
            c.fill(leaf(pts[i][0], pts[i][1], heading + side * 40, 0.05, 0.02))


def poppy_stem(c, rng):
    stem = spline([(0.1, 1.0), (0.2, 0.45), (0.0, 0.0), (0.02, -0.18)], steps=20)
    c.line(stem, FINE * 1.3)
    side = spline([(0.17, 0.5), (0.48, 0.28), (0.66, -0.12), (0.62, -0.36)], steps=14)
    c.line(side, FINE * 1.2)
    for i, (x, y, a) in enumerate(((0.14, 0.62, 300), (0.2, 0.34, 60), (0.11, 0.84, 62))):
        _fine_leaf(c, x, y, a, 0.5 if i != 1 else 0.36, 0.17, veins=5)
    petals = (
        [(0.02, -0.2), (-0.42, -0.18), (-0.62, -0.48), (-0.5, -0.84), (-0.18, -0.92), (0.02, -0.74)],
        [(0.02, -0.2), (0.42, -0.2), (0.6, -0.5), (0.48, -0.84), (0.18, -0.94), (-0.02, -0.74)],
        [(-0.2, -0.32), (-0.26, -0.68), (0, -0.98), (0.26, -0.68), (0.2, -0.32), (0, -0.2)],
    )
    for pts in petals:
        shape = spline(pts, closed=True)
        c.line(shape, FINE, closed=True)
        c.fill(shape, 0)
        c.line(shape, FINE, closed=True)
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        for i in range(9):
            u = (i + 0.5) / 9
            p = (cx + (u - 0.5) * 0.56, cy - 0.2 + abs(u - 0.5) * 0.18)
            c.line([(0.02 + (p[0] - 0.02) * 0.34, -0.26 + (p[1] + 0.26) * 0.34), p], taper(FINE * 0.7, FINE * 0.5, 0.002))
    c.fill(circle(0.0, -0.32, 0.07, 40))
    for i in range(16):
        p = polar(0.115, 22.5 * i, 0.0, -0.32)
        c.line([polar(0.07, 22.5 * i, 0.0, -0.32), p], FINE * 0.6)
        c.disc(p[0], p[1], 0.008)
    c.fill(place(sym([(0, -0.14), (0.1, -0.08), (0.11, 0.04), (0.04, 0.12), (0, 0.13)]), 0.62, -0.46, 1.0), 0)
    c.line(place(sym([(0, -0.14), (0.1, -0.08), (0.11, 0.04), (0.04, 0.12), (0, 0.13)]), 0.62, -0.46, 1.0), FINE, closed=True)
    c.line([(0.5, -0.59), (0.62, -0.62), (0.74, -0.59)], FINE * 1.5)
    for i in range(-3, 4):
        c.line([(0.62, -0.34), (0.62 + i * 0.03, -0.58)], FINE * 0.6)


def foxglove_spire(c, rng):
    stem = spline([(-0.08, 1.0), (-0.04, 0.3), (0.02, -0.4), (0.0, -0.98)], steps=22)
    c.line(stem, FINE * 1.3)
    pts = resample(stem, 60)
    for x, y, a, l in ((-0.08, 0.86, 300, 0.62), (-0.07, 0.72, 62, 0.64), (-0.06, 0.92, 95, 0.5)):
        _fine_leaf(c, x, y, a, l, 0.22, veins=6)
    bell_shape = spline([(0, 0), (0.1, 0.05), (0.15, 0.3), (0.24, 0.56), (0.15, 0.6), (0.06, 0.66), (-0.06, 0.66), (-0.15, 0.6), (-0.24, 0.56), (-0.15, 0.3), (-0.1, 0.05)], closed=True)
    for i in range(14):
        t = i / 13
        p = pts[int(16 + t * 37)]
        size = 0.72 * (1 - t * 0.76)
        side = 1 if i % 2 else -1
        bell = place(bell_shape, p[0], p[1], size, rot=-side * 52)
        c.fill(bell, 0)
        c.line(bell, FINE, closed=True)
        mouth = polar(size * 0.46, 180 - side * 52, p[0], p[1])
        c.line(place(circle(0, 0, 0.17, 30, ry=0.05), mouth[0], mouth[1], size, rot=-side * 52), FINE * 0.8, closed=True)
        for j in range(int(4 + size * 18)):
            q = polar(rng.uniform(0.2, 0.42) * size, 180 - side * 52 + rng.uniform(-14, 14), p[0], p[1])
            c.disc(q[0], q[1], 0.0075)
    for i in range(8):
        p = (0.0, -0.84 - i * 0.02)
        c.fill(leaf(p[0], p[1], 150 if i % 2 else 210, 0.05, 0.03))


def moon_thistle(c, rng):
    outer = arc(0, -0.22, 0.82, 12, 168, 60)
    inner = arc(-0.2, -0.22, 0.76, 148, 28, 60)
    moon = outer + inner
    c.line(moon, FINE * 1.1, closed=True)
    for i in range(1, 60, 2):
        p = outer[i]
        q = polar(0.12 * math.sin(math.pi * i / 60) + 0.006, i * 156 / 60 + 192, *p)
        c.line([p, q], taper(FINE * 0.8, FINE * 0.6, 0.002))
    stem = spline([(-0.02, 1.0), (0.0, 0.4), (0.0, -0.3)], steps=20)
    c.line(stem, FINE * 1.3)
    for y, side, l in ((0.8, 1, 0.56), (0.62, -1, 0.56), (0.42, 1, 0.5), (0.24, -1, 0.42)):
        heading = 300 if side < 0 else 60
        tip = polar(l, heading, 0, y)
        spine = spline([(0, y), polar(l * 0.55, heading - side * 18, 0, y), tip])
        c.line(spine, FINE)
        for i in range(1, 6):
            p = spine[i * 4]
            for s2 in (1, -1):
                spike = polar(0.11 * (1 - i * 0.08), heading + s2 * 52, *p)
                c.line([p, spike], taper(FINE, FINE * 0.8, 0.002))
    bulb = sym([(0, -0.34), (0.2, -0.3), (0.3, -0.14), (0.24, 0.06), (0.1, 0.14), (0, 0.16)])
    c.fill(bulb, 0)
    c.line(bulb, FINE * 1.3, closed=True)
    for row in range(5):
        y = 0.1 - row * 0.09
        half = 0.2 + 0.09 * math.sin(row * 0.6)
        n = 3 + row
        for i in range(n):
            x = -half + (2 * half) * (i + 0.5) / n
            c.line([(x - 0.045, y), (x, y - 0.075), (x + 0.045, y)], FINE * 0.8)
    for i in range(29):
        a = -70 + i * 5
        base = polar(0.2, a, 0, -0.2)
        c.line([base, polar(0.42 + 0.16 * math.sin(i * 1.7) ** 2, a, 0, -0.2)], taper(FINE * 0.9, FINE * 0.7, 0.002))


def forest_caps(c, rng):
    def cap(x, y, s, rot):
        stalk = sym([(0, -0.06), (0.14, -0.02), (0.1, 0.5), (0.17, 0.92), (0, 0.98)])
        c.fill(place(stalk, x, y, s, rot=rot), 0)
        c.line(place(stalk, x, y, s, rot=rot), FINE * 1.1, closed=True)
        ring_y = 0.2
        c.line(place(spline([(-0.12, ring_y), (0, ring_y + 0.08), (0.12, ring_y)]), x, y, s, rot=rot), FINE)
        for i in range(-3, 4):
            c.line(place([(i * 0.03, 0.34), (i * 0.03, 0.46 + 0.05 * (i % 2))], x, y, s, rot=rot), FINE * 0.7)
        hood = spline([(-0.62, 0.05), (-0.56, -0.28), (-0.28, -0.6), (0, -0.68), (0.28, -0.6), (0.56, -0.28), (0.62, 0.05), (0, 0.13)], closed=True, steps=12)
        c.fill(place(hood, x, y, s, rot=rot), 0)
        c.line(place(hood, x, y, s, rot=rot), FINE * 1.2, closed=True)
        for i in range(-10, 11):
            c.line(place([(i * 0.055, 0.1 - abs(i) * 0.002), (i * 0.04, 0.02)], x, y, s, rot=rot), FINE * 0.7)
        for px, py, r in ((-0.32, -0.26, 0.09), (0.05, -0.44, 0.1), (0.36, -0.22, 0.07), (-0.05, -0.18, 0.06), (-0.26, -0.48, 0.045)):
            c.line(place(circle(px, py, r, 24), x, y, s, rot=rot), FINE * 0.8, closed=True)

    cap(0.42, 0.3, 0.72, 9)
    cap(-0.42, -0.1, 1.0, -7)
    cap(0.1, 0.5, 0.48, -2)
    ground = spline([(-0.92, 0.9), (-0.4, 0.84), (0.2, 0.92), (0.9, 0.84)])
    c.line(ground, FINE)
    for i in range(34):
        x = -0.9 + i * 0.054
        c.line([(x, 0.9), (x + rng.uniform(-0.04, 0.04), 0.9 - rng.uniform(0.05, 0.16))], taper(FINE * 0.9, FINE * 0.6, 0.002))


def wild_sprig_wreath(c, rng):
    c.line(arc(0, 0, 0.76, 8, 352, 110), FINE * 1.2)
    for i in range(30):
        a = 12 * i + 6
        p = polar(0.76, a)
        _fine_leaf(c, p[0], p[1], a + 42, 0.22, 0.09, veins=3)
        _fine_leaf(c, p[0], p[1], a + 142, 0.2, 0.08, veins=3)
    for a in range(0, 360, 60):
        x, y = polar(0.76, a)
        for i in range(5):
            c.fill(petal(x, y, 72 * i + a, 0.1, 0.075), 0)
            c.line(petal(x, y, 72 * i + a, 0.1, 0.075), FINE * 0.9, closed=True)
        c.disc(x, y, 0.016)
    for i in range(8):
        _fine_leaf(c, 0, 0, 45 * i, 0.24, 0.1, veins=2)
    c.disc(0, 0, 0.022)
    for i in range(16):
        c.disc(*polar(0.34, 22.5 * i), 0.008)


# --- 3. Madame Zircon Dotsworth: stippled mandalas, sacred geometry ----------


def _dot_shade(c, mask, rng, depth=0.1, gap=0.0125, r=0.0055, edge=1.05):
    field = mask.field()
    c.stipple(mask, lambda x, y: max(0.0, min(1.0, edge - field(x, y) / depth)), gap, r, rng)


def _petal_ring(c, rng, base, length, width, count, rot=0.0, depth=0.075):
    petals = [petal(*polar(base, rot + 360 * i / count), rot + 360 * i / count, length, width) for i in range(count)]
    mask = type(c)()
    for p in petals:
        mask.fill(p)
    _dot_shade(c, mask, rng, depth=depth)
    for p in petals:
        c.line(p, 0.012, closed=True)


def _dot_ring(c, r, count, size, rot=0.0):
    for i in range(count):
        c.disc(*polar(r, rot + 360 * i / count), size)


def lotus_mandala(c, rng):
    _petal_ring(c, rng, 0.72, 0.28, 0.2, 24, 7.5)
    c.ring(0, 0, 0.73, 0.014)
    _dot_ring(c, 0.685, 48, 0.011)
    _petal_ring(c, rng, 0.38, 0.28, 0.2, 16, 0)
    c.ring(0, 0, 0.385, 0.014)
    _dot_ring(c, 0.345, 30, 0.009)
    _petal_ring(c, rng, 0.1, 0.22, 0.13, 8, 22.5)
    c.fill(circle(0, 0, 0.11))
    c.fill(circle(0, 0, 0.05), 0)
    c.ring(0, 0, 0.99, 0.014)


def sun_wheel(c, rng):
    for i in range(28):
        a = i * 360 / 28
        c.fill(leaf(*polar(0.55, a), a, 0.46 if i % 2 else 0.32, 0.075 if i % 2 else 0.05))
    disc = c.mask_of(circle(0, 0, 0.54))
    c.stipple(disc, lambda x, y: min(1.0, max(0.0, math.hypot(x, y) / 0.54) ** 2.2 + 0.03), 0.012, 0.0055, rng)
    c.ring(0, 0, 0.55, 0.018)
    for r, n, size in ((0.48, 44, 0.009), (0.41, 36, 0.008)):
        _dot_ring(c, r, n, size)
    for i in range(12):
        a = i * 30
        tri = [polar(0.32, a - 13), polar(0.32, a + 13), polar(0.12, a)]
        c.fill(tri, 0)
        c.line(tri, 0.012, closed=True)
    c.fill(circle(0, 0, 0.13))
    for i in range(8):
        c.disc(*polar(0.085, 45 * i), 0.012, 0)


def flower_of_life(c, rng):
    r = 0.33
    centres = [(0, 0)] + [polar(r, 60 * i) for i in range(6)]
    petals = []
    for x, y in centres:
        for i in range(6):
            petals.append(leaf(x, y, 60 * i, r, r * 0.58, steps=20, belly=0.5))
    mask = type(c)()
    for p in petals:
        mask.fill(p)
    c.stipple(mask, lambda x, y: 0.12 + 0.88 * (math.hypot(x, y) / 0.68) ** 1.4, 0.0115, 0.0055, rng)
    for p in petals:
        c.line(p, 0.012, closed=True)
    for x, y in centres:
        c.disc(x, y, 0.02)
    c.ring(0, 0, r * 2.45, 0.02)
    c.ring(0, 0, r * 2.38, 0.008)
    for i in range(36):
        a = i * 10
        c.fill(leaf(*polar(r * 2.47, a), a, 0.14 if i % 3 else 0.2, 0.04))


def sri_triangles(c, rng):
    tri = []
    for r, rot in ((0.92, 0), (0.92, 180), (0.72, 0), (0.72, 180), (0.5, 0), (0.5, 180), (0.28, 0)):
        tri.append(ngon(0, 0.04 if rot == 0 else -0.04, r, 3, rot))
    stip = c.mask_of(tri[:6])
    field = stip.field()
    c.stipple(stip, lambda x, y: min(1.0, 1.0 - field(x, y) / 0.14) if field(x, y) < 0.14 else 0.0, 0.011, 0.005, rng)
    for t in tri:
        c.line(t, 0.015, closed=True)
    c.fill(tri[-1])
    c.disc(0, 0.04, 0.05, 0)
    c.ring(0, 0, 0.99, 0.016)
    c.ring(0, 0, 0.955, 0.007)


def moon_mandala(c, rng):
    phases = [(-0.56, 0.3), (-0.3, 0.18), (0.3, 0.18), (0.56, 0.3)]
    disc = circle(0, 0, 0.42)
    c.stipple(c.mask_of(disc), lambda x, y: max(0.0, min(1.0, (x * 0.7 + y * 0.7) / 0.42 + 0.62)), 0.0115, 0.0052, rng)
    c.line(disc, 0.018, closed=True)
    for i in range(24):
        a = i * 15
        c.line([polar(0.48, a), polar(0.56 if i % 2 else 0.61, a)], taper(0.02, 0.012, 0.002))
    c.ring(0, 0, 0.455, 0.008)
    for i in range(8):
        a = 22.5 + 45 * i
        x, y = polar(0.76, a)
        size = 0.13
        m = [circle(x, y, size, 50)]
        offset = polar(size * (0.5 if i % 2 else 0.9), a + 90, x, y)
        c.fill(m[0])
        c.fill(circle(offset[0], offset[1], size * 0.92, 50), 0)
        c.line(m[0], 0.012, closed=True)
    for i in range(8):
        a = 45 * i
        x, y = polar(0.78, a)
        c.fill(star(x, y, 0.1, 0.022, 4, rot=a))
        c.disc(*polar(0.65, a), 0.012)
    c.ring(0, 0, 0.985, 0.018)
    _dot_ring(c, 0.945, 90, 0.008)


def stippled_orb(c, rng):
    for i in range(3):
        c.line(place(circle(0, 0, 0.96 - i * 0.02, 160, ry=0.24), rot=i * 60 + 30), 0.012, closed=True)
    orb = circle(0, 0, 0.56)
    c.fill(orb, 0)
    c.stipple(c.mask_of(orb), lambda x, y: min(1.0, max(0.0, math.hypot(x + 0.2, y + 0.24) / 0.62) ** 1.8), 0.0105, 0.005, rng)
    c.line(orb, 0.016, closed=True)
    for i in range(3):
        back = [(p[0] * 0.96, p[1] * 0.24) for p in arc(0, 0, 1, 90, 270, 60)]
        c.line(place(back, rot=i * 60 + 30), 0.012)
    for i in range(6):
        c.disc(*polar(0.96, i * 60 + 90 + 30), 0.03)
    for i in range(14):
        x, y = polar(rng.uniform(0.74, 0.97), rng.uniform(0, 360))
        c.fill(star(x, y, 0.028, 0.008, 4))


# --- 4. Captain Inkbeard: traditional flash, thick lines, whip shading ------

BOLD = 0.034


def _whip(c, contour, rng, keep=None, length=0.2, every=0.024, width=0.024):
    c.whip(contour, c.mask_of(contour), width, length, every, rng, keep)


def swallow(c, rng):
    def turned(pts):
        return place(pts, 0.02, 0.0, 0.86, rot=-22)

    wing = spline([(0.08, -0.26), (0.34, -0.5), (0.72, -0.66), (1.08, -0.64), (0.8, -0.26), (0.46, 0.0), (0.1, 0.12)], closed=True)
    band = spline([(0.08, -0.26), (0.34, -0.5), (0.72, -0.66), (1.08, -0.64), (0.72, -0.5), (0.36, -0.28), (0.12, -0.08)], closed=True)
    tail = [(0.03, 0.1), (0.14, 0.38), (0.44, 1.0), (0.14, 0.62), (0.0, 0.42)]
    body = sym([(0, -0.62), (0.1, -0.56), (0.17, -0.34), (0.19, -0.06), (0.12, 0.26), (0, 0.42)])
    head = sym([(0, -0.62), (0.1, -0.56), (0.17, -0.34), (0.15, -0.2), (0, -0.14)])
    for shape in (tail, mirror(tail)):
        c.shape(turned(shape), BOLD, solid=True)
    for flip in (1, -1):
        def side(pts):
            return turned(pts if flip > 0 else mirror(pts))
        whole = side(wing)
        c.shape(whole, BOLD)
        layer = type(c)()
        for i in range(8):
            t = i / 8
            start = side([(0.14 + t * 0.7, -0.14 - t * 0.42)])[0]
            end = side([(0.1 + t * 0.48, 0.18 - t * 0.2)])[0]
            layer.line([start, end], taper(0.024, 0.018, 0.002))
        c.stamp(layer, c.mask_of(whole))
        c.fill(side(band))
    c.shape(turned(body), BOLD)
    c.stamp(_flicks(c, [(0, -0.1), (0, 0.32)], turned), c.mask_of(turned(body)))
    c.fill(turned(head))
    for ex in (0.08, -0.08):
        x, y = turned([(ex, -0.42)])[0]
        c.fill(circle(x, y, 0.026, 24), 0)
    c.fill(turned([(-0.05, -0.6), (0.05, -0.6), (0, -0.73)]))
    for x, y, s in ((-0.78, -0.72, 0.13), (0.8, 0.5, 0.1), (0.82, 0.86, 0.06), (-0.72, 0.76, 0.08)):
        c.fill(star(x, y, s, s * 0.42, 5))


def _flicks(c, spine, turned):
    layer = type(c)()
    for t in range(9):
        y = spine[0][1] + (spine[1][1] - spine[0][1]) * t / 9
        for sx in (1, -1):
            layer.line(turned([(sx * 0.2, y), (sx * 0.05, y + 0.08)]), taper(0.02, 0.012, 0.002))
    return layer


def lucky_anchor(c, rng):
    shaft = [(0, -0.6), (0, 0.84)]
    stock = [(-0.42, -0.42), (0.42, -0.42)]
    arms = spline([(-0.76, 0.3), (-0.62, 0.62), (-0.3, 0.86), (0, 0.92), (0.3, 0.86), (0.62, 0.62), (0.76, 0.3)], steps=12)
    ring = circle(0, -0.76, 0.14, 60)
    paths = (shaft, stock, arms)
    widths = (0.15, 0.1, 0.12)
    c.line(ring, 0.1, closed=True)
    for p, w in zip(paths, widths):
        c.line(p, w + BOLD * 2)
    for sx in (-1, 1):
        fluke = [(sx * 0.98, 0.42), (sx * 0.78, 0.04), (sx * 0.56, 0.4), (sx * 0.72, 0.36)]
        c.fill(fluke)
        c.line(fluke, BOLD, closed=True)
        c.fill(star(sx * 0.42, -0.42, 0.075, 0.03, 4))
    c.line(ring, 0.1 - BOLD * 1.4, ink=0, closed=True)
    for p, w in zip(paths, widths):
        c.line(p, w, 0)
    for sx in (-1, 1):
        fluke = [(sx * 0.9, 0.38), (sx * 0.78, 0.13), (sx * 0.64, 0.36)]
        c.fill(fluke, 0)
    layer = type(c)()
    for y in range(-30, 44):
        layer.line([(0.0, y * 0.021), (0.1, y * 0.021 + 0.03)], taper(0.016, 0.012, 0.002))
    c.stamp(layer, c.mask_of(ribbon(shaft, lambda t: 0.15)))
    layer = type(c)()
    for i, p in enumerate(resample(arms, 30)):
        layer.line([p, (p[0] * 0.92, p[1] * 0.86)], taper(0.016, 0.012, 0.002))
    c.stamp(layer, c.mask_of(ribbon(arms, lambda t: 0.12)))
    rope_path = [(0.0, -0.62), (0.34, -0.5), (-0.28, -0.2), (0.3, 0.08), (-0.24, 0.32), (0.24, 0.54), (0.42, 0.9), (0.68, 0.76)]
    rope = spline(rope_path, steps=18)
    c.line(rope, 0.078 + BOLD)
    c.line(rope, 0.078, 0)
    for p in resample(rope, 42):
        c.line([(p[0] - 0.03, p[1] - 0.026), (p[0] + 0.03, p[1] + 0.026)], 0.012)


def dagger_heart(c, rng):
    blade = [(-0.085, -0.62), (0.085, -0.62), (0.09, 0.3), (0, 1.0), (-0.09, 0.3)]
    c.shape(blade, BOLD * 0.8)
    c.line([(0.0, -0.6), (0.0, 0.82)], 0.018)
    heart = place(HEART, 0, 0.1, 0.62)
    c.shape(heart, BOLD)
    _whip(c, heart, rng, keep=lambda x, y: x + (y - 0.1) * 0.45 > 0.04, length=0.26, every=0.021)
    c.fill(spline([(-0.42, -0.04), (-0.38, -0.2), (-0.22, -0.3), (-0.28, -0.18), (-0.34, -0.02)], closed=True))
    guard = [(-0.34, -0.72), (0.34, -0.72), (0.4, -0.66), (0.34, -0.6), (-0.34, -0.6), (-0.4, -0.66)]
    c.shape(guard, BOLD * 0.8, solid=True)
    c.disc(-0.42, -0.66, 0.045)
    c.disc(0.42, -0.66, 0.045)
    grip = [(-0.06, -0.98), (0.06, -0.98), (0.07, -0.72), (-0.07, -0.72)]
    c.shape(grip, BOLD * 0.8)
    for i in range(5):
        y = -0.95 + i * 0.045
        c.line([(-0.065, y), (0.065, y + 0.03)], 0.014)
    c.fill(circle(0, -1.03, 0.07, 40))
    for x, y, s in ((0.3, 0.72, 1.0), (0.46, 0.46, 0.72), (-0.34, 0.76, 0.8)):
        c.fill(place(sym([(0, -0.12), (0.04, -0.02), (0.05, 0.03), (0, 0.08)]), x, y, s))
    c.fill(star(-0.74, 0.5, 0.1, 0.04, 5))
    c.fill(star(0.78, 0.8, 0.08, 0.03, 5))
    c.fill(star(0.72, -0.56, 0.08, 0.03, 5))


def rose_layers(c, x, y, s, rng, w=BOLD, whip=True):
    """A traditional rose: rings of cupped petals around a spiral heart."""

    def cup(a, inner, outer, spread):
        return spline(
            [polar(s * inner, a - spread * 0.9, x, y), polar(s * outer * 0.92, a - spread, x, y), polar(s * outer, a - spread * 0.45, x, y),
             polar(s * outer * 1.03, a, x, y), polar(s * outer, a + spread * 0.45, x, y), polar(s * outer * 0.92, a + spread, x, y), polar(s * inner, a + spread * 0.9, x, y)],
            closed=True)

    for inner, outer, spread, angles, reach in (
        (0.3, 1.04, 46, (18, 90, 162, 234, 306), 0.62),
        (0.18, 0.76, 42, (54, 126, 198, 270, 342), 0.44),
        (0.1, 0.5, 52, (0, 120, 240), 0.2),
    ):
        for a in angles:
            shape = cup(a, inner, outer, spread)
            c.shape(shape, w)
            if whip:
                c.whip(shape, c.mask_of(shape), w * 0.75, s * 0.28, s * 0.05, rng,
                       keep=lambda px, py, r=reach: math.hypot(px - x, py - y) < s * r)
    c.fill(circle(x, y, s * 0.22, 40))
    c.line(curl(*polar(s * 0.2, 200, x, y), 110, s * 0.72, 620), taper(w * 0.5, w * 0.6, w * 0.2), 0)


def bold_rose(c, rng):
    for a, l, w in ((222, 1.04, 0.46), (140, 1.0, 0.44), (40, 1.04, 0.46), (312, 0.92, 0.4), (90, 0.84, 0.36), (272, 0.82, 0.34)):
        contour = leaf(*polar(0.42, a), a, l - 0.36, w)
        c.shape(contour, BOLD)
        layer = type(c)()
        layer.fill([polar(0.42, a), polar(l + 0.06, a), polar(0.5, a + 90, *polar(0.7, a))])
        c.stamp(layer, c.mask_of(contour))
        c.line([polar(0.42, a), polar(l - 0.04, a)], 0.02)
        for i in range(1, 5):
            base = polar(0.42 + (l - 0.44) * i / 5, a)
            c.line([base, polar(0.12 * math.sin(i / 5 * 3.14 + 0.2), a - 44, *base)], taper(0.016, 0.012, 0.002))
    rose_layers(c, 0, 0, 0.64, rng)


def lucky_horseshoe(c, rng):
    spine = spline([(-0.3, 0.8), (-0.52, 0.3), (-0.62, -0.2), (-0.42, -0.62), (0, -0.76), (0.42, -0.62), (0.62, -0.2), (0.52, 0.3), (0.3, 0.8)], steps=16)
    shoe = ribbon(spine, lambda t: 0.3)
    c.shape(shoe, BOLD)
    c.line(spine[:6] + spine[6:], 0.02)
    mask = c.mask_of(shoe)
    layer = type(c)()
    for p in resample(spine, 70):
        layer.line([(p[0] * 1.27, p[1] * 1.2), (p[0] * 1.06, p[1] * 1.06 + 0.02)], taper(0.024, 0.016, 0.002))
    c.stamp(layer, mask)
    for t in (0.1, 0.22, 0.34, 0.66, 0.78, 0.9):
        p = spine[int(t * (len(spine) - 1))]
        c.fill(circle(p[0], p[1], 0.05, 20), 0)
        c.ring(p[0], p[1], 0.05, 0.022)
    for sx in (-1, 1):
        cap = ngon(sx * 0.3, 0.9, 0.17, 4, 45)
        c.shape(cap, BOLD, solid=True)
    c.shape(star(0, -0.08, 0.34, 0.14, 5), BOLD, solid=True)
    c.fill(star(0, -0.08, 0.16, 0.06, 5), 0)
    for x, y, s in ((-0.2, 0.42, 0.1), (0.2, 0.42, 0.1), (0, 0.72, 0.12), (-0.86, -0.72, 0.1), (0.88, -0.72, 0.1)):
        c.fill(star(x, y, s, s * 0.4, 5))


def rattler_coil(c, rng):
    def fit(pts):
        return place(pts, 0.0, 0.1, 0.84)

    spine = spline(
        [(-0.86, 0.72), (-0.42, 0.94), (0.42, 0.9), (0.84, 0.48), (0.36, 0.2), (-0.5, 0.26), (-0.78, -0.08), (-0.34, -0.36), (0.3, -0.26), (0.52, -0.52), (0.28, -0.78)],
        steps=22,
    )
    width = lambda t: 0.05 + 0.25 * math.sin(math.pi * min(t * 1.25, 1.0) ** 0.8) ** 0.7 + 0.06 * t
    pts = resample(fit(spine), 120)
    c.line(pts, lambda t: width(t) + BOLD * 2)
    c.line(pts, width, 0)
    for i in range(14, 116, 4):
        c.fill(ngon(pts[i][0], pts[i][1], width(i / 119) * 0.32, 4, rot=i * 3))
    head = spline([(0.0, -0.26), (0.13, -0.16), (0.28, 0.02), (0.18, 0.2), (-0.18, 0.2), (-0.28, 0.02), (-0.13, -0.16)], closed=True)
    hx, hy = fit([(0.27, -0.84)])[0]
    c.shape(place(head, hx, hy, 0.95, rot=-8), BOLD, solid=True)
    for ex in (-0.1, 0.1):
        c.fill(circle(hx + ex, hy - 0.03, 0.03, 24), 0)
        c.disc(hx + ex, hy - 0.03, 0.012)
    tx, ty = hx - 0.035, hy - 0.25
    c.line([(tx, ty), (tx - 0.01, ty - 0.1)], 0.018)
    c.line([(tx - 0.01, ty - 0.09), (tx - 0.07, ty - 0.14)], 0.013)
    c.line([(tx - 0.01, ty - 0.09), (tx + 0.05, ty - 0.14)], 0.013)
    ax, ay = pts[0]
    for i in range(4):
        c.fill(circle(ax - 0.03 - i * 0.04, ay - 0.03 - i * 0.06, 0.042 - i * 0.004, 24))
        c.ring(ax - 0.03 - i * 0.04, ay - 0.03 - i * 0.06, 0.05 - i * 0.004, 0.01, 0)
    c.fill(star(0.76, -0.46, 0.11, 0.045, 5))
    c.fill(star(-0.72, -0.5, 0.09, 0.036, 5))


# --- 5. Filigree Von Curlicue: symmetric scrollwork and lace, tapered curls --


def _scroll(c, x, y, a, size, turn=560.0, sign=1, w=0.024):
    for flip in (False, True):
        pts = curl(x, y, a, size, turn, sign)
        pts = mirror(pts) if flip else pts
        c.line(pts, taper(w * 0.7, w, 0.006, 0.25))
        c.disc(pts[-1][0], pts[-1][1], w * 0.55)


def _bud(c, x, y, a, l=0.14, w=0.07, solid=True):
    for flip in (1, -1):
        contour = leaf(flip * x, y, flip * a, l, w)
        c.shape(contour, 0.012, solid=solid)


def _beads(c, spine, count, r):
    for x, y in resample(spine, count):
        c.disc(x, y, r)
        c.disc(-x, y, r)


def damask_medallion(c, rng):
    c.line(sym([(0, -1.0), (0.5, -0.62), (0.78, -0.08), (0.7, 0.42), (0.3, 0.82), (0, 1.0)]), 0.03, closed=True)
    c.line(sym([(0, -0.92), (0.45, -0.57), (0.71, -0.08), (0.63, 0.39), (0.27, 0.75), (0, 0.91)]), 0.008, closed=True)
    _scroll(c, 0.02, 0.56, 62, 0.9, 500, -1)
    _scroll(c, 0.02, 0.1, 52, 0.84, 540, -1)
    _scroll(c, 0.02, 0.1, 128, 0.62, 500, 1)
    _scroll(c, 0.02, -0.34, 44, 0.66, 500, -1)
    _scroll(c, 0.02, -0.6, 40, 0.34, 500, -1, w=0.018)
    c.line([(0, -0.82), (0, 0.8)], taper(0.006, 0.026, 0.006))
    for y, s in ((-0.75, 0.13), (-0.42, 0.07), (0.1, 0.09), (0.5, 0.07), (0.82, 0.05)):
        c.fill(ngon(0, y, s, 4))
        c.fill(ngon(0, y, s * 0.45, 4), 0)
    _bud(c, 0.02, -0.5, 58, 0.2, 0.09)
    _bud(c, 0.02, 0.28, 108, 0.24, 0.1)
    for sx in (-1, 1):
        for i in range(5):
            c.disc(sx * (0.85 + 0.008 * i), -0.2 + 0.12 * i - 0.01 * i * i, 0.016)
        c.fill(leaf(sx * 0.7, -0.74, sx * 40, 0.2, 0.09))
        c.fill(leaf(sx * 0.54, 0.8, sx * 140, 0.2, 0.09))


def lace_collar(c, rng):
    top = spline([(-0.92, -0.78), (-0.5, -0.5), (0, -0.4), (0.5, -0.5), (0.92, -0.78)], steps=16)
    bottom = spline([(-0.98, -0.28), (-0.56, 0.2), (0, 0.42), (0.56, 0.2), (0.98, -0.28)], steps=18)
    c.line(top, 0.036)
    c.line(bottom, 0.02)
    pts = resample(bottom, 19)
    tops = resample(top, 19)
    for i, p in enumerate(pts):
        q = tops[i]
        c.line([q, p], 0.008)
        if i < len(pts) - 1:
            n = pts[i + 1]
            mid = ((p[0] + n[0]) / 2, (p[1] + n[1]) / 2)
            c.line(arc(mid[0], mid[1], 0.06, 90, 270, 16)[::1], 0.012)
            c.line(place(leaf(0, 0, 180, 0.2, 0.09), mid[0], mid[1] + 0.03), 0.012, closed=True)
            c.disc(mid[0], mid[1] + 0.11, 0.018)
            c.disc(mid[0], mid[1] + 0.27, 0.014)
            r = tops[i + 1]
            hub = ((mid[0] * 2 + (q[0] + r[0]) / 2) / 3, (mid[1] * 2 + (q[1] + r[1]) / 2) / 3)
            c.ring(hub[0], hub[1], 0.05, 0.012)
            for k in range(8):
                c.line([polar(0.012, 45 * k, *hub), polar(0.05, 45 * k, *hub)], 0.006)
            c.disc(hub[0], hub[1], 0.012)
    for i in range(18):
        q, r = tops[i], tops[i + 1]
        c.line(arc((q[0] + r[0]) / 2, (q[1] + r[1]) / 2 + 0.02, 0.05, 110, 250, 12), 0.01)
    for t in resample(top, 24):
        c.disc(t[0], t[1] - 0.05, 0.012)
    c.fill(ngon(0, 0.62, 0.17, 4))
    c.fill(circle(0, 0.62, 0.09, 30), 0)
    c.disc(0, 0.62, 0.05)
    c.fill(leaf(0, 0.76, 180, 0.2, 0.08))


def empty_cartouche(c, rng):
    frame = sym([(0, -0.72), (0.2, -0.66), (0.42, -0.56), (0.52, -0.3), (0.56, 0.0), (0.5, 0.32), (0.34, 0.56), (0.14, 0.66), (0, 0.7)])
    c.line(frame, 0.042, closed=True)
    c.line(place(frame, s=0.9), 0.01, closed=True)
    _scroll(c, 0.3, -0.62, 62, 0.72, 620, 1, 0.032)
    _scroll(c, 0.5, -0.4, 100, 0.56, 560, 1, 0.028)
    _scroll(c, 0.55, 0.2, 130, 0.6, 560, -1, 0.03)
    _scroll(c, 0.3, 0.6, 110, 0.58, 590, -1, 0.03)
    _scroll(c, 0.04, -0.75, 20, 0.42, 620, -1, 0.024)
    _scroll(c, 0.05, 0.72, 160, 0.34, 590, 1, 0.022)
    c.fill(leaf(0, -0.68, 0, 0.32, 0.16))
    c.fill(leaf(0, 0.66, 180, 0.3, 0.14))
    _bud(c, 0.5, -0.5, 60, 0.26, 0.1)
    _bud(c, 0.55, 0.42, 120, 0.26, 0.1)
    _bud(c, 0.14, -0.74, 70, 0.2, 0.07)
    for r in resample(place(frame, s=0.8), 56, closed=True):
        c.disc(r[0], r[1], 0.009)


def chandelier_drop(c, rng):
    c.line([(0, -1.02), (0, -0.2)], taper(0.012, 0.024, 0.012))
    for y, r in ((-0.98, 0.04), (-0.78, 0.06), (-0.5, 0.075), (-0.18, 0.11)):
        c.fill(circle(0, y, r, 40))
        c.ring(0, y, r * 0.5, 0.006, 0)
    for x, y, cup in ((0.92, -0.12, 0.14), (0.58, -0.42, 0.11), (0.32, -0.66, 0.08)):
        arm = spline([(0, y + 0.3), (x * 0.42, y + 0.34), (x * 0.82, y + 0.22), (x, y)], steps=14)
        c.line(arm, taper(0.018, 0.024, 0.012))
        c.line(mirror(arm), taper(0.018, 0.024, 0.012))
        _scroll(c, x * 0.5, y + 0.36, 150, 0.28, 420, 1, 0.014)
        for sx in (-1, 1):
            c.fill(place(sym([(0, -0.5), (0.7, -0.5), (0.45, 0.1), (0.1, 0.32), (0, 0.32)]), sx * x, y, cup))
            c.line([(sx * x, y - cup * 0.45), (sx * x, y - cup * 1.6)], 0.018)
            c.fill(leaf(sx * x, y - cup * 1.6, 0, cup * 1.0, cup * 0.48))
            for k in range(3):
                dx = -cup * 0.6 + cup * 0.6 * k
                c.line([(sx * x + dx, y + cup * 0.28), (sx * x + dx, y + cup * 0.7 + 0.06)], 0.006)
                c.fill(leaf(sx * x + dx, y + cup * 0.7 + 0.06, 180, 0.09, 0.05))
    swag = spline([(-0.92, 0.06), (-0.46, 0.5), (0, 0.32), (0.46, 0.5), (0.92, 0.06)], steps=20)
    for p in resample(swag, 40):
        c.disc(p[0], p[1], 0.012)
    c.line([(0, 0.18), (0, 0.5)], 0.016)
    c.fill(ngon(0, 0.68, 0.17, 4))
    c.fill(circle(0, 0.68, 0.09, 30), 0)
    c.disc(0, 0.68, 0.05)
    c.fill(leaf(0, 0.82, 180, 0.18, 0.08))


def wrought_gate(c, rng):
    for inset, w in ((0, 0.036), (0.09, 0.012)):
        outline = [(-0.76 + inset, 1.0 - inset * 0.3)] + arc(0, -0.2, 0.76 - inset, 270, 450, 50) + [(0.76 - inset, 1.0 - inset * 0.3)]
        c.line(outline, w, closed=True)
    c.line([(0, -0.84), (0, 0.92)], 0.02)
    _scroll(c, 0.03, -0.14, 50, 0.92, 640, -1, 0.026)
    _scroll(c, 0.03, -0.18, 130, 0.6, 520, 1, 0.02)
    _scroll(c, 0.03, 0.42, 50, 0.9, 640, -1, 0.026)
    _scroll(c, 0.03, 0.36, 130, 0.48, 520, 1, 0.02)
    _scroll(c, 0.03, 0.86, 44, 0.42, 500, -1, 0.02)
    _scroll(c, 0.03, -0.54, 62, 0.46, 520, -1, 0.02)
    for y in (-0.6, -0.16, 0.38, 0.84):
        c.fill(ngon(0, y, 0.06, 4))
    c.fill(leaf(0, -0.96, 0, 0.1, 0.09))
    for p in arc(0, -0.2, 0.82, 278, 442, 18):
        c.fill(leaf(p[0], p[1], math.degrees(math.atan2(p[0], -(p[1] + 0.2))), 0.08, 0.04))
    for sx in (-1, 1):
        c.fill(ngon(sx * 0.76, 1.0, 0.08, 4))
        c.fill(ngon(sx * 0.76, -0.2, 0.07, 4))


def spade_finial(c, rng):
    spade = sym([(0, -1.0), (0.28, -0.56), (0.76, -0.14), (0.72, 0.28), (0.34, 0.36), (0.1, 0.2), (0.18, 0.72), (0.3, 0.92), (0, 0.92)])
    c.line(spade, 0.038, closed=True)
    c.line(place(spade, 0, 0.0, 0.93), 0.008, closed=True)
    _scroll(c, 0.02, 0.2, 58, 0.92, 640, -1, 0.026)
    _scroll(c, 0.02, -0.14, 44, 0.6, 620, -1, 0.022)
    _scroll(c, 0.02, -0.46, 32, 0.28, 520, -1, 0.016)
    c.line([(0, -0.8), (0, 0.8)], taper(0.006, 0.024, 0.006))
    _bud(c, 0.02, 0.28, 120, 0.22, 0.08)
    for y, s in ((-0.74, 0.06), (0.04, 0.09), (0.58, 0.06), (0.8, 0.045)):
        c.fill(ngon(0, y, s, 4))
    for sx in (-1, 1):
        for i in range(6):
            c.disc(sx * (0.86 + 0.02 * i), 0.04 - i * 0.09, 0.012 + i * 0.002)
        c.fill(leaf(sx * 0.24, 0.84, sx * 90, 0.34, 0.09))


