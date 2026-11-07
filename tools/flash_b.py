"""Stand-in tattoo designs, part two. Each function draws one design."""

import math

from flash_a import HEART, NOSE, SKULL, SOCKET, curl
from ink import (
    Canvas,
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

def crescent(x, y, r, shift, theta):
    """A moon with its horns to the right, at compass angles theta and 180 - theta.

    shift moves the cutting circle right: the larger, the fatter the moon.
    """
    px, py = r * math.sin(math.radians(theta)), r * math.cos(math.radians(theta))
    radius = math.hypot(px - shift, py)
    horn = math.degrees(math.atan2(px - shift, py))
    return arc(x, y, r, theta, -180 - theta, 70) + arc(x + shift, y, radius, 180 - horn, 360 + horn, 50)[1:-1]


# --- 6. Blackfang Zuzubar: tribal, solid flowing blades with sharp tips ------


def _blade(c, pts, w, at=0.4, ink=1):
    c.line(pts, taper(0.003, w, 0.002, at), ink)


def _both(c, pts, w, at=0.4):
    _blade(c, spline(pts, steps=14), w, at)
    _blade(c, spline(mirror(pts), steps=14), w, at)


def tribal_sun(c, rng):
    for i in range(10):
        a = 36 * i
        _blade(c, curl(*polar(0.3, a), a + 42, 0.8, 100, 1), 0.17, 0.3)
        _blade(c, curl(*polar(0.34, a + 18), a + 82, 0.44, 140, -1), 0.08, 0.3)
    c.fill([circle(0, 0, 0.27, 90), circle(0, 0, 0.17, 70)])
    c.fill(star(0, 0, 0.13, 0.05, 5))


def hook_spiral(c, rng):
    spiral = []
    for i in range(160):
        t = i / 159
        spiral.append(polar(0.98 * (1 - t) ** 0.85 + 0.04, 40 + 800 * t))
    width = lambda t: 0.015 + 0.27 * math.sin(math.pi * min(t * 1.5 + 0.02, 1)) ** 0.8 * (1 - t * 0.5)
    c.line(spiral, width)
    for i in range(12, 130, 13):
        a, b = spiral[i - 1], spiral[i + 1]
        heading = math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1])))
        p = spiral[i]
        half = width(i / 159) * 0.45
        outward = polar(1.0, heading - 90)
        size = 0.16 * (1 - i / 170) + 0.05
        hook = spline([(p[0] + outward[0] * half, p[1] + outward[1] * half),
                       polar(size * 0.6, heading - 62, p[0] + outward[0] * half, p[1] + outward[1] * half),
                       polar(size, heading - 18, p[0] + outward[0] * half, p[1] + outward[1] * half)], steps=8)
        _blade(c, hook, 0.09 * (1 - i / 200), 0.05)


def fang_heart(c, rng):
    _both(c, [(0.02, 0.98), (0.3, 0.46), (0.82, 0.02), (0.92, -0.52), (0.56, -0.86), (0.2, -0.68), (0.06, -0.2)], 0.22, 0.45)
    _both(c, [(0.04, 0.36), (0.26, 0.2), (0.58, -0.1), (0.62, -0.46), (0.38, -0.56)], 0.1, 0.45)
    for sx in (-1, 1):
        _blade(c, spline([(sx * 0.8, 0.06), (sx * 1.02, 0.18), (sx * 1.06, 0.46)]), 0.09, 0.15)
        _blade(c, spline([(sx * 0.46, 0.42), (sx * 0.74, 0.5), (sx * 0.84, 0.82)]), 0.09, 0.15)
        _blade(c, spline([(sx * 0.3, -0.76), (sx * 0.36, -0.96), (sx * 0.6, -1.06)]), 0.08, 0.15)
        _blade(c, spline([(sx * 0.82, -0.62), (sx * 1.0, -0.72), (sx * 1.04, -0.92)]), 0.08, 0.15)
    c.fill(sym([(0, -0.24), (0.1, -0.08), (0.08, 0.1), (0, 0.24)]))


def twin_flames(c, rng):
    _both(c, [(0.02, 1.0), (0.36, 0.68), (0.52, 0.24), (0.3, -0.26), (0.46, -0.66), (0.26, -1.0)], 0.27, 0.4)
    _both(c, [(0.14, 0.56), (0.66, 0.5), (0.88, 0.12), (0.74, -0.24), (0.9, -0.56)], 0.2, 0.42)
    _both(c, [(0.02, 0.34), (0.14, 0.06), (0.05, -0.32), (0.14, -0.72)], 0.1, 0.4)
    _both(c, [(0.44, 0.92), (0.72, 0.84), (0.98, 0.56)], 0.12, 0.3)
    _both(c, [(0.6, -0.04), (0.52, -0.3), (0.62, -0.66)], 0.07, 0.3)


def manta_glide(c, rng):
    wing = spline([(0.08, -0.5), (0.5, -0.5), (1.04, -0.14), (0.68, -0.08), (0.34, 0.26), (0.08, 0.34)], closed=True, steps=12)
    for shape in (wing, mirror(wing)):
        c.fill(shape)
    c.fill(sym([(0, -0.62), (0.16, -0.56), (0.2, -0.1), (0.14, 0.36), (0, 0.6)]))
    c.line([(0, 0.5), (0, 1.04)], taper(0.05, 0.03, 0.002))
    for sx in (-1, 1):
        _blade(c, spline([(sx * 0.14, -0.58), (sx * 0.2, -0.8), (sx * 0.08, -0.96)]), 0.09, 0.15)
        for s, y0 in ((0.86, -0.2), (0.62, -0.06)):
            _blade(c, spline([(sx * s * 0.34, y0 + 0.02), (sx * s * 0.68, y0 - 0.03), (sx * s, y0 - 0.1)]), 0.05, 0.4)
            c.line(spline([(sx * s * 0.34, y0 - 0.02), (sx * s * 0.68, y0 - 0.08), (sx * s, y0 - 0.14)]), taper(0.002, 0.036, 0.002), 0)
        c.line(spline([(sx * 0.16, -0.36), (sx * 0.6, -0.34), (sx * 0.94, -0.2)]), taper(0.002, 0.04, 0.002), 0)
        _blade(c, spline([(sx * 0.3, 0.3), (sx * 0.5, 0.42), (sx * 0.56, 0.72)]), 0.12, 0.15)
        _blade(c, spline([(sx * 0.15, 0.48), (sx * 0.26, 0.62), (sx * 0.26, 0.92)]), 0.09, 0.15)
        _blade(c, spline([(sx * 0.68, -0.02), (sx * 0.84, 0.12), (sx * 0.88, 0.42)]), 0.1, 0.15)
        c.disc(sx * 0.08, -0.44, 0.02, 0)


# --- 7. Old Quillon Burinsnout: engraved swelling parallel lines -------------

ENGRAVE = 0.019


def _engrave(c, contour, degrees, gap, shade, wobble=None, outline=0.02):
    c.fill(contour, 0)
    c.hatch(c.mask_of(contour), degrees, gap, ENGRAVE, wobble=wobble, swell=lambda x, y: max(0.0, shade(x, y)))
    if outline:
        c.line(contour, outline, closed=True)


def sperm_whale(c, rng):
    body = spline([(-0.98, -0.1), (-0.92, -0.44), (-0.5, -0.56), (0.02, -0.5), (0.5, -0.22), (0.86, -0.1), (0.94, -0.06), (0.8, 0.02), (0.4, 0.2), (-0.1, 0.3), (-0.56, 0.3), (-0.7, 0.18), (-0.96, 0.1)], closed=True, steps=14)
    wave = lambda x, y: 0.12 * math.sin((x + 0.4) * 1.9)
    _engrave(c, body, 90, 0.032, lambda x, y: 0.12 + (y + 0.5) * 1.15 + 0.2 * max(0.0, x), wobble=wave)
    tail = spline([(0.84, -0.06), (0.98, -0.2), (1.06, -0.52), (0.88, -0.36), (0.76, -0.46), (0.82, -0.2)], closed=True)
    _engrave(c, tail, 30, 0.024, lambda x, y: 0.55)
    fin = spline([(-0.34, 0.26), (-0.22, 0.56), (-0.02, 0.62), (-0.08, 0.28)], closed=True)
    _engrave(c, fin, 20, 0.024, lambda x, y: 0.75)
    c.line(spline([(-0.96, 0.1), (-0.68, 0.07), (-0.44, 0.09)]), 0.02)
    for i in range(7):
        x = -0.92 + i * 0.07
        c.fill([(x, 0.095), (x + 0.03, 0.095), (x + 0.015, 0.15)])
    c.fill(circle(-0.64, -0.08, 0.034, 30), 0)
    c.disc(-0.64, -0.08, 0.02)
    c.line(arc(-0.64, -0.08, 0.06, 280, 410, 20), 0.008)
    for i in range(3):
        y = 0.56 + i * 0.13
        wave_line = [(-0.92 + j * 0.05 + i * 0.1, y + 0.03 * math.sin(j * 0.9 + i)) for j in range(36 - i * 3)]
        c.line(wave_line, taper(0.002, 0.018, 0.002))
    c.line(spline([(-0.76, -0.56), (-0.8, -0.72), (-0.94, -0.82)]), taper(0.012, 0.012, 0.002))
    c.line(spline([(-0.76, -0.56), (-0.7, -0.74), (-0.56, -0.84)]), taper(0.012, 0.012, 0.002))


def alpine_range(c, rng):
    for i in range(36):
        a = 180 + (i - 17.5) * 5
        a = (a + 180) % 360
        c.line([polar(0.36, a, 0.34, -0.5), polar(0.44 + 0.1 * (i % 2), a, 0.34, -0.5)], taper(0.012, 0.012, 0.002))
    c.fill(circle(0.34, -0.5, 0.3), 0)
    c.ring(0.34, -0.5, 0.3, 0.018)
    peaks = (
        ([(0.2, 0.9), (0.68, -0.12), (1.06, 0.9)], 0.68, -0.12),
        ([(-1.0, 0.9), (-0.44, -0.3), (0.12, 0.9)], -0.44, -0.3),
        ([(-0.34, 0.9), (0.14, -0.78), (0.72, 0.9)], 0.14, -0.78),
    )
    for contour, tx, ty in peaks:
        def shade(x, y, tx=tx, ty=ty):
            side = (x - tx) / max(y - ty + 0.3, 0.1)
            base = 0.9 if side > -0.02 else 0.22
            return base + (y - ty) * 0.2

        _engrave(c, contour, 62, 0.026, shade)
        ridge = [(tx, ty), (tx + 0.06, ty + 0.24), (tx - 0.04, ty + 0.5), (tx + 0.08, ty + 0.76), (tx + 0.02, 0.9)]
        c.line(ridge[:4], taper(0.018, 0.012, 0.002))
        cap = [(tx, ty - 0.01), (tx + 0.2 * (0.88 + ty) / 1.66, ty + 0.3), (tx + 0.07, ty + 0.2), (tx, ty + 0.38), (tx - 0.1, ty + 0.2), (tx - 0.2 * (0.88 + ty) / 1.66, ty + 0.3)]
        c.fill(cap, 0)
        c.line(cap, 0.012, closed=True)
    for i in range(3):
        c.line([(-1.0 + i * 0.03, 0.92 + i * 0.05), (1.0 - i * 0.03, 0.92 + i * 0.05)], taper(0.003, 0.018, 0.003))


def lighthouse(c, rng):
    for a, s in ((76, 1), (292, 1)):
        beam = [(0.0, -0.66), polar(0.86, a - 7, 0, -0.66), polar(0.86, a + 7, 0, -0.66)]
        c.hatch(c.mask_of(beam), a, 0.024, 0.014)
    tower = [(-0.14, -0.5), (0.14, -0.5), (0.3, 0.72), (-0.3, 0.72)]

    def cyl(x, y):
        half = 0.14 + (y + 0.5) * 0.13
        u = max(-1.0, min(1.0, x / half))
        band = 0.55 if -0.28 < y < -0.06 or 0.2 < y < 0.44 else 0.0
        return 0.1 + band + 0.55 * max(0.0, u + 0.1) ** 1.2

    _engrave(c, tower, 90, 0.026, cyl)
    c.line([(-0.2, -0.5), (0.2, -0.5)], 0.034)
    c.line([(-0.2, -0.5), (0.2, -0.5)], 0.01, 0)
    c.shape([(-0.1, -0.5), (-0.1, -0.74), (0.1, -0.74), (0.1, -0.5)], 0.016)
    c.line([(0, -0.74), (0, -0.5)], 0.01)
    c.fill([(-0.14, -0.74), (0, -0.92), (0.14, -0.74)])
    c.line([(0, -0.92), (0, -1.0)], 0.016)
    c.disc(0, -1.0, 0.02)
    c.fill(circle(0, -0.62, 0.05, 30))
    for i in range(3):
        c.shape(circle(0, -0.42 + i * 0.3, 0.03, 20), 0.008)
    rock = spline([(-0.92, 0.94), (-0.74, 0.72), (-0.42, 0.66), (-0.1, 0.72), (0.34, 0.66), (0.68, 0.78), (0.94, 0.94)], steps=10)
    rock = rock + [(0.94, 1.0), (-0.92, 1.0)]
    _engrave(c, rock, 58, 0.024, lambda x, y: 0.4 + (y - 0.66) * 1.8 + 0.4 * max(0.0, x))
    for sx, i in ((-0.92, 0), (0.46, 1)):
        for k in range(3):
            c.line(arc(sx + k * 0.16, 0.98, 0.09, 310, 410, 12), taper(0.002, 0.016, 0.002))


def engraved_moon(c, rng):
    disc = circle(0, 0, 0.82, 160)
    curve = lambda x, y: 0.22 * math.sin((x + 0.0) * 1.8)
    def shade(x, y):
        return 0.1 + 1.25 * max(0.0, (x * 0.8 + y * 0.6) / 0.82 + 0.12) ** 1.3
    _engrave(c, disc, 90, 0.028, shade, wobble=curve, outline=0.024)
    for x, y, r in ((-0.36, -0.34, 0.15), (0.05, -0.5, 0.09), (-0.42, 0.22, 0.1), (0.05, 0.05, 0.19), (0.46, 0.34, 0.12), (-0.08, 0.54, 0.08), (0.42, -0.26, 0.07)):
        rim = circle(x, y, r, 48)
        c.fill(rim, 0)
        c.hatch(c.mask_of(rim), 42, 0.02, 0.012, swell=lambda px, py, x=x, y=y, r=r: max(0.0, 1.2 - ((px - x) + (py - y)) / r * 0.9 - 0.8))
        c.line(rim, 0.012, closed=True)
        c.line(arc(x, y, r * 1.08, 90, 240, 18), taper(0.002, 0.01, 0.002))
    for i in range(16):
        a = i * 22.5
        x, y = polar(0.94, a)
        c.fill(star(x, y, 0.055 if i % 2 else 0.09, 0.012, 4, rot=a))


def bronze_bell(c, rng):
    bell = sym([(0, -0.58), (0.24, -0.56), (0.36, -0.34), (0.42, 0.04), (0.52, 0.34), (0.76, 0.56), (0, 0.64)], 12)
    def cyl(x, y):
        half = 0.3 + max(0.0, y + 0.5) * 0.42
        u = x / max(half, 0.1)
        return 0.16 + 1.15 * max(0.0, u + 0.25) ** 1.4 + 0.45 * max(0.0, -u - 0.62)
    curve = lambda x, y: 0.0
    _engrave(c, bell, 90, 0.024, cyl, wobble=curve)
    for y, half in ((-0.28, 0.35), (-0.2, 0.37), (0.26, 0.47), (0.36, 0.55)):
        c.line(spline([(-half, y), (0, y + 0.04), (half, y)]), 0.018)
    c.fill(spline([(-0.78, 0.55), (0, 0.65), (0.78, 0.55), (0, 0.74)], closed=True))
    c.line(spline([(-0.76, 0.56), (0, 0.66), (0.76, 0.56)]), 0.012, 0)
    c.line([(0, 0.7), (0, 0.8)], 0.02)
    c.fill(circle(0, 0.86, 0.075, 40))
    c.line(arc(-0.02, 0.86, 0.045, 200, 330, 12), 0.01, 0)
    yoke = [(-0.12, -0.58), (-0.1, -0.8), (0.1, -0.8), (0.12, -0.58)]
    c.line(arc(0, -0.74, 0.14, 270, 450, 30), 0.05)
    c.line(arc(0, -0.74, 0.14, 270, 450, 30), 0.014, 0)
    c.shape(place(yoke, 0, 0.0), 0.02)
    c.hatch(c.mask_of(yoke), 90, 0.03, 0.014)
    for i, (x, y, l) in enumerate(((-0.86, 0.12, 0.32), (-0.82, -0.14, 0.24), (0.86, 0.12, 0.32), (0.82, -0.14, 0.24), (-0.9, 0.36, 0.2), (0.9, 0.36, 0.2))):
        sign = 1 if x > 0 else -1
        c.line([(x, y - l / 2), (x + sign * 0.04, y), (x, y + l / 2)], taper(0.002, 0.02, 0.002))


def windfall_pear(c, rng):
    pear = sym([(0, -0.72), (0.16, -0.68), (0.24, -0.4), (0.44, -0.04), (0.62, 0.34), (0.56, 0.7), (0.26, 0.88), (0, 0.9)], 12)
    wobble = lambda x, y: 0.2 * math.sin(x * 1.9 + 0.3)
    def shade(x, y):
        return 0.08 + 1.3 * max(0.0, (x * 0.55 + (y - 0.2) * 0.55) + 0.1) ** 1.05 * 1.8
    _engrave(c, pear, 90, 0.028, shade, wobble=wobble)
    c.line(spline([(0, -0.7), (0.04, -0.88), (0.14, -1.02)]), taper(0.05, 0.03, 0.03))
    leaf_shape = leaf(0.06, -0.8, 72, 0.62, 0.3)
    _engrave(c, leaf_shape, 30, 0.022, lambda x, y: 0.6 + (y + 0.75) * 2.0)
    c.line([(0.06, -0.8), polar(0.56, 72, 0.06, -0.8)], 0.012, 0)
    for i in range(7):
        x, y = rng.uniform(-0.3, 0.1), rng.uniform(-0.02, 0.42)
        c.fill(circle(x, y, 0.009, 10), 0)
        c.disc(x, y, 0.006)
    c.fill(sym([(0, 0.78), (0.05, 0.84), (0.03, 0.9), (0, 0.9)]))
    shadow = spline([(-0.8, 0.94), (-0.2, 0.9), (0.5, 0.92), (0.94, 0.94)])
    c.line(shadow, taper(0.002, 0.03, 0.002))
    c.line([(-0.5, 1.0), (0.66, 1.0)], taper(0.002, 0.016, 0.002))


# --- 8. Professor Hatchwick Gloom: macabre pen cross-hatching ----------------

PEN = 0.0095


def _xhatch(c, contour, shade, gap=0.03, outline=0.018, keep_paper=True):
    """Hatching building up in layers as a shade function grows from 0 to 1."""
    if keep_paper:
        c.fill(contour, 0)
    mask = c.mask_of(contour)
    for degrees, threshold in ((45, 0.14), (-45, 0.36), (90, 0.58), (0, 0.78)):
        c.hatch(mask, degrees, gap, PEN, swell=lambda x, y, t=threshold: 1.0 if shade(x, y) > t else 0.0)
    if outline:
        c.line(contour, outline, closed=True)


def _lit(light_x, light_y, reach, floor=0.0):
    return lambda x, y: floor + min(1.0, math.hypot(x - light_x, y - light_y) / reach)


def hatched_skull(c, rng):
    skull = place(SKULL, 0, 0.1, 1.08)
    _xhatch(c, skull, _lit(-0.34, -0.5, 1.5, -0.04))
    for sx in (-1, 1):
        socket = place(SOCKET, sx * 0.34, -0.06, 1.08, flip=sx < 0)
        c.fill(socket)
    nose = place(NOSE, 0, 0.1, 1.08)
    c.fill(nose)
    jaw = spline([(-0.46, 0.46), (0, 0.5), (0.46, 0.46)])
    c.line(jaw, 0.016)
    for i in range(-4, 5):
        x = i * 0.082
        c.shape([(x - 0.038, 0.51), (x + 0.038, 0.51), (x + 0.032, 0.76 - abs(i) * 0.014), (x - 0.032, 0.76 - abs(i) * 0.014)], 0.013)
    c.line(spline([(-0.4, 0.74), (0, 0.9), (0.4, 0.74)]), 0.014)
    for pts in ([(-0.1, -1.0), (-0.04, -0.82), (-0.12, -0.7), (-0.05, -0.56)], [(-0.05, -0.74), (0.06, -0.68)], [(0.5, -0.74), (0.4, -0.6), (0.46, -0.48)]):
        c.line(pts, taper(0.018, 0.012, 0.002))


def hourglass_vigil(c, rng):
    glass = sym([(0, -0.84), (0.44, -0.82), (0.46, -0.48), (0.2, -0.14), (0.05, 0.0), (0.2, 0.14), (0.46, 0.48), (0.44, 0.82), (0, 0.84)], 10)
    c.fill(glass, 0)
    upper = [(-0.32, -0.42), (0.32, -0.42), (0.04, -0.02), (-0.04, -0.02)]
    pile = spline([(-0.44, 0.8), (-0.24, 0.48), (0, 0.32), (0.24, 0.48), (0.44, 0.8)]) + [(-0.44, 0.8)]
    _xhatch(c, upper, lambda x, y: 0.3 + (x + 0.2) * 1.0, gap=0.024, outline=0.01)
    _xhatch(c, pile, lambda x, y: 0.25 + (x + 0.3) * 0.8 + (y - 0.4) * 0.4, gap=0.024, outline=0.01)
    c.line([(0, -0.02), (0, 0.32)], 0.014)
    c.line(glass, 0.02, closed=True)
    c.line(spline([(-0.32, -0.74), (-0.34, -0.54), (-0.22, -0.34)]), taper(0.002, 0.01, 0.002))
    for y, sign in ((-0.92, 1), (0.92, -1)):
        cap = [(-0.66, y - 0.08), (0.66, y - 0.08), (0.66, y + 0.08), (-0.66, y + 0.08)]
        _xhatch(c, cap, lambda x, y: 0.4 + (x + 0.5) * 0.5, gap=0.022, outline=0.018)
    for sx in (-1, 1):
        post = [(sx * 0.58, -0.84), (sx * 0.66, -0.84), (sx * 0.66, 0.84), (sx * 0.58, 0.84)]
        _xhatch(c, post, lambda x, y: 0.6 if sx > 0 else 0.2, gap=0.022, outline=0.016)
        for y in (-0.5, 0.0, 0.5):
            c.fill(circle(sx * 0.62, y, 0.05, 24), 0)
            c.ring(sx * 0.62, y, 0.05, 0.016)


def guttering_candle(c, rng):
    wax = spline([(-0.3, -0.34), (-0.1, -0.28), (0.06, -0.36), (0.3, -0.3), (0.32, 0.12), (0.34, 0.5), (0.36, 0.56), (-0.36, 0.56), (-0.32, 0.5), (-0.34, 0.2), (-0.3, -0.06)], closed=True, steps=8)
    _xhatch(c, wax, lambda x, y: 0.08 + max(0.0, x + 0.05) * 1.6)
    for x, top, l, w in ((-0.2, -0.3, 0.46, 0.09), (0.16, -0.32, 0.28, 0.08), (0.32, -0.28, 0.58, 0.07)):
        drip = spline([(x - w / 2, top), (x - w / 2, top + l), (x, top + l + w / 2), (x + w / 2, top + l), (x + w / 2, top)], closed=True, steps=6)
        c.fill(drip, 0)
        c.line(drip[:-5], 0.014)
    c.line([(0, -0.3), (0.0, -0.46)], 0.018)
    flame = sym([(0, -1.0), (0.05, -0.84), (0.13, -0.66), (0.1, -0.52), (0, -0.46)])
    c.line(flame, 0.018, closed=True)
    c.fill(sym([(0, -0.72), (0.05, -0.58), (0.03, -0.5), (0, -0.48)]))
    for i in range(16):
        a = i * 22.5
        c.line([polar(0.26, a, 0, -0.68), polar(0.33 + (i % 2) * 0.06, a, 0, -0.68)], PEN)
    tray = spline([(-0.76, 0.58), (-0.4, 0.58), (0.4, 0.58), (0.76, 0.58), (0.56, 0.84), (-0.56, 0.84)], closed=True, steps=6)
    _xhatch(c, [(-0.78, 0.56), (0.78, 0.56), (0.5, 0.84), (-0.5, 0.84)], lambda x, y: 0.3 + (x + 0.4) * 0.65 + (y - 0.56))
    handle = arc(0.78, 0.68, 0.16, 330, 570, 30)
    c.line(handle, 0.04)
    c.line(handle, 0.012, 0)
    c.line([(-0.54, 0.92), (0.54, 0.92)], 0.02)


def nailed_coffin(c, rng):
    lid = [(-0.22, -1.0), (0.22, -1.0), (0.5, -0.46), (0.3, 1.0), (-0.3, 1.0), (-0.5, -0.46)]
    side = [(0.22, -1.0), (0.3, -0.96), (0.62, -0.44), (0.4, 0.96), (0.3, 1.0), (0.5, -0.46)]
    _xhatch(c, side, lambda x, y: 0.82)
    _xhatch(c, lid, lambda x, y: 0.1 + max(0.0, (x + 0.1) * 0.4 + (y + 0.2) * 0.32))
    inset = place(lid, 0, -0.01, 0.84)
    c.line(inset, 0.01, closed=True)
    cross = [(-0.05, -0.62), (0.05, -0.62), (0.05, -0.36), (0.22, -0.36), (0.22, -0.26), (0.05, -0.26), (0.05, 0.3), (-0.05, 0.3), (-0.05, -0.26), (-0.22, -0.26), (-0.22, -0.36), (-0.05, -0.36)]
    c.line(cross, 0.04, 0, closed=True)
    c.shape(cross, 0.014, solid=True)
    for x, y in ((-0.14, -0.9), (0.14, -0.9), (-0.42, -0.46), (0.42, -0.46), (-0.34, 0.2), (0.34, 0.2), (-0.23, 0.9), (0.23, 0.9)):
        c.fill(circle(x, y, 0.025, 20), 0)
        c.ring(x, y, 0.025, 0.012)
        c.disc(x, y, 0.008)


def belfry_bat(c, rng):
    wing = [(0.08, -0.16), (0.3, -0.42), (0.58, -0.56), (0.98, -0.5), (0.98, 0.0), (0.84, -0.06), (0.74, 0.18), (0.56, 0.06), (0.4, 0.34), (0.26, 0.16), (0.08, 0.34)]
    head = sym([(0.0, -0.32), (0.05, -0.36), (0.15, -0.58), (0.19, -0.3), (0.17, -0.16), (0.08, -0.06), (0, -0.04)], 6)
    body = sym([(0, -0.1), (0.13, -0.04), (0.11, 0.3), (0.04, 0.5), (0, 0.54)])
    for shape in (wing, mirror(wing)):
        _xhatch(c, shape, lambda x, y: 0.58 + abs(x) * 0.26 - (y + 0.2) * 0.2 if abs(x) < 2 else 0, gap=0.024)
        for fx, fy in (shape[4], shape[6], shape[8]):
            c.line(spline([(shape[2][0] * 0.98, shape[2][1] * 0.98), ((shape[2][0] + fx) / 2, (shape[2][1] + fy) / 2 - 0.05), (fx, fy)]), 0.014)
        c.line([shape[0], shape[2]], 0.02)
    _xhatch(c, body, lambda x, y: 0.8, gap=0.02)
    _xhatch(c, head, lambda x, y: 0.85, gap=0.02)
    for sx in (-1, 1):
        c.fill(circle(sx * 0.075, -0.2, 0.024, 20), 0)
    c.fill([(-0.03, -0.1), (-0.015, -0.05), (0, -0.1), (0.015, -0.05), (0.03, -0.1)], 0)
    c.fill(crescent(0.0, 0.76, 0.18, 0.12, 36))
    for sx, y in ((-0.72, 0.56), (0.68, 0.6), (-0.42, 0.82), (0.48, 0.88)):
        c.fill(star(sx, y, 0.05, 0.012, 4))


def poison_bottle(c, rng):
    bottle = sym([(0, -0.62), (0.13, -0.62), (0.13, -0.32), (0.42, -0.08), (0.56, 0.2), (0.56, 0.82), (0.44, 0.94), (0, 0.94)], 8)
    _xhatch(c, bottle, lambda x, y: 0.2 + max(0.0, x + 0.28) * 0.72)
    highlight = spline([(-0.4, 0.2), (-0.44, 0.5), (-0.42, 0.74), (-0.34, 0.74), (-0.36, 0.5), (-0.32, 0.2)], closed=True)
    c.fill(highlight, 0)
    cork = [(-0.16, -0.94), (0.16, -0.94), (0.12, -0.62), (-0.12, -0.62)]
    _xhatch(c, cork, lambda x, y: 0.2 + (x + 0.1) * 2.0, gap=0.024)
    for x, y, r in ((-0.05, -0.84, 0.012), (0.06, -0.76, 0.012), (-0.02, -0.7, 0.01)):
        c.disc(x, y, r)
    c.line([(-0.15, -0.6), (0.15, -0.6)], 0.03)
    label = [(-0.4, 0.26), (0.4, 0.26), (0.4, 0.84), (-0.4, 0.84)]
    c.fill(label, 0)
    c.line(label, 0.016, closed=True)
    c.line(place(label, s=0.9, x=0.0, y=0.055), 0.008, closed=True)
    skull = place(SKULL, 0, 0.5, 0.19)
    c.shape(skull, 0.012)
    for sx in (-1, 1):
        c.fill(place(SOCKET, sx * 0.06, 0.47, 0.2, flip=sx < 0))
    c.fill(place(NOSE, 0, 0.5, 0.19))
    for a, b in (((-0.28, 0.66), (0.28, 0.78)), ((0.28, 0.66), (-0.28, 0.78))):
        c.line([a, b], 0.03)
        for p in (a, b):
            c.disc(p[0] - 0.015 if p[0] < 0 else p[0] + 0.015, p[1], 0.02)
    for i, (x, y, r) in enumerate(((0.3, -0.3, 0.03), (0.46, -0.5, 0.045), (0.34, -0.72, 0.06), (0.62, -0.84, 0.035))):
        c.fill(circle(x, y, r, 24), 0)
        c.ring(x, y, r, 0.011)


# --- 9. Polygonzo the Faceted: low-poly masks made of hatched triangles ------


def _facets(c, vertices, faces, rng, width=0.013):
    """Faces are (a, b, c, kind): k black, h hatch, H dense hatch, d dots, w blank."""
    for flip in (1, -1):
        for a, b, d, kind in faces:
            tri = [vertices[a], vertices[b], vertices[d]]
            if flip < 0:
                tri = mirror(tri)
            if kind == "k":
                c.fill(tri)
            elif kind in ("h", "H"):
                c.hatch(c.mask_of(tri), 45 * flip, 0.022 if kind == "H" else 0.038, 0.011)
            elif kind == "d":
                c.stipple(c.mask_of(tri), lambda x, y: 0.75, 0.018, 0.006, rng)
            c.line(tri, width, closed=True)


def fox_mask(c, rng):
    v = dict(a=(0.74, -1.0), b=(0.24, -0.52), c=(0.86, -0.24), d=(0, -0.44), e=(0.32, -0.1), f=(1.0, 0.16),
             g=(0.14, 0.06), h=(0.2, 0.42), i=(0.54, 0.44), j=(0, 1.0), k=(0, 0.62), l=(0, 0.1), m=(0.5, -0.56))
    faces = [("a", "b", "m", "k"), ("a", "m", "c", "h"), ("b", "m", "e", "d"), ("m", "c", "e", "w"), ("b", "d", "e", "H"),
             ("d", "l", "e", "w"), ("e", "c", "f", "H"), ("e", "f", "i", "w"), ("e", "i", "g", "k"), ("g", "i", "h", "d"),
             ("l", "e", "g", "h"), ("l", "g", "h", "w"), ("l", "h", "k", "d"), ("h", "i", "j", "H"), ("h", "j", "k", "w")]
    _facets(c, v, faces, rng)
    c.fill([(0, 0.62), (0.11, 0.54), (0, 0.76), (-0.11, 0.54)])
    for sx in (-1, 1):
        c.fill(circle(sx * 0.3, 0.14, 0.03, 16), 0)


def wolf_mask(c, rng):
    v = dict(a=(0.54, -1.0), b=(0.2, -0.46), c=(0.66, -0.28), d=(0, -0.56), e=(0.26, -0.16), f=(0.92, 0.0),
             g=(0.1, 0.1), h=(0.2, 0.5), i=(0.62, 0.34), j=(0.42, 0.72), k=(0, 0.8), l=(0, 0.14), m=(0.18, 0.88), n=(0, 1.0), o=(0.76, 0.58))
    faces = [("a", "b", "c", "H"), ("b", "d", "e", "k"), ("b", "c", "e", "h"), ("d", "l", "e", "d"), ("e", "c", "f", "w"),
             ("e", "f", "i", "H"), ("f", "i", "o", "k"), ("i", "o", "j", "h"), ("e", "i", "g", "k"), ("g", "i", "h", "w"), ("l", "e", "g", "w"),
             ("l", "g", "h", "h"), ("l", "h", "k", "w"), ("h", "i", "j", "d"), ("h", "j", "m", "H"), ("h", "m", "k", "d"), ("k", "m", "n", "k")]
    _facets(c, v, faces, rng)
    c.fill([(0, 0.8), (0.14, 0.72), (0, 0.9), (-0.14, 0.72)])
    for sx in (-1, 1):
        c.fill([(sx * 0.2, 0.0), (sx * 0.38, 0.1), (sx * 0.24, 0.13)], 0)


def owl_mask(c, rng):
    v = dict(a=(0.74, -0.98), b=(0.3, -0.56), c=(0, -0.46), d=(0.96, -0.2), e=(0.98, 0.42), f=(0.56, 0.98), g=(0, 0.72),
             h=(0.1, -0.08), i=(0.14, 0.34), j=(0.56, 0.56), k=(0.42, -0.5), l=(0.8, 0.08))
    faces = [("a", "b", "k", "k"), ("a", "k", "d", "H"), ("b", "c", "h", "k"), ("b", "k", "h", "w"), ("k", "d", "l", "w"),
             ("d", "l", "e", "H"), ("l", "e", "j", "w"), ("e", "f", "j", "k"), ("j", "f", "g", "h"), ("i", "j", "g", "d"),
             ("h", "i", "c", "w"), ("c", "i", "g", "H")]
    _facets(c, v, faces, rng)
    for sx in (-1, 1):
        c.shape(ngon(sx * 0.42, -0.04, 0.32, 8, 22.5), 0.016)
        for i in range(8):
            c.line([polar(0.32, 45 * i + 22.5, sx * 0.42, -0.04), polar(0.14, 45 * i + 22.5, sx * 0.42, -0.04)], 0.011)
        c.fill(ngon(sx * 0.42, -0.04, 0.15, 8, 22.5))
        c.fill(circle(sx * 0.37, -0.09, 0.03, 16), 0)
    c.shape([(0, 0.0), (0.09, 0.14), (0, 0.42), (-0.09, 0.14)], 0.014, solid=True)


def cut_diamond(c, rng):
    v = dict(a=(0.42, -0.74), b=(0.0, -0.74), c=(0.82, -0.36), d=(0.42, -0.36), e=(0.0, -0.36), f=(0.2, -0.74), g=(0, 0.98))
    faces = [("b", "f", "e", "H"), ("f", "e", "d", "w"), ("f", "a", "d", "d"), ("a", "d", "c", "k"), ("c", "d", "g", "H"), ("d", "e", "g", "h")]
    _facets(c, v, faces, rng, width=0.016)
    for x, y, s in ((-0.8, -0.8, 0.12), (0.84, -0.84, 0.08), (0.68, 0.32, 0.1), (-0.64, 0.42, 0.08), (0.92, -0.56, 0.05)):
        c.fill(star(x, y, s, s * 0.14, 4))


def icosa_cage(c, rng):
    outer = ngon(0, 0, 1.0, 6, 0)
    inner = ngon(0, 0.0, 0.54, 3, 180)
    ring = outer
    shells = []
    for i in range(6):
        p, q = ring[i], ring[(i + 1) % 6]
        n = min(inner, key=lambda v: math.hypot(v[0] - (p[0] + q[0]) / 2, v[1] - (p[1] + q[1]) / 2))
        shells.append((p, q, n))
    for i in range(3):
        a, b = inner[i], inner[(i + 1) % 3]
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        p = min(ring, key=lambda v: math.hypot(v[0] - mx, v[1] - my) - 0.0)
        shells.append((a, b, p))
    kinds = ["k", "h", "w", "H", "d", "w", "h", "w", "k"]
    for (p, q, n), kind in zip(shells, kinds):
        tri = [p, q, n]
        if kind == "k":
            c.fill(tri)
        elif kind in ("h", "H"):
            c.hatch(c.mask_of(tri), 30, 0.022 if kind == "H" else 0.038, 0.011)
        elif kind == "d":
            c.stipple(c.mask_of(tri), lambda x, y: 0.75, 0.018, 0.006, rng)
    for p, q, n in shells:
        c.line([p, q, n], 0.016, closed=True)
    tri = inner
    c.stipple(c.mask_of(tri), lambda x, y: min(1.0, math.hypot(x, y) / 0.5), 0.015, 0.006, rng)
    c.line(tri, 0.02, closed=True)
    for p in ring + inner:
        c.fill(circle(p[0], p[1], 0.032, 16))


# --- 10. The Koi Whisperer of Mu: Japanese-style bold bars, scales and waves --

IRE = 0.024


def _wind_bars(c, rows):
    """The black swept background bars that frame a Japanese-style piece."""
    for y, x0, x1, bow, w in rows:
        dip = 0.05 if x0 < -0.5 else -0.05
        pts = spline([(x0, y + dip), ((x0 + x1) / 2, y - dip * 0.4), (x1, y + dip * 0.2)], steps=16)
        c.line(pts, taper(0.003, w * 1.5, 0.003, 0.3 if x0 < -0.5 else 0.7))


def _seigaiha(c, contour, r=0.15):
    c.fill(contour, 0)
    layer = Canvas()
    row = 0
    y = -1.3
    while y < 1.4:
        x = -1.4 + (r if row % 2 else 0)
        while x < 1.4:
            layer.fill(circle(x, y, r, 40), 0)
            for k, width in ((1.0, 0.018), (0.7, 0.012), (0.42, 0.012)):
                layer.line(circle(x, y, r * k, 40), width, closed=True)
            x += r * 2
        y += r * 0.5
        row += 1
    c.stamp(layer, c.mask_of(contour))


def _scale_body(c, spine, width, gap=0.11):
    pts = resample(spine, int(_length(spine) / gap * 2.2))
    layer = Canvas()
    for i in range(len(pts) - 2, 0, -1):
        a, b = pts[i - 1], pts[i + 1]
        heading = math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1])))
        half = width(i / (len(pts) - 1)) / 2
        rows = 3
        for j in range(-rows, rows + 1):
            off = (j + (i % 2) * 0.5) / rows * half * 1.0
            cx, cy = polar(off, heading + 90, *pts[i])
            scale = arc(cx, cy, gap * 0.62, heading + 96, heading + 264, 12)
            layer.line(scale, 0.012)
    return layer


def _length(points):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:]))


def koi_ascending(c, rng):
    _wind_bars(c, ((-0.9, -1.0, 0.56, 0.0, 0.1), (-0.72, 0.32, 1.02, 0.0, 0.08), (0.6, -1.0, -0.14, 0.0, 0.09), (0.8, 0.0, 1.02, 0.0, 0.1), (0.96, -0.8, 0.5, 0.0, 0.06)))
    spine = spline([(0.42, -0.72), (0.2, -0.26), (-0.22, 0.1), (-0.3, 0.44), (-0.02, 0.68)], steps=20)
    width = lambda t: 0.04 + 0.46 * math.sin(math.pi * min(t * 0.92 + 0.14, 1.0)) ** 0.8 * (1 - t * 0.45)
    tail_tip = spine[-1]
    for pts, w in (([tail_tip, (0.3, 0.8), (0.62, 0.7), (0.78, 0.42)], 0.3), ([tail_tip, (0.04, 0.86), (0.24, 0.95), (0.48, 0.94)], 0.2)):
        fin = ribbon(spline(pts, steps=10), taper(0.03, w, 0.01, 0.55))
        c.shape(fin, IRE)
        rays = Canvas()
        for k in range(3):
            rays.line(spline([tail_tip, ((pts[1][0] + tail_tip[0] + k * 0.03) / 2, (pts[1][1] + tail_tip[1] - k * 0.04) / 2), (pts[3][0] - 0.12 * k, pts[3][1] + 0.08 * (k - 1))]), taper(0.014, 0.01, 0.002))
        c.stamp(rays, c.mask_of(fin))
    for (bx, by, a, l, w) in ((0.04, -0.3, 80, 0.48, 0.3), (0.26, -0.26 + 0.0, 110, 0.0, 0.0), (-0.42, 0.04, 245, 0.44, 0.28)):
        if l:
            fin = leaf(bx, by, a, l, w, belly=0.62)
            c.shape(fin, IRE)
            for k in range(-2, 3):
                c.line([(bx, by), polar(l * 0.9, a + k * 7, bx, by)], taper(0.012, 0.008, 0.002))
    body = ribbon(spine, width)
    c.shape(body, IRE)
    c.stamp(_scale_body(c, spine, width), c.mask_of(body))
    head = sym([(0, -0.36), (0.09, -0.34), (0.2, -0.12), (0.27, 0.1), (0.2, 0.26), (0, 0.3)])
    head = place(head, 0.42, -0.68, 1.0, rot=25)
    c.shape(head, IRE)
    crown = place(sym([(0, -0.08), (0.06, -0.04), (0.08, 0.04), (0.04, 0.1), (0, 0.1)]), 0.44, -0.66, 1.0, rot=25)
    c.fill(crown)
    for sx in (-1, 1):
        ex, ey = place([(sx * 0.17, -0.1)], 0.42, -0.68, rot=25)[0]
        c.fill(circle(ex, ey, 0.04, 24))
        c.fill(circle(ex - 0.01, ey - 0.01, 0.014, 12), 0)
        whisk = place(spline([(sx * 0.07, -0.33), (sx * 0.2, -0.4), (sx * 0.27, -0.27)]), 0.42, -0.68, rot=25)
        c.line(whisk, taper(0.016, 0.012, 0.002))
    c.line(place(spline([(-0.25, 0.14), (0, 0.27), (0.25, 0.14)]), 0.42, -0.68, rot=25), 0.018)
    for x, y, r in ((-0.66, -0.3, 0.1), (-0.8, 0.5, 0.06), (0.64, 0.1, 0.09), (0.7, -0.26, 0.05)):
        for k in (1.0, 0.6, 0.25):
            c.ring(x, y, r * k, 0.011)


def _ruffle(a, inner, outer, spread, rng, x=0.0, y=0.0):
    pts = [polar(inner, a - spread * 0.8, x, y)]
    steps = 7
    for i in range(steps + 1):
        u = i / steps
        r = outer * (0.9 + 0.1 * math.sin(math.pi * u)) * (1.0 + (0.05 if i % 2 else -0.025))
        pts.append(polar(r, a - spread + 2 * spread * u, x, y))
    pts.append(polar(inner, a + spread * 0.8, x, y))
    return spline(pts, closed=True, steps=6)


def _peony(c, x, y, s, rng):
    for inner, outer, spread, count, rot in ((0.5, 1.0, 34, 8, 0), (0.36, 0.78, 34, 7, 18), (0.2, 0.56, 38, 6, 8), (0.08, 0.36, 44, 5, 30)):
        for i in range(count):
            a = rot + 360 * i / count
            shape = _ruffle(a, inner * s, outer * s, spread, rng, x, y)
            c.shape(shape, IRE * 0.8)
            for k in range(-2, 3):
                aa = a + k * spread * 0.3
                c.line([polar(s * (inner + 0.06), aa, x, y), polar(s * (outer * 0.82), aa, x, y)], taper(0.012, 0.009, 0.002))
    c.fill(circle(x, y, s * 0.1, 24))


def peony_bloom(c, rng):
    _wind_bars(c, ((-0.92, -1.0, 0.1, 0.0, 0.1), (-0.74, -1.0, -0.4, 0.0, 0.08), (0.92, -0.2, 1.0, 0.0, 0.1), (0.74, 0.46, 1.0, 0.0, 0.08), (0.76, -1.0, -0.56, 0.0, 0.07)))
    for x, y, a, l in ((-0.46, -0.7, 320, 0.62), (0.56, -0.68, 42, 0.64), (-0.7, 0.36, 250, 0.42), (0.62, 0.62, 128, 0.56), (0.76, 0.0, 88, 0.3), (-0.4, 0.72, 208, 0.44)):
        base = (x * 0.6, y * 0.6)
        contour = leaf(base[0], base[1], a, l, 0.3, belly=0.55)
        c.shape(contour, IRE)
        c.line([base, polar(l * 0.9, a, *base)], 0.014)
        for k in range(1, 6):
            p = polar(l * k / 6, a, *base)
            half = 0.11 * math.sin(math.pi * k / 6)
            c.line([p, polar(half, a - 50, *p)], 0.01)
            c.line([p, polar(half, a + 50, *p)], 0.01)
    _peony(c, 0, 0, 0.72, rng)


def great_wave(c, rng):
    base = [(-1.02, 0.0), (1.02, 0.0), (1.02, 1.0), (-1.02, 1.0)]
    swell = spline([(-1.02, 0.42), (-0.5, 0.12), (0.0, 0.28), (0.4, 0.46), (0.74, 0.3), (1.02, 0.02)], steps=14) + [(1.02, 1.0), (-1.02, 1.0)]
    _seigaiha(c, swell)
    c.line(swell[:-2], IRE * 1.2)
    crest = spline([(-0.92, 0.46), (-0.72, -0.12), (-0.3, -0.62), (0.2, -0.82), (0.66, -0.64), (0.8, -0.36), (0.58, -0.3), (0.5, -0.46), (0.22, -0.38), (-0.08, -0.08), (-0.14, 0.22), (0.02, 0.44), (-0.42, 0.54)], closed=True, steps=14)
    c.fill(crest, 0)
    c.line(crest, IRE * 1.2, closed=True)
    for i in range(5):
        pts = spline([(-0.76 + i * 0.12, 0.42), (-0.6 + i * 0.13, -0.08 + i * 0.03), (-0.2 + i * 0.13, -0.5 + i * 0.09), (0.26 + i * 0.04, -0.68 + i * 0.09)], steps=10)
        c.line(pts, taper(0.05 - i * 0.004, 0.05 - i * 0.005, 0.003))
    for i, a in enumerate(range(20, 170, 18)):
        x, y = polar(0.2, a - 10, 0.56, -0.54)
        hook = curl(0.44 + i * 0.06, -0.7 + 0.04 * i * i * 0.2, a + 50, 0.26, 340, 1)
        c.line(hook, taper(0.03, 0.022, 0.003, 0.1))
    for i in range(44):
        a, r = rng.uniform(310, 470), rng.uniform(0.3, 0.72)
        x, y = polar(r, a, 0.44, -0.46)
        if abs(x) < 1.02 and -1.06 < y < -0.2 and not (x > -0.1 and x < 0.6 and y > -0.74):
            c.disc(x, y, rng.uniform(0.008, 0.026))
    c.fill(crescent(-0.66, -0.72, 0.2, 0.12, 36))


def _blossom(c, x, y, s, rot):
    for i in range(5):
        a = rot + 72 * i
        contour = spline(
            [(x, y), polar(s * 0.8, a - 26, x, y), polar(s * 1.02, a - 8, x, y), polar(s * 0.86, a, x, y), polar(s * 1.02, a + 8, x, y), polar(s * 0.8, a + 26, x, y)],
            closed=True, steps=6)
        c.shape(contour, IRE * 0.72)
    for i in range(10):
        a = rot + 36 * i + 8
        c.line([polar(s * 0.1, a, x, y), polar(s * 0.46, a, x, y)], 0.008)
        c.disc(*polar(s * 0.46, a, x, y), 0.012)
    c.disc(x, y, s * 0.12)


def sakura_bough(c, rng):
    _wind_bars(c, ((0.72, -0.2, 1.02, 0.0, 0.11), (0.9, 0.2, 1.02, 0.0, 0.08), (-0.86, -1.0, -0.2, 0.0, 0.1), (-0.68, -1.0, -0.58, 0.0, 0.08)))
    main = spline([(-1.0, 0.86), (-0.54, 0.56), (-0.2, 0.08), (0.34, -0.2), (0.96, -0.74)], steps=16)
    c.line(main, taper(0.15, 0.09, 0.012, 0.01))
    for pts, w in (([(-0.42, 0.42), (-0.5, -0.02), (-0.34, -0.5)], 0.05), ([(0.1, -0.06), (0.4, 0.2), (0.82, 0.3)], 0.05), ([(0.34, -0.2), (0.2, -0.56), (0.32, -0.9)], 0.04), ([(-0.14, 0.04), (0.04, 0.4), (-0.02, 0.76)], 0.04)):
        c.line(spline(pts, steps=10), taper(w, w * 0.7, 0.008, 0.01))
    for i in range(5):
        p = main[8 + i * 8]
        c.line([(p[0] - 0.035, p[1] + 0.02), (p[0] + 0.035, p[1] + 0.05)], 0.014, 0)
    for x, y, s, r in ((-0.34, -0.56, 0.24, 10), (0.32, -0.9 + 0.1, 0.18, 40), (0.84, 0.28, 0.2, 20), (-0.02, 0.76, 0.22, 50), (-0.16, -0.14, 0.28, 30), (0.52, -0.42, 0.22, 5), (0.5, 0.1, 0.17, 60), (-0.56, 0.2, 0.17, 44)):
        _blossom(c, x, y, s, r)
    for x, y, a in ((-0.76, -0.34, 20), (0.66, 0.66, 80), (0.3, 0.56, 130), (-0.56, 0.74, 200), (-0.84, 0.14, 60), (0.84, -0.26, 100)):
        c.shape(petal(x, y, a, 0.1, 0.075), 0.012)


def cloud_knot(c, rng):
    def cloud(x, y, s, flip=False):
        lobes = [(-0.62, 0.04, 0.34), (-0.18, -0.14, 0.44), (0.32, -0.02, 0.36), (0.68, 0.14, 0.26)]
        tail = [(-0.9, 0.3), (0.9, 0.3)]
        for lx, ly, lr in lobes:
            cx, cy = x + (-lx if flip else lx) * s, y + ly * s
            c.shape(circle(cx, cy, lr * s, 50), 0.026)
        band = spline([(-0.98, 0.26), (-0.4, 0.18), (0.4, 0.2), (0.98, 0.28), (0.3, 0.42), (-0.5, 0.42)], closed=True, steps=8)
        band = place(band, x, y, s, flip=flip)
        c.line(band, 0.02, closed=True)
        c.fill(band, 0)
        for lx, ly, lr in lobes:
            cx, cy = x + (-lx if flip else lx) * s, y + ly * s
            c.fill(circle(cx, cy, lr * s * 0.98, 50), 0)
            spiral = [polar(lr * s * 0.8 * (1 - t / 40) ** 0.9 + 0.002, 170 + t * 22, cx, cy) for t in range(41)]
            c.line(spiral, taper(0.012, 0.028, 0.004))
        c.line(spline([place(tail, x, y, s, flip=flip)[0], (x, y + 0.42 * s), place(tail, x, y, s, flip=flip)[1]]), 0.024)

    c.fill(circle(0.0, -0.3, 0.68, 150))
    c.fill(circle(0.0, -0.3, 0.62, 150), 0)
    c.stipple(c.mask_of(circle(0, -0.3, 0.6)), lambda x, y: max(0.0, min(1.0, (y + 0.55) * 0.5)), 0.018, 0.008, rng)
    cloud(0.3, 0.02, 0.62)
    cloud(-0.34, 0.42, 0.72, flip=True)
    cloud(0.34, 0.74, 0.62)
    _wind_bars(c, ((-0.94, -1.0, 0.1, 0.0, 0.08), (0.98, -0.5, 1.0, 0.0, 0.07)))


def seigaiha_fan(c, rng):
    pivot = (0, 0.62)
    outer = arc(pivot[0], pivot[1], 1.13, -62, 62, 50)
    inner = arc(pivot[0], pivot[1], 0.48, 62, -62, 30)
    panel = outer + inner
    _seigaiha(c, panel, 0.11)
    c.line(panel, IRE * 1.3, closed=True)
    for i in range(1, 12):
        a = -62 + 124 * i / 12
        c.line([polar(0.48, a, *pivot), polar(1.13, a, *pivot)], 0.012)
    for i in range(0, 13, 1):
        a = -62 + 124 * i / 12
        c.line([polar(0.08, a, *pivot), polar(0.48, a, *pivot)], 0.024 if i in (0, 12) else 0.014)
    c.fill(circle(pivot[0], pivot[1], 0.075, 24))
    c.fill(circle(pivot[0], pivot[1], 0.024, 12), 0)
    c.line(arc(pivot[0], pivot[1], 0.48, -62, 62, 40), IRE)
    cord = spline([(0, 0.68), (-0.1, 0.8), (-0.28, 0.78), (-0.42, 0.84)], steps=10)
    c.line(cord, 0.018)
    c.fill(circle(-0.46, 0.84, 0.05, 16))
    for k in range(-3, 4):
        c.line([(-0.46, 0.86), (-0.46 + k * 0.035, 0.98)], 0.012)
    for x, y, s in ((-0.76, 0.62, 0.17), (0.74, 0.66, 0.2)):
        _blossom(c, x, y, s, 12)


# --- 11. Wobbly Pim Scribblesworth: naive marker doodles, wonky on purpose ---

MARKER = 0.04


def _wob(pts, rng, amp=0.014, closed=False):
    """A shaky hand: slow drift added along the line."""
    points = resample(pts, max(int(_length(list(pts) + ([pts[0]] if closed else [])) / 0.06), 6), closed=closed)
    phase = [rng.uniform(0, 6.28) for _ in range(4)]
    out = []
    for i, (x, y) in enumerate(points):
        u = i * 0.19
        out.append((x + amp * (math.sin(u + phase[0]) + 0.5 * math.sin(u * 2.3 + phase[1])),
                    y + amp * (math.sin(u * 0.9 + phase[2]) + 0.5 * math.sin(u * 2.1 + phase[3]))))
    return out


def _draw(c, pts, rng, closed=False, width=MARKER, amp=0.014):
    c.line(_wob(pts, rng, amp, closed), width, closed=closed)


def _scribble(c, contour, rng, rows=13, degrees=None):
    """Colouring-in, back and forth with the marker, wobbling past the line."""
    mask = c.mask_of(contour)
    layer = Canvas()
    xs = [p[0] for p in contour]
    ys = [p[1] for p in contour]
    y = min(ys)
    step = (max(ys) - min(ys)) / rows
    pts = []
    left = True
    while y < max(ys):
        pts.append((min(xs) if left else max(xs), y + rng.uniform(-0.01, 0.01)))
        left = not left
        y += step
    layer.line(pts, MARKER * 0.85)
    c.stamp(layer, mask)


def sad_ghost(c, rng):
    ghost = spline([(-0.56, 0.84), (-0.66, 0.1), (-0.5, -0.56), (0, -0.92), (0.5, -0.56), (0.66, 0.1), (0.56, 0.84), (0.34, 0.66), (0.16, 0.88), (-0.04, 0.68), (-0.22, 0.9), (-0.42, 0.68)], closed=True)
    _draw(c, ghost, rng, closed=True)
    for sx in (-1, 1):
        _draw(c, [(sx * 0.3 - 0.09, -0.24), (sx * 0.3 + 0.09, -0.1)], rng, width=0.034, amp=0.004)
        _draw(c, [(sx * 0.3 + 0.09, -0.24), (sx * 0.3 - 0.09, -0.1)], rng, width=0.034, amp=0.004)
    _draw(c, spline([(-0.18, 0.28), (0, 0.14), (0.18, 0.28)]), rng, width=0.034, amp=0.004)
    c.fill(place(sym([(0, -0.1), (0.05, 0.0), (0.04, 0.08), (0, 0.1)]), 0.36, 0.14, 1.0))
    for x, y in ((-0.86, -0.6), (0.84, -0.7), (0.9, 0.3), (-0.92, 0.4)):
        _draw(c, [(x - 0.07, y), (x + 0.07, y)], rng, width=0.026, amp=0.002)
        _draw(c, [(x, y - 0.07), (x, y + 0.07)], rng, width=0.026, amp=0.002)


def grumpy_cat(c, rng):
    head = spline([(-0.7, -0.12), (-0.72, -0.84), (-0.3, -0.5), (0.3, -0.5), (0.72, -0.84), (0.7, -0.12), (0.8, 0.34), (0.42, 0.82), (-0.42, 0.82), (-0.8, 0.34)], closed=True, steps=8)
    _draw(c, head, rng, closed=True)
    for sx in (-1, 1):
        _draw(c, [(sx * 0.44, -0.2), (sx * 0.14, -0.06)], rng, amp=0.004)
        c.fill(circle(sx * 0.3, 0.04, 0.07, 24))
        for k in range(3):
            y = 0.3 + k * 0.1
            _draw(c, [(sx * 0.48, y), (sx * 0.98, y - 0.1 + k * 0.1)], rng, width=0.022, amp=0.006)
        _scribble(c, [(sx * 0.6, -0.6), (sx * 0.7, -0.74), (sx * 0.68, -0.34)], rng, 5)
    c.fill([(-0.07, 0.24), (0.07, 0.24), (0, 0.34)])
    _draw(c, spline([(-0.18, 0.56), (0, 0.46), (0.18, 0.56)]), rng, amp=0.004, width=0.032)
    _draw(c, [(0, 0.34), (0, 0.46)], rng, amp=0.002, width=0.03)
    for i in (-1, 0, 1):
        _draw(c, [(i * 0.1, -0.5), (i * 0.1, -0.34)], rng, amp=0.004, width=0.03)


def happy_cactus(c, rng):
    body = [(-0.2, 0.8), (-0.22, -0.58), (-0.14, -0.84), (0.14, -0.84), (0.22, -0.58), (0.2, 0.8)]
    _draw(c, spline(body, steps=8), rng, closed=False)
    left = [(-0.2, 0.2), (-0.54, 0.2), (-0.7, 0.06), (-0.7, -0.34), (-0.58, -0.44), (-0.46, -0.34), (-0.46, -0.08), (-0.2, -0.08)]
    right = [(0.2, -0.04), (0.56, -0.04), (0.7, -0.18), (0.7, -0.56), (0.58, -0.66), (0.46, -0.56), (0.46, -0.3), (0.2, -0.3)]
    _draw(c, spline(left, steps=8), rng)
    _draw(c, spline(right, steps=8), rng)
    pot = [(-0.52, 0.56), (0.52, 0.56), (0.38, 1.0), (-0.38, 1.0)]
    c.fill(pot, 0)
    _draw(c, pot, rng, closed=True)
    _scribble(c, pot, rng, 11)
    _draw(c, [(-0.62, 0.56), (0.62, 0.56)], rng, amp=0.006)
    c.fill(circle(-0.08, -0.34, 0.034, 16))
    c.fill(circle(0.08, -0.34, 0.034, 16))
    _draw(c, spline([(-0.08, -0.18), (0, -0.1), (0.08, -0.18)]), rng, width=0.024, amp=0.002)
    for x, y, a in ((-0.1, 0.2, 80), (0.1, 0.32, 280), (-0.08, -0.6, 300), (0.1, -0.64, 60), (-0.6, -0.16, 280), (0.6, -0.4, 80), (0.0, 0.42, 100)):
        _draw(c, [(x, y), polar(0.1, a, x, y)], rng, width=0.022, amp=0.002)
    for i in range(5):
        c.fill(leaf(0, -0.86, -50 + i * 25, 0.18, 0.08))


def toothy_flower(c, rng):
    _draw(c, spline([(0, 0.2), (0.05, 0.6), (-0.06, 1.02)]), rng, width=0.05)
    for sx, y in ((1, 0.72), (-1, 0.88)):
        _draw(c, spline([(0.0, y), (sx * 0.34, y - 0.24), (sx * 0.6, y - 0.14), (sx * 0.3, y + 0.04), (0, y)], closed=True, steps=6), rng, width=0.034, amp=0.008)
    for i in range(8):
        shape = spline([polar(0.3, 45 * i - 22), polar(0.72, 45 * i - 16), polar(0.8, 45 * i), polar(0.72, 45 * i + 16), polar(0.3, 45 * i + 22)], closed=True, steps=6)
        shape = place(shape, 0, -0.18)
        c.fill(shape, 0)
        _draw(c, shape, rng, closed=True, width=0.034, amp=0.008)
    c.fill(circle(0, -0.18, 0.36, 60), 0)
    _draw(c, circle(0, -0.18, 0.36, 60), rng, closed=True)
    mouth = [(-0.24, -0.12), (0.24, -0.12), (0.18, 0.06), (0, 0.11), (-0.18, 0.06)]
    c.fill(spline(mouth, closed=True, steps=6))
    for x in (-0.14, -0.05, 0.05, 0.14):
        c.fill([(x - 0.038, -0.12), (x + 0.038, -0.12), (x, -0.02)], 0)
    for sx in (-1, 1):
        c.fill(circle(sx * 0.14, -0.28, 0.04, 16))


def little_bomb(c, rng):
    ball = circle(0, 0.22, 0.68, 80)
    _draw(c, ball, rng, closed=True)
    _scribble(c, circle(0.0, 0.22, 0.66, 60), rng, 24)
    c.fill(spline([(-0.46, 0.0), (-0.36, -0.2), (-0.14, -0.3), (-0.3, -0.12), (-0.38, 0.04)], closed=True), 0)
    cap = [(-0.16, -0.5), (0.16, -0.5), (0.16, -0.38), (-0.16, -0.38)]
    c.fill(cap, 0)
    _draw(c, cap, rng, closed=True)
    fuse = spline([(0, -0.52), (0.1, -0.76), (0.34, -0.7), (0.48, -0.86)])
    _draw(c, fuse, rng)
    for i in range(8):
        a = i * 45 + 20
        _draw(c, [polar(0.07, a, 0.54, -0.92), polar(0.17 + (i % 2) * 0.05, a, 0.54, -0.92)], rng, width=0.024, amp=0.002)
    for sx in (-1, 1):
        c.fill(circle(sx * 0.22, 0.14, 0.1, 24), 0)
        c.fill(circle(sx * 0.22 + 0.02, 0.17, 0.045, 16))
    smile = spline([(-0.3, 0.46), (0, 0.62), (0.3, 0.46)])
    c.line(smile, 0.04, 0)


def speedy_snail(c, rng):
    foot = spline([(-0.98, 0.72), (-0.6, 0.78), (0.2, 0.8), (0.62, 0.74), (0.88, 0.5), (0.96, 0.16), (0.8, 0.12), (0.74, 0.34), (0.5, 0.42), (0.1, 0.36)], steps=8)
    _draw(c, foot, rng)
    c.line([(-0.98, 0.72), (-0.48, 0.5)], MARKER)
    c.line([(-0.5, 0.5), (0.1, 0.36)], MARKER)
    spiral = [polar(0.62 * (1 - t / 80) ** 0.8 + 0.02, 250 + t * 12.5, -0.18, 0.02) for t in range(81)]
    c.fill(circle(-0.18, 0.02, 0.62, 80), 0)
    _draw(c, spiral, rng)
    _draw(c, circle(-0.18, 0.02, 0.62, 80), rng, closed=True)
    for sx, y in ((0.74, -0.2), (1.0, -0.14)):
        _draw(c, spline([(sx - 0.06 if sx < 1 else 0.92, 0.2), (sx, y + 0.1), (sx, y)]), rng, width=0.028, amp=0.003)
        c.fill(circle(sx, y - 0.02, 0.05, 16))
    for y in (0.3, 0.52, 0.72):
        _draw(c, [(-0.96, y - 0.14), (-0.86, y - 0.14)], rng, width=0.026, amp=0.002)
    c.fill(spline([(0.8, 0.44), (0.9, 0.38), (0.84, 0.5)], closed=True))


# --- 12. Pokey Pixie Pinprick: hand-poked, everything made of separate dots ---

POKE = 0.034
DOT = 0.0135


def _poke(c, pts, closed=False, gap=POKE, r=DOT):
    c.dotted(pts, gap, r, closed)


def _shade_dots(c, contour, spacing=0.045, r=0.012, keep=None):
    mask = c.mask_of(contour)
    n = int(1.3 / spacing)
    for j in range(-n, n + 1):
        for i in range(-n, n + 1):
            x = (i + (j % 2) * 0.5) * spacing
            y = j * spacing * 0.87
            if mask.has(x, y) and (keep is None or keep(x, y)):
                c.disc(x, y, r)


def poked_heart(c, rng):
    heart = place(HEART, 0, -0.04, 0.82)
    _poke(c, heart, closed=True)
    _poke(c, place(HEART, 0, -0.04, 0.68), closed=True, gap=0.044, r=0.01)
    _shade_dots(c, place(HEART, 0, -0.04, 0.54), 0.056, 0.012, keep=lambda x, y: x + y * 0.4 > -0.1)
    for a in range(0, 360, 30):
        x, y = polar(0.98, a, 0, -0.02)
        if abs(y) < 1.02 and (a < 100 or a > 260):
            _poke(c, [(x, y), polar(0.1, a, x, y)], gap=0.03, r=0.01)
    for x, y in ((-0.84, 0.78), (0.84, 0.78), (-0.5, 0.92), (0.5, 0.92)):
        c.fill(star(x, y, 0.07, 0.016, 4))


def moon_and_pins(c, rng):
    moon = crescent(-0.1, 0, 0.84, 0.42, 34)
    _poke(c, moon, closed=True)
    _shade_dots(c, moon, 0.05, 0.012, keep=lambda x, y: math.hypot(x - 0.32, y) > 0.78 and math.hypot(x + 0.1, y) < 0.74)
    for x, y, s in ((0.32, -0.44, 0.22), (0.56, 0.1, 0.13), (0.18, 0.28, 0.1), (0.62, -0.72, 0.1), (-0.0, -0.08, 0.08)):
        for a in range(0, 360, 90):
            _poke(c, [(x, y), polar(s, a, x, y)], gap=0.03, r=0.01)
        for a in range(45, 360, 90):
            c.disc(*polar(s * 0.34, a, x, y), 0.008)
        c.disc(x, y, 0.018)
    for x, y in ((-0.92, -0.86), (0.9, 0.6), (-0.88, 0.84), (0.94, -0.3), (0.5, 0.8), (-0.3, 0.98)):
        c.disc(x, y, 0.02)


def poked_dagger(c, rng):
    blade = [(-0.1, -0.4), (0.1, -0.4), (0.12, 0.3), (0, 1.0), (-0.12, 0.3)]
    _poke(c, blade, closed=True)
    _shade_dots(c, [(0, -0.38), (0.1, -0.38), (0.11, 0.3), (0, 0.92)], 0.042, 0.011)
    guard = [(-0.42, -0.54), (0.42, -0.54), (0.42, -0.42), (-0.42, -0.42)]
    _poke(c, guard, closed=True)
    grip = [(-0.08, -0.86), (0.08, -0.86), (0.08, -0.54), (-0.08, -0.54)]
    _poke(c, grip, closed=True)
    for i in range(4):
        y = -0.8 + i * 0.07
        _poke(c, [(-0.07, y), (0.07, y + 0.03)], gap=0.03, r=0.009)
    _poke(c, circle(0, -0.97, 0.1, 40), closed=True)
    c.disc(0, -0.97, 0.03)
    spine = spline([(-0.6, 0.64), (-0.3, 0.3), (0.28, 0.2), (0.36, -0.12), (-0.24, -0.2), (-0.38, -0.34), (0.1, -0.46)], steps=14)
    c.fill(ribbon(spine, lambda t: 0.1), 0)
    _poke(c, ribbon(spine, lambda t: 0.1), closed=True, gap=0.036, r=0.01)
    for sx, y in ((-0.72, -0.2), (0.72, 0.4), (-0.72, 0.84), (0.7, -0.76)):
        c.fill(star(sx, y, 0.08, 0.018, 4))


def poked_bee(c, rng):
    body = sym([(0, -0.3), (0.2, -0.22), (0.28, 0.06), (0.22, 0.42), (0.1, 0.68), (0, 0.84)])
    _poke(c, body, closed=True)
    for y0, y1 in ((-0.02, 0.1), (0.2, 0.32), (0.44, 0.54)):
        mask = c.mask_of(body)
        for j in range(int((y1 - y0) / 0.025) + 1):
            y = y0 + j * 0.025
            for i in range(-12, 13):
                x = i * 0.026 + (j % 2) * 0.013
                if mask.has(x, y):
                    c.disc(x, y, 0.012)
    _poke(c, circle(0, -0.46, 0.17, 50), closed=True)
    for sx in (-1, 1):
        c.disc(sx * 0.07, -0.5, 0.032)
        _poke(c, spline([(sx * 0.06, -0.62), (sx * 0.2, -0.84), (sx * 0.34, -0.86)]), gap=0.03, r=0.011)
        c.disc(sx * 0.35, -0.87, 0.026)
        fore = spline([(sx * 0.16, -0.22), (sx * 0.54, -0.6), (sx * 0.98, -0.46), (sx * 0.92, -0.14), (sx * 0.4, 0.0)], closed=True)
        hind = spline([(sx * 0.2, 0.02), (sx * 0.62, -0.04), (sx * 0.84, 0.14), (sx * 0.6, 0.36), (sx * 0.24, 0.24)], closed=True)
        _poke(c, fore, closed=True)
        _poke(c, hind, closed=True)
        for t, (ax, ay) in enumerate(((0.54, -0.6), (0.82, -0.46))):
            _poke(c, spline([(sx * 0.2, -0.2), (sx * (ax - 0.1), ay + 0.2), (sx * ax, ay + 0.08)]), gap=0.034, r=0.008)
        _poke(c, [(sx * 0.3, 0.1), (sx * 0.7, 0.14)], gap=0.034, r=0.008)
    for x, y in ((-0.84, 0.74), (0.8, 0.82), (-0.6, 0.94), (0.5, 0.96)):
        c.disc(x, y, 0.02)


def poked_cherries(c, rng):
    twig = spline([(0.0, -0.9), (0.04, -0.78), (0.2, -0.76)])
    _poke(c, twig)
    _poke(c, spline([(0.02, -0.78), (-0.2, -0.42), (-0.42, 0.04)]))
    _poke(c, spline([(0.04, -0.78), (0.24, -0.34), (0.42, 0.26)]))
    for x, y, r in ((-0.46, 0.34, 0.42), (0.44, 0.58, 0.38)):
        rim = circle(x, y, r, 60)
        _poke(c, rim, closed=True)
        _shade_dots(c, rim, 0.04, 0.012, keep=lambda px, py, x=x, y=y, r=r: (px - x) + (py - y) > -r * 0.2 and math.hypot(px - x, py - y) < r * 0.9)
        c.disc(x - r * 0.4, y - r * 0.4, 0.03)
    for pts in (leaf(0.04, -0.82, 90, 0.72, 0.28), leaf(-0.02, -0.84, 290, 0.5, 0.2)):
        _poke(c, pts, closed=True)
    _poke(c, [(0.04, -0.82), (0.7, -0.82)], gap=0.036, r=0.009)
    _poke(c, [(-0.02, -0.84), polar(0.46, 290, -0.02, -0.84)], gap=0.036, r=0.009)
    for x, y in ((-0.88, -0.5), (-0.7, -0.74), (0.9, -0.28), (0.96, 0.12), (-0.9, 0.86), (-0.18, 0.92)):
        c.disc(x, y, 0.018)


def poked_sheet(c, rng):
    """A page of small hand-poked stick-and-poke charms."""
    slots = [(-0.66, -0.66), (0, -0.66), (0.66, -0.66), (-0.66, 0), (0, 0), (0.66, 0), (-0.66, 0.66), (0, 0.66), (0.66, 0.66)]
    gap, r = 0.026, 0.0105
    x, y = slots[0]
    _poke(c, place(HEART, x, y, 0.26), True, gap, r)
    x, y = slots[1]
    _poke(c, star(x, y, 0.28, 0.11, 5), True, gap, r)
    x, y = slots[2]
    _poke(c, crescent(x - 0.03, y, 0.27, 0.13, 36), True, gap, r)
    x, y = slots[3]
    _poke(c, [(x - 0.04, y - 0.28), (x + 0.04, y - 0.28), (x + 0.03, y + 0.14), (x, y + 0.28), (x - 0.03, y + 0.14)], True, gap, r)
    _poke(c, [(x - 0.14, y - 0.14), (x + 0.14, y - 0.14)], False, gap, r)
    x, y = slots[4]
    for i in range(5):
        _poke(c, petal(x, y, 72 * i, 0.27, 0.15), True, gap, r)
    c.disc(x, y, 0.03)
    x, y = slots[5]
    _poke(c, circle(x, y, 0.13, 30), True, gap, r)
    _poke(c, leaf(x, y - 0.13, 180 + 180, 0.15, 0.08), True, gap, r)
    for a in (100, 130, 160, 200, 230, 260):
        _poke(c, [polar(0.13, a, x, y), polar(0.28, a, x, y)], False, gap, r)
    x, y = slots[6]
    _poke(c, place(sym([(0, -0.28), (0.22, -0.26), (0.24, 0.02), (0.1, 0.14), (0.08, 0.26), (0, 0.27)]), x, y), True, gap, r)
    for sx in (-1, 1):
        c.disc(x + sx * 0.09, y - 0.06, 0.035)
    x, y = slots[7]
    _poke(c, [(x - 0.2, y - 0.2), (x + 0.2, y - 0.2), (x + 0.28, y - 0.06), (x, y + 0.28), (x - 0.28, y - 0.06)], True, gap, r)
    _poke(c, [(x - 0.28, y - 0.06), (x + 0.28, y - 0.06)], False, gap, r)
    x, y = slots[8]
    _poke(c, [(x + 0.06, y - 0.28), (x - 0.14, y + 0.03), (x + 0.0, y + 0.03), (x - 0.06, y + 0.28), (x + 0.16, y - 0.06), (x + 0.02, y - 0.06)], True, gap, r)


# --- 13. Lady Whiplash Lilyvane: art nouveau, halos and whiplash thick-thin --


def _whiplash(c, pts, w, ink=1, at=0.45):
    c.line(spline(pts, steps=16), taper(0.004, w, 0.002, at), ink)


def _halo(c, x, y, r, rays=48):
    c.ring(x, y, r, 0.028)
    c.ring(x, y, r * 0.92, 0.008)
    for i in range(rays):
        a = 360 * i / rays
        c.disc(*polar(r * 0.96, a, x, y), 0.009)


def _nouveau_frame(c):
    for sx in (-1, 1):
        _whiplash(c, [(sx * 0.1, 1.02), (sx * 0.64, 1.0), (sx * 0.92, 0.76), (sx * 0.93, 0.1), (sx * 0.95, -0.5), (sx * 0.76, -0.9)], 0.05)
        _whiplash(c, [(sx * 0.26, 0.92), (sx * 0.66, 0.88), (sx * 0.83, 0.62), (sx * 0.84, 0.16)], 0.026)
        c.line(curl(sx * 0.76, -0.9, -sx * 70, 0.34, 460, -sx), taper(0.016, 0.02, 0.004))
    c.line([(-0.24, 1.02), (0.24, 1.02)], taper(0.002, 0.024, 0.002))


def peacock_eye(c, rng):
    _nouveau_frame(c)
    _halo(c, 0, -0.34, 0.62)
    stem = spline([(0.0, 1.0), (-0.02, 0.5), (0.0, -0.1)])
    c.line(stem, taper(0.03, 0.016, 0.01))
    for i in range(26):
        t = i / 26
        p = (0, 0.64 - t * 1.28)
        spread = 0.46 * math.sin(math.pi * min(t * 0.9 + 0.08, 1.0)) ** 0.7 + 0.04
        for sx in (-1, 1):
            end = (sx * spread, p[1] - 0.17 - t * 0.04)
            c.line(spline([p, (sx * spread * 0.5, p[1] - 0.04 - t * 0.02), end], steps=8), taper(0.014, 0.012, 0.002))
    c.shape(circle(0, -0.34, 0.24, 60, ry=0.27), 0.022)
    c.fill(circle(0, -0.36, 0.16, 50, ry=0.18))
    c.fill(circle(0, -0.36, 0.08, 30), 0)
    c.disc(0, -0.36, 0.04)
    c.disc(-0.016, -0.378, 0.012, 0)
    for i in range(24):
        c.disc(*polar(0.205, i * 15, 0, -0.34), 0.009)


def calla_lilies(c, rng):
    _nouveau_frame(c)
    _halo(c, 0, -0.3, 0.68)
    for x, top, flip, s in ((-0.28, -0.3, 1, 0.92), (0.3, -0.1, -1, 0.82), (0.0, -0.56, 1, 1.0)):
        stem = spline([(x * 0.2, 1.0), (x * 0.5, 0.5), (x, top + 0.2 * s)], steps=10)
        c.line(stem, taper(0.024, 0.018, 0.018))
        bloom = spline([(0, 0.28), (-0.2, 0.08), (-0.28, -0.14), (-0.1, -0.3), (0.12, -0.5), (0.1, -0.28), (0.26, -0.04), (0.16, 0.16)], closed=True, steps=8)
        bloom = place(bloom, x, top, s * 1.1, flip=flip < 0)
        c.shape(bloom, 0.026)
        c.line(place(spline([(0.0, 0.16), (0.01, -0.02), (-0.02, -0.16)]), x, top, s * 1.1, flip=flip < 0), taper(0.05, 0.05, 0.03))
        for k, (px, py) in enumerate(((-0.14, 0.06), (-0.18, -0.08), (0.12, 0.08), (0.18, -0.06))):
            c.line(place(spline([(px * 0.3, 0.2), (px, py)]), x, top, s * 1.1, flip=flip < 0), taper(0.012, 0.01, 0.002))
    for sx, y, l in ((-1, 0.66, 0.6), (1, 0.78, 0.56)):
        _whiplash(c, [(0.0, y + 0.2), (sx * l * 0.36, y - 0.1), (sx * l * 0.72, y - 0.14), (sx * l, y - 0.32)], 0.13)
        c.line(spline([(0.0, y + 0.2), (sx * l * 0.36, y - 0.1), (sx * l * 0.72, y - 0.14), (sx * l, y - 0.32)]), 0.008, 0)


def halo_dragonfly(c, rng):
    _halo(c, 0, -0.04, 0.78, 60)
    for sx in (-1, 1):
        for root_y, tip_x, tip_y, w in ((-0.3, 1.02, -0.5, 0.28), (-0.12, 1.0, 0.18, 0.32)):
            wing = spline([(sx * 0.03, root_y), (sx * tip_x * 0.5, tip_y - 0.1), (sx * tip_x, tip_y - w * 0.3), (sx * tip_x, tip_y + w * 0.3), (sx * tip_x * 0.5, root_y + w * 0.34)], closed=True, steps=10)
            c.shape(wing, 0.02)
            for k in range(1, 5):
                u = k / 5
                c.line(spline([(sx * 0.05, root_y), (sx * tip_x * 0.5 * (0.9 + u * 0.1), root_y + (tip_y - root_y) * 0.5 + (u - 0.5) * w * 0.8 - 0.04), (sx * tip_x * 0.94, tip_y + (u - 0.5) * w * 0.5)]), 0.008)
            layer = Canvas()
            for i in range(12):
                x = sx * (0.2 + i * 0.07)
                layer.line([(x, -1), (x + sx * 0.08, 1)], 0.007)
            c.stamp(layer, c.mask_of(wing))
            spot = circle(sx * tip_x * 0.76, tip_y - 0.03, 0.06, 20)
            c.fill(spot)
    tail = [(0, -0.1), (0, 1.02)]
    c.line(tail, taper(0.08, 0.05, 0.022, 0.08))
    for i in range(8):
        y = 0.1 + i * 0.11
        c.line([(-0.05, y), (0.05, y)], 0.012, 0)
    c.fill(sym([(0, -0.36), (0.09, -0.3), (0.1, -0.12), (0, -0.04)]))
    c.fill(circle(0, -0.46, 0.09, 30))
    for sx in (-1, 1):
        c.fill(circle(sx * 0.06, -0.48, 0.03, 16), 0)
        c.line(spline([(sx * 0.03, -0.56), (sx * 0.14, -0.74), (sx * 0.28, -0.8)]), taper(0.01, 0.01, 0.002))


def swan_reflection(c, rng):
    _halo(c, 0, -0.38, 0.56)
    neck = spline([(0.2, 0.3), (0.42, -0.1), (0.2, -0.46), (-0.06, -0.72), (-0.34, -0.66)], steps=18)
    c.line(neck, taper(0.22, 0.13, 0.085, 0.02))
    c.line(neck, taper(0.17, 0.085, 0.04, 0.02), 0)
    c.shape(place(sym([(0, -0.1), (0.08, -0.05), (0.09, 0.05), (0, 0.1)]), -0.38, -0.67, 1.0, rot=90), 0.02)
    c.fill([(-0.44, -0.71), (-0.72, -0.62), (-0.44, -0.6)])
    c.disc(-0.36, -0.7, 0.02)
    body = spline([(-0.72, 0.26), (-0.46, 0.42), (0.1, 0.5), (0.52, 0.32), (0.56, 0.14), (0.3, 0.14), (0.14, 0.26), (-0.22, 0.14), (-0.56, 0.02), (-0.96, -0.2)], closed=True, steps=12)
    c.shape(body, 0.026)
    for i, s in enumerate((0.0, 0.1, 0.2, 0.3)):
        _whiplash(c, [(-0.76 + s, -0.04 + s * 0.5), (-0.4 + s, 0.16 + s * 0.3), (0.0 + s * 0.4, 0.28 + s * 0.2), (0.36 + s * 0.2, 0.26)], 0.05)
    for i in range(5):
        y = 0.6 + i * 0.1
        half = 0.96 - i * 0.14
        _whiplash(c, [(-half, y + 0.04), (-half * 0.4, y - 0.03), (half * 0.3, y + 0.03), (half, y - 0.04)], 0.05 - i * 0.004)


def ginkgo_spray(c, rng):
    _nouveau_frame(c)
    _halo(c, 0, -0.26, 0.66)
    trunk = spline([(0.02, 1.0), (-0.08, 0.5), (0.04, 0.04), (0.0, -0.3)], steps=12)
    c.line(trunk, taper(0.04, 0.024, 0.012, 0.02))

    def fan(x, y, degrees, s):
        edge = [polar(s, degrees + a, x, y) for a in range(-66, 67, 6)]
        lobes = []
        for i, p in enumerate(edge):
            wave = 0.04 * s * (math.sin(i * 0.57) + (2.6 if i == len(edge) // 2 else 0))
            lobes.append(polar(s - wave, degrees - 66 + i * 6, x, y))
        contour = [(x, y)] + lobes
        c.shape(contour, 0.022)
        for a in range(-58, 60, 9):
            c.line([polar(s * 0.2, degrees + a, x, y), polar(s * 0.92, degrees + a, x, y)], taper(0.012, 0.009, 0.002))

    for x, y, a, l, s in ((-0.08, 0.5, 298, 0.5, 0.26), (-0.04, 0.26, 62, 0.52, 0.28), (0.02, -0.02, 312, 0.42, 0.3), (0.03, -0.12, 48, 0.42, 0.3), (0.0, -0.3, 358, 0.26, 0.34)):
        tip = polar(l, a, x, y)
        c.line(spline([(x, y), polar(l * 0.5, a + 12, x, y), tip]), 0.014)
        fan(tip[0], tip[1], a, s)
    for sx, y, l in ((-1, 0.7, 0.4), (1, 0.76, 0.42)):
        c.shape(leaf(0, y + 0.18, sx * 62, l + 0.18, 0.12), 0.018)
