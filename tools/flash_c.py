"""Stand-in tattoo designs, part three. Each function draws one design."""

import math

from flash_a import HEART, NOSE, SKULL, SOCKET
from flash_b import crescent
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

# --- 14. Bramble Knotwright the Third: Celtic interlace, over-and-under bands -


def _segments_cross(a, b, p, q):
    d1 = (b[0] - a[0], b[1] - a[1])
    d2 = (q[0] - p[0], q[1] - p[1])
    denominator = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(denominator) < 1e-12:
        return None
    t = ((p[0] - a[0]) * d2[1] - (p[1] - a[1]) * d2[0]) / denominator
    u = ((p[0] - a[0]) * d1[1] - (p[1] - a[1]) * d1[0]) / denominator
    return (t, u) if 0 <= t < 1 and 0 <= u < 1 else None


def _weave(c, strands, width, gap, outlined=True):
    """Draws closed strands with crossings alternating over and under."""
    loops = [resample(s, max(int(_perimeter(s) / 0.025), 12), closed=True) for s in strands]
    # Every crossing, as (loop, index) on each of the two passes through it.
    hits = {}
    crossings = []
    for la, loop_a in enumerate(loops):
        for lb in range(la, len(loops)):
            loop_b = loops[lb]
            for i, a in enumerate(loop_a):
                b = loop_a[(i + 1) % len(loop_a)]
                start = i + 2 if la == lb else 0
                for j in range(start, len(loop_b)):
                    if la == lb and (j + 1) % len(loop_b) == i:
                        continue
                    p, q = loop_b[j], loop_b[(j + 1) % len(loop_b)]
                    if max(a[0], b[0]) < min(p[0], q[0]) or max(p[0], q[0]) < min(a[0], b[0]):
                        continue
                    if max(a[1], b[1]) < min(p[1], q[1]) or max(p[1], q[1]) < min(a[1], b[1]):
                        continue
                    if _segments_cross(a, b, p, q) is not None:
                        number = len(crossings)
                        crossings.append({"over": None, "passes": ((la, i), (lb, j))})
                        hits.setdefault(la, []).append((i, number, 0))
                        hits.setdefault(lb, []).append((j, number, 1))
    # Alternate along each strand; a crossing already decided sets the phase.
    for la in sorted(hits):
        ordered = sorted(hits[la])
        phase = 0
        for k, (_, number, side) in enumerate(ordered):
            if crossings[number]["over"] is not None:
                is_over = crossings[number]["over"] == side
                phase = (0 if is_over else 1) - k
                break
        for k, (_, number, side) in enumerate(ordered):
            if crossings[number]["over"] is None:
                over = (k + phase) % 2 == 0
                crossings[number]["over"] = side if over else 1 - side

    for loop in loops:
        c.line(loop, width, closed=True)
    if outlined:
        for loop in loops:
            c.line(loop, width - gap * 2, 0, closed=True)
    reach = int(width * 1.2 / 0.025) + 1
    for crossing in crossings:
        loop_index, i = crossing["passes"][crossing["over"]]
        loop = loops[loop_index]
        piece = [loop[(i + k) % len(loop)] for k in range(-reach, reach + 2)]
        # Flat-ended pieces, so the redrawn strand runs seamlessly into itself.
        c.fill(ribbon(piece[1:-1], lambda t: width + gap * 2.6), 0)
        c.fill(ribbon(piece, lambda t: width))
        if outlined:
            c.fill(ribbon(piece, lambda t: width - gap * 2), 0)
    return crossings


def _perimeter(points):
    return sum(math.hypot(points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]) for i in range(len(points)))


def _lattice_knot(columns, rows, transform):
    """Strands of a plaitwork panel: diagonal runs that bounce off the panel edge."""
    width, height = columns * 2, rows * 2
    inset = 0.4
    seen = set()
    strands = []

    def inside(value, limit):
        return inset if value == 0 else limit - inset if value == limit else value

    for y in range(1, height):
        for x in range(1, width):
            if (x + y) % 2 == 0:
                continue
            for start in ((1, 1), (1, -1)):
                state = (x, y, start[0], start[1])
                if state in seen or (x, y, -start[0], -start[1]) in seen:
                    continue
                path = []
                px, py, dx, dy = state
                while True:
                    if 0 < px < width and 0 < py < height:
                        if (px, py, dx, dy) in seen:
                            break
                        seen.add((px, py, dx, dy))
                    path.append((inside(px, width) / width, inside(py, height) / height))
                    px, py = px + dx, py + dy
                    if px in (0, width):
                        dx = -dx
                    if py in (0, height):
                        dy = -dy
                strands.append(spline([transform(u, v) for u, v in path], closed=True, steps=6))
    return strands


def square_knot(c, rng):
    strands = _lattice_knot(4, 4, lambda u, v: (-0.9 + 1.8 * u, -0.9 + 1.8 * v))
    _weave(c, strands, 0.11, 0.021)
    for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        c.fill(ngon(x * 0.96, y * 0.96, 0.05, 4))


def long_panel(c, rng):
    strands = _lattice_knot(2, 6, lambda u, v: (-0.36 + 0.72 * u, -0.96 + 1.92 * v))
    _weave(c, strands, 0.095, 0.019)
    for sx in (-1, 1):
        c.line([(sx * 0.56, -1.0), (sx * 0.56, 1.0)], 0.036)
        c.line([(sx * 0.62, -1.0), (sx * 0.62, 1.0)], 0.01)
        for i in range(9):
            y = -0.88 + i * 0.22
            c.fill(ngon(sx * 0.74, y, 0.04, 4))
    for y in (-1.0, 1.0):
        c.line([(-0.62, y), (0.62, y)], 0.036)


def round_knot(c, rng):
    outer = [polar(0.66 + 0.26 * math.sin(math.radians(a * 8)), a) for a in range(0, 360, 2)]
    inner = [polar(0.66 - 0.26 * math.sin(math.radians(a * 8)), a) for a in range(0, 360, 2)]
    _weave(c, [outer, inner], 0.1, 0.02)
    c.ring(0, 0, 0.27, 0.034)
    c.fill(star(0, 0, 0.2, 0.06, 8))
    c.ring(0, 0, 1.03, 0.03)


def triquetra_ring(c, rng):
    # The trefoil curve, with a ring laced through its three loops.
    knot = []
    for i in range(240):
        t = i * 2 * math.pi / 240
        knot.append((0.325 * (math.sin(t) + 2 * math.sin(2 * t)), 0.325 * (math.cos(t) - 2 * math.cos(2 * t))))
    _weave(c, [knot, circle(0, 0, 0.68, 180)], 0.09, 0.018)
    c.fill(star(0, 0, 0.13, 0.03, 4))


def triskele_spiral(c, rng):
    for a in (0, 120, 240):
        centre = polar(0.46, a)
        pts = [polar(0.42 * (1 - t / 90) ** 0.85 + 0.01, a + 210 + t * 11, *centre) for t in range(91)]
        tail = spline([(0.0, 0.0), polar(0.16, a + 50), pts[0]], steps=10)
        run = tail + pts
        c.line(run, taper(0.03, 0.09, 0.024, 0.2))
        c.line(run, taper(0.002, 0.03, 0.002, 0.2), 0)
    c.fill(circle(0, 0, 0.09, 24))
    c.fill(circle(0, 0, 0.035, 16), 0)
    c.ring(0, 0, 1.0, 0.026)
    for i in range(30):
        c.disc(*polar(0.95, i * 12), 0.012)


# --- 15. Starry Nebulon Quasarpants: cosmic, night windows and orbit lines ---


def _sky(c, contour, rng, count=60):
    c.fill(contour)
    mask = c.mask_of(contour)
    for _ in range(count):
        x, y = rng.uniform(-1.05, 1.05), rng.uniform(-1.05, 1.05)
        if mask.has(x, y):
            if rng.random() < 0.14:
                c.fill(star(x, y, rng.uniform(0.03, 0.05), 0.008, 4), 0)
            else:
                c.disc(x, y, rng.uniform(0.004, 0.012), 0)


def ringed_planet(c, rng):
    _sky(c, circle(0, 0, 1.0, 180), rng, 90)
    planet = circle(0, 0, 0.42, 90)
    for k in (0.78, 0.86, 0.94):
        ring = place(circle(0, 0, k, 140, ry=k * 0.24), rot=-18)
        c.line(ring, 0.024, 0, closed=True)
    # The front half of the ring passes over the planet; the back half behind it.
    c.fill(planet, 0)
    c.hatch(c.mask_of(planet), 72, 0.056, 0.024, swell=lambda x, y: min(1.2, max(0.0, 0.34 + x * 1.2 + y * 0.9)))
    c.ring(0, 0, 0.42, 0.016)
    for k in (0.78, 0.86, 0.94):
        front = place(arc(0, 0, k, 90, 270, 60), s=1.0, sy=0.24, rot=-18)
        c.line(front, 0.046, 1)
        c.line(front, 0.024, 0)


def moon_phases(c, rng):
    _sky(c, spline([(-1.0, -0.42), (0, -0.46), (1.0, -0.42), (1.0, 0.42), (0, 0.46), (-1.0, 0.42)], closed=True, steps=12), rng, 40)
    phases = [(-0.84, 0.1), (-0.54, 0.15), (0.0, 0.3), (0.54, 0.15), (0.84, 0.1)]
    for i, (x, r) in enumerate(phases):
        c.fill(circle(x, 0, r, 80), 0)
        if i in (0, 1):
            d = (0.78 if i == 0 else 0.42) * r
            c.fill(circle(x + d, 0, r * 0.98, 70))
        elif i in (3, 4):
            d = (0.78 if i == 4 else 0.42) * r
            c.fill(circle(x - d, 0, r * 0.98, 70))
        else:
            c.stipple(c.mask_of(circle(x, 0, r)), lambda px, py: min(1.0, math.hypot(px - x + 0.1, py + 0.08) / r) ** 2, 0.014, 0.0055, rng)
    for sx in (-1, 1):
        for i in range(3):
            c.line(arc(sx * 0.0, 0, 0.66 + 0.1 * i, 330 if sx > 0 else 150, 390 if sx > 0 else 210, 18), taper(0.002, 0.012, 0.002))
    for y, flip in ((-0.7, 1), (0.7, -1)):
        for i in range(-3, 4):
            s = 0.11 - abs(i) * 0.018
            c.fill(star(i * 0.24, y + flip * abs(i) * 0.03, s, s * 0.14, 4))


def great_comet(c, rng):
    head = (0.52, -0.52)
    for i in range(28):
        spread = (i - 13.5) * 3.0
        length = rng.uniform(0.9, 1.5)
        p0 = polar(0.08, 225 + spread, *head)
        p1 = polar(length, 225 + spread * 0.82, *head)
        c.line([p0, p1], taper(0.036, 0.026, 0.002, 0.1))
    c.fill(circle(head[0], head[1], 0.17, 50))
    c.fill(circle(head[0], head[1], 0.13, 40), 0)
    c.stipple(c.mask_of(circle(head[0], head[1], 0.12)), lambda x, y: 0.75, 0.014, 0.0055, rng)
    for i in range(16):
        a = i * 22.5
        c.line([polar(0.22, a, *head), polar(0.3 + 0.08 * (i % 2), a, *head)], taper(0.016, 0.012, 0.002))
    for x, y, s in ((-0.1, -0.74, 0.1), (0.8, 0.14, 0.09), (0.34, 0.2, 0.06), (-0.7, -0.4, 0.07), (0.62, 0.62, 0.11), (-0.1, 0.64, 0.05)):
        c.fill(star(x, y, s, s * 0.14, 4))
    for x, y, r in ((-0.44, -0.84, 0.014), (0.08, -0.18, 0.012), (0.9, -0.14, 0.012), (0.2, 0.76, 0.014), (-0.84, 0.0, 0.012)):
        c.disc(x, y, r)


def total_eclipse(c, rng):
    for i in range(60):
        a = i * 6
        l = 0.3 + 0.5 * abs(math.sin(math.radians(a * 2.0))) * rng.uniform(0.7, 1.0)
        spine = spline([polar(0.48, a), polar(0.5 + l * 0.5, a + rng.uniform(-4, 4)), polar(0.5 + l, a + rng.uniform(-6, 6))], steps=8)
        c.line(spine, taper(0.03, 0.022, 0.002, 0.1))
    c.fill(circle(0, 0, 0.5, 120))
    c.ring(0, 0, 0.455, 0.012, 0)
    for i in range(6):
        p = polar(0.31, 40 + i * 60)
        c.fill(star(p[0], p[1], 0.04, 0.008, 4), 0)
    c.fill(circle(0, 0, 0.06, 20), 0)
    for i in range(12):
        a = i * 30 + 15
        c.disc(*polar(0.98, a), 0.016)


def constellation_chart(c, rng):
    c.ring(0, 0, 1.0, 0.03)
    c.ring(0, 0, 0.95, 0.008)
    for i in range(72):
        a = i * 5
        c.line([polar(0.95, a), polar(0.91 if i % 6 else 0.86, a)], 0.009)
    for r in (0.3, 0.6):
        c.dotted(circle(0, 0, r, 100), 0.03, 0.005, closed=True)
    for a in range(0, 180, 45):
        c.dotted([polar(0.84, a), polar(0.84, a + 180)], 0.03, 0.005)
    groups = (
        [(-0.6, -0.46), (-0.36, -0.58), (-0.16, -0.44), (0.02, -0.56), (0.08, -0.3), (-0.14, -0.2), (-0.16, -0.44)],
        [(0.3, -0.12), (0.5, -0.3), (0.68, -0.1), (0.5, 0.12), (0.3, -0.12), (0.2, 0.24)],
        [(-0.62, 0.06), (-0.4, 0.16), (-0.26, 0.42), (-0.46, 0.6), (-0.66, 0.42)],
        [(0.0, 0.36), (0.18, 0.54), (0.42, 0.42), (0.5, 0.66), (0.22, 0.76)],
    )
    for pts in groups:
        c.line(pts, 0.012)
        for x, y in pts:
            c.fill(circle(x, y, 0.046, 16), 0)
            c.fill(star(x, y, 0.062, 0.014, 4))
    for i in range(40):
        x, y = polar(rng.uniform(0.1, 0.84), rng.uniform(0, 360))
        c.disc(x, y, rng.uniform(0.004, 0.009))


def orbit_diagram(c, rng):
    orbits = (0.34, 0.52, 0.72, 0.94)
    for r in orbits:
        c.line(circle(0, 0, r, 160), 0.014, closed=True)
    for i in range(16):
        a = i * 22.5
        c.fill(leaf(*polar(0.17, a), a, 0.1 if i % 2 else 0.14, 0.04))
    c.fill(circle(0, 0, 0.16, 50))
    c.fill(circle(-0.04, -0.05, 0.04, 16), 0)
    for r, a, size, kind in ((0.34, 60, 0.06, 0), (0.52, 200, 0.08, 1), (0.72, 320, 0.11, 2), (0.94, 120, 0.07, 3)):
        x, y = polar(r, a)
        c.fill(circle(x, y, size + 0.02, 40), 0)
        if kind == 0:
            c.fill(circle(x, y, size, 30))
        elif kind == 1:
            c.ring(x, y, size, 0.016)
            c.stipple(c.mask_of(circle(x, y, size)), lambda px, py: 0.8 if px - x > -0.02 else 0.1, 0.012, 0.005, rng)
        elif kind == 2:
            c.ring(x, y, size, 0.016)
            c.hatch(c.mask_of(circle(x, y, size)), 90, 0.03, 0.016)
            c.line(place(circle(0, 0, size * 1.7, 50, ry=size * 0.4), x, y, rot=-22), 0.012, closed=True)
        else:
            c.ring(x, y, size, 0.016)
            c.fill(crescent(x, y, size * 0.8, size * 0.5, 40))
            c.disc(*polar(size * 2.2, a + 60, x, y), 0.018)
    for r, a in ((0.34, 215), (0.52, 45), (0.72, 110), (0.94, 280)):
        x, y = polar(r, a)
        c.fill(star(x, y, 0.04, 0.008, 4))
    for x, y, s in ((-0.86, -0.82, 0.08), (0.86, -0.84, 0.06), (0.9, 0.82, 0.07), (-0.82, 0.86, 0.05)):
        c.fill(star(x, y, s, s * 0.14, 4))


# --- 16. Doctor Moire Dizzywink: optical black-and-white warps --------------


def stripe_sphere(c, rng):
    # Latitude bands, thin at the poles and wide at the equator, as on a globe.
    c.fill(circle(0, 0, 0.98, 180))
    mask = c.mask_of(circle(0, 0, 0.98, 180))
    layer = Canvas()
    for i in range(0, 22, 2):
        a0 = math.radians(-90 + i * 180 / 22)
        a1 = math.radians(-90 + (i + 1) * 180 / 22)
        rows = []
        for j in range(61):
            x = -1.0 + j / 30
            shift = 0.26 * (1 - x * x)
            rows.append((x, math.sin(a0) + shift))
        for j in range(60, -1, -1):
            x = -1.0 + j / 30
            shift = 0.26 * (1 - x * x)
            rows.append((x, math.sin(a1) + shift))
        layer.fill(rows)
    c.stamp(layer, mask, 0)
    c.ring(0, 0, 0.98, 0.03)


def checker_bulge(c, rng):
    def warp(u, v):
        d = math.hypot(u, v)
        k = 1.0 + 0.9 * max(0.0, 1 - d / 1.2) ** 2
        return (u * k * 0.62, v * k * 0.62)

    n = 13
    for iy in range(-n, n):
        for ix in range(-n, n):
            if (ix + iy) % 2:
                continue
            step = 1.42 / n
            u0, v0 = ix * step, iy * step
            edge = []
            for t in range(5):
                edge.append(warp(u0 + step * t / 4, v0))
            for t in range(5):
                edge.append(warp(u0 + step, v0 + step * t / 4))
            for t in range(5):
                edge.append(warp(u0 + step - step * t / 4, v0 + step))
            for t in range(5):
                edge.append(warp(u0, v0 + step - step * t / 4))
            if max(max(abs(p[0]), abs(p[1])) for p in edge) < 1.0:
                c.fill(edge)
    c.line([(-0.98, -0.98), (0.98, -0.98), (0.98, 0.98), (-0.98, 0.98)], 0.03, closed=True)


def hypnotic_spiral(c, rng):
    contour = []
    arms = 2
    for arm in range(arms):
        band = []
        for i in range(321):
            t = i / 320
            r = 0.02 + t * 1.4
            a = arm * 180 + 1000 * t ** 0.8
            band.append(polar(r, a))
        for i in range(320, -1, -1):
            t = i / 320
            r = 0.02 + t * 1.4
            a = arm * 180 + 1000 * t ** 0.8 + 90
            band.append(polar(r, a))
        contour.append(band)
    mask = c.mask_of(circle(0, 0, 1.0, 180))
    layer = Canvas()
    for band in contour:
        layer.fill(band)
    c.stamp(layer, mask)
    c.ring(0, 0, 1.0, 0.03)


def ripple_rings(c, rng):
    radii = [1.0 - i * 0.082 for i in range(12)]
    for i, r in enumerate(radii):
        contour = []
        for j in range(240):
            a = j * 1.5
            wave = 0.038 * math.sin(math.radians(a * 5 + i * 34)) * (1 - i * 0.05)
            contour.append(polar(r + wave, a))
        c.fill(contour, 1 if i % 2 == 0 else 0)


def nested_tunnel(c, rng):
    size = 1.0
    for i in range(16):
        square = ngon(0.02 * i * math.sin(i * 0.4), 0.018 * i, size * 1.41, 4, 45 + i * 6.5)
        c.fill(square, 1 if i % 2 == 0 else 0)
        size *= 0.845


# --- 17. Hexarch Spindlethorn: sigilism, long hairline spikes in symmetry ----


def _spike(c, a, b, w=0.04, bow=0.0, at=0.3):
    mid = ((a[0] + b[0]) / 2 + (b[1] - a[1]) * bow, (a[1] + b[1]) / 2 - (b[0] - a[0]) * bow)
    c.line(spline([a, mid, b], steps=14), taper(0.002, w, 0.001, at))


def _pair(c, a, b, w=0.04, bow=0.0, at=0.3):
    _spike(c, a, b, w, bow, at)
    _spike(c, (-a[0], a[1]), (-b[0], b[1]), w, -bow, at)


def thorn_star(c, rng):
    for i in range(8):
        a = i * 45
        l = 1.04 if i % 2 == 0 else 0.68
        _spike(c, polar(0.06, a), polar(l, a), 0.07, 0, 0.18)
    for i in range(16):
        a = i * 22.5 + 11.25
        _spike(c, polar(0.14, a), polar(0.62, a + 8), 0.022, 0.08, 0.2)
        _spike(c, polar(0.14, a), polar(0.62, a - 8), 0.022, -0.08, 0.2)
    c.ring(0, 0, 0.32, 0.013)
    c.ring(0, 0, 0.7, 0.008)
    for i in range(8):
        c.disc(*polar(0.7, 22.5 + i * 45), 0.018)
    c.fill(ngon(0, 0, 0.09, 4))


def spine_cross(c, rng):
    _spike(c, (0, 0.0), (0, -1.05), 0.075, 0, 0.1)
    _spike(c, (0, -0.1), (0, 1.05), 0.085, 0, 0.1)
    _pair(c, (0.02, -0.34), (0.72, -0.34), 0.06, 0.0, 0.1)
    for i in range(10):
        y = -0.76 + i * 0.18
        l = 0.3 - abs(i - 2) * 0.024
        _pair(c, (0.0, y), (l, y + 0.12), 0.02, 0.1, 0.2)
        _pair(c, (0.0, y), (l * 0.56, y - 0.08), 0.014, -0.1, 0.2)
    _pair(c, (0.56, -0.34), (0.72, -0.6), 0.016, 0.1)
    _pair(c, (0.56, -0.34), (0.72, -0.1), 0.016, -0.1)
    c.ring(0, -0.34, 0.2, 0.012)
    c.fill(ngon(0, -0.34, 0.06, 4))


def barbed_halo(c, rng):
    for r in (0.62, 0.68):
        pts = [polar(r + 0.025 * math.sin(math.radians(a * 10) + (r > 0.65) * 3.14), a) for a in range(0, 362, 2)]
        c.line(pts, 0.016)
    for i in range(10):
        a = i * 36 + 18
        p = polar(0.65, a)
        for off in (-45, 45, 135, 225):
            c.line([p, polar(0.09, a + off, *p)], taper(0.016, 0.012, 0.001))
    for i in range(20):
        a = i * 18
        l = 0.98 if i % 2 == 0 else 0.82
        _spike(c, polar(0.72, a), polar(l + 0.06, a), 0.03, 0, 0.1)
        _spike(c, polar(0.56, a + 9), polar(0.28, a + 9), 0.024, 0, 0.1)
    c.fill(star(0, 0, 0.24, 0.05, 4))
    c.fill(star(0, 0, 0.12, 0.03, 4, rot=45))
    c.ring(0, 0, 0.27, 0.01)


def bat_sigil(c, rng):
    _pair(c, (0.05, -0.22), (1.06, -0.72), 0.06, 0.1, 0.2)
    _pair(c, (0.5, -0.45), (0.96, 0.2), 0.03, -0.14, 0.2)
    _pair(c, (0.3, -0.36), (0.66, 0.44), 0.03, -0.14, 0.2)
    _pair(c, (0.12, -0.26), (0.32, 0.56), 0.03, -0.14, 0.2)
    _pair(c, (0.96, 0.2), (0.66, 0.44), 0.012, 0.16, 0.5)
    _pair(c, (0.66, 0.44), (0.32, 0.56), 0.012, 0.16, 0.5)
    _pair(c, (0.06, -0.3), (0.16, -0.62), 0.04, 0.0, 0.2)
    _spike(c, (0, -0.42), (0, 0.44), 0.11, 0, 0.14)
    for k in range(-3, 4):
        _spike(c, (k * 0.05, 0.5), (k * 0.2, 0.96 - abs(k) * 0.08), 0.03, 0, 0.14)
    c.fill(ngon(0, -0.3, 0.06, 4))
    c.disc(0, -0.6, 0.016)
    c.disc(0, -0.72, 0.012)
    c.disc(0, -0.82, 0.008)
    for sx in (-1, 1):
        c.disc(sx * 0.03, -0.31, 0.009, 0)


def hexed_crown(c, rng):
    for i, (x, top) in enumerate(((0, -1.05), (0.28, -0.8), (0.54, -0.92), (0.8, -0.62))):
        _pair(c, (x, 0.0), (x * 1.08, top), 0.05, 0.0, 0.14)
    _spike(c, (0, 0), (0, -1.05), 0.08, 0, 0.14)
    for i in range(3):
        _pair(c, (0.14 + i * 0.27, -0.02), (0.14 + i * 0.27, -0.56 - (i % 2) * 0.16), 0.022, 0, 0.14)
    band = spline([(-0.9, -0.06), (0, 0.06), (0.9, -0.06)], steps=20)
    c.line(band, 0.018)
    c.line(place(band, y=0.1), 0.044)
    c.line(place(band, y=0.2), 0.012)
    for i in range(-4, 5):
        y = 0.13 + 0.06 * (1 - (i / 4.5) ** 2)
        c.fill(ngon(i * 0.19, y, 0.024, 4), 0)
    for i in range(-4, 5):
        y = 0.28 + 0.06 * (1 - (i / 4.5) ** 2)
        l = 0.34 + 0.32 * (1 - abs(i) / 4)
        _spike(c, (i * 0.19, y), (i * 0.13, y + l), 0.03, 0, 0.1)
    for i in (-1, 1):
        c.fill(star(i * 0.86, 0.72, 0.16, 0.022, 4))
    c.fill(ngon(0, -0.3, 0.08, 4))
    c.ring(0, -0.3, 0.14, 0.01)


# --- 18. Beetlebrow Mothwick: entomology plates, stipple-shaded specimens ----


def _stip(c, contour, rng, depth=0.1, gap=0.0105, r=0.0052, line=0.016, edge=1.08):
    c.fill(contour, 0)
    mask = c.mask_of(contour)
    field = mask.field()
    c.stipple(mask, lambda x, y: max(0.05, min(1.0, edge - field(x, y) / depth)), gap, r, rng)
    if line:
        c.line(contour, line, closed=True)


def _leg(c, pts, w=0.016):
    c.line(pts, w)
    for p in pts[1:-1]:
        c.disc(p[0], p[1], w * 0.9)
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        for t in (0.3, 0.6, 0.85):
            p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            c.line([p, (p[0] + (b[1] - a[1]) * 0.12, p[1] - (b[0] - a[0]) * 0.12)], 0.007)


def _both_legs(c, sets):
    for pts in sets:
        _leg(c, pts)
        _leg(c, mirror(pts))


def stag_beetle(c, rng):
    _both_legs(c, ([(0.2, -0.26), (0.54, -0.38), (0.62, -0.56), (0.82, -0.74)],
                   [(0.3, 0.02), (0.68, 0.08), (0.84, 0.28), (0.94, 0.52)],
                   [(0.3, 0.3), (0.56, 0.56), (0.62, 0.76), (0.72, 0.98)]))
    elytra = sym([(0, -0.2), (0.3, -0.2), (0.4, 0.1), (0.36, 0.56), (0.16, 0.84), (0, 0.9)], 10)
    _stip(c, elytra, rng, depth=0.13)
    c.line([(0, -0.2), (0, 0.9)], 0.016)
    for sx in (-1, 1):
        for k in range(3):
            c.line(spline([(sx * (0.08 + k * 0.08), -0.12), (sx * (0.1 + k * 0.09), 0.3), (sx * (0.04 + k * 0.06), 0.72)]), 0.006)
    thorax = sym([(0, -0.5), (0.3, -0.5), (0.38, -0.32), (0.3, -0.2), (0, -0.2)], 8)
    _stip(c, thorax, rng, depth=0.08)
    head = sym([(0, -0.68), (0.24, -0.68), (0.28, -0.58), (0.2, -0.49), (0, -0.49)], 8)
    _stip(c, head, rng, depth=0.06, edge=1.2)
    for sx in (-1, 1):
        jaw = spline([(sx * 0.18, -0.66), (sx * 0.34, -0.8), (sx * 0.3, -0.96), (sx * 0.14, -1.06), (sx * 0.22, -0.92), (sx * 0.2, -0.82), (sx * 0.08, -0.7)], closed=True)
        c.shape(jaw, 0.014, solid=True)
        c.fill(circle(sx * 0.24, -0.62, 0.028, 12))
        c.line(spline([(sx * 0.2, -0.62), (sx * 0.44, -0.72), (sx * 0.52, -0.92)]), 0.01)


def hawk_moth(c, rng):
    fore = spline([(0.05, -0.34), (0.4, -0.66), (0.86, -0.72), (1.04, -0.56), (0.76, -0.2), (0.4, 0.0), (0.08, -0.04)], closed=True, steps=10)
    hind = spline([(0.06, -0.02), (0.44, 0.02), (0.68, 0.18), (0.6, 0.5), (0.3, 0.56), (0.1, 0.3)], closed=True, steps=10)
    for w in (hind, fore):
        for shape in (w, mirror(w)):
            _stip(c, shape, rng, depth=0.1, edge=1.0)
    for sx in (-1, 1):
        for a in (58, 72, 86, 100, 118):
            c.line(spline([(sx * 0.06, -0.28), polar(0.5, sx * a, 0.0, -0.28), polar(0.86 - abs(a - 70) * 0.004, sx * (a - 4), 0.0, -0.28)]), 0.007)
        for a in (100, 124, 148):
            c.line([(sx * 0.08, 0.0), polar(0.54, sx * a, 0, 0)], 0.007)
        c.fill(circle(sx * 0.52, -0.42, 0.05, 20))
        c.fill(circle(sx * 0.52, -0.42, 0.018, 12), 0)
        c.line(spline([(sx * 0.04, -0.48), (sx * 0.2, -0.76), (sx * 0.42, -0.86)]), taper(0.012, 0.01, 0.002))
    body = sym([(0, -0.48), (0.08, -0.4), (0.13, -0.16), (0.11, 0.3), (0.05, 0.62), (0, 0.72)])
    _stip(c, body, rng, depth=0.05)
    for i in range(6):
        y = 0.04 + i * 0.1
        c.line([(-0.11 + i * 0.01, y), (0.11 - i * 0.01, y)], 0.012)


def honey_bee(c, rng):
    for sx in (1, -1):
        fore = spline([(sx * 0.1, -0.3), (sx * 0.5, -0.62), (sx * 1.0, -0.6), (sx * 0.96, -0.3), (sx * 0.5, -0.06)], closed=True, steps=10)
        hind = spline([(sx * 0.12, -0.08), (sx * 0.5, -0.04), (sx * 0.74, 0.12), (sx * 0.52, 0.28), (sx * 0.16, 0.14)], closed=True, steps=10)
        for w in (hind, fore):
            c.shape(w, 0.014)
            cut = Canvas()
            cut.fill(w)
            field = cut.field()
            c.stipple(cut, lambda x, y, f=field: max(0.0, 0.6 - f(x, y) / 0.1), 0.012, 0.0045, rng)
        for a, l in ((68, 0.84), (82, 0.86), (98, 0.76)):
            c.line([(sx * 0.1, -0.3), polar(l, sx * a, sx * 0.1, -0.3)], 0.007)
        c.line(spline([(sx * 0.1, -0.3), (sx * 0.52, -0.24), (sx * 0.56, -0.5), (sx * 0.84, -0.46)]), 0.007)
        c.line([(sx * 0.14, -0.04), (sx * 0.66, 0.1)], 0.007)
    _both_legs(c, ([(0.14, -0.3), (0.34, -0.14), (0.42, 0.1), (0.5, 0.22)],
                   [(0.14, -0.14), (0.36, 0.14), (0.42, 0.42), (0.54, 0.58)],
                   [(0.13, 0.0), (0.3, 0.34), (0.36, 0.72), (0.5, 0.92)]))
    abdomen = sym([(0, -0.1), (0.2, -0.02), (0.26, 0.26), (0.2, 0.56), (0.08, 0.78), (0, 0.9)], 10)
    _stip(c, abdomen, rng, depth=0.09)
    layer = Canvas()
    for y0, y1 in ((0.08, 0.18), (0.3, 0.4), (0.52, 0.62)):
        layer.fill(spline([(-0.4, y0), (0, y0 + 0.05), (0.4, y0), (0.4, y1), (0, y1 + 0.05), (-0.4, y1)], closed=True, steps=6))
    c.stamp(layer, c.mask_of(abdomen))
    thorax = sym([(0, -0.46), (0.18, -0.42), (0.23, -0.24), (0.15, -0.06), (0, -0.04)], 8)
    _stip(c, thorax, rng, depth=0.1, edge=1.3)
    for i in range(70):
        a, r = rng.uniform(0, 360), rng.uniform(0.05, 0.23)
        x, y = polar(r, a, 0, -0.24)
        c.line([(x, y), polar(0.03, a, x, y)], 0.006)
    head = spline([(0, -0.46), (0.16, -0.58), (0.13, -0.72), (0, -0.78), (-0.13, -0.72), (-0.16, -0.58)], closed=True)
    _stip(c, head, rng, depth=0.06, edge=1.2)
    for sx in (-1, 1):
        c.fill(place(sym([(0, -0.08), (0.05, -0.02), (0.04, 0.06), (0, 0.08)]), sx * 0.13, -0.64))
        c.line(spline([(sx * 0.05, -0.76), (sx * 0.14, -0.9), (sx * 0.32, -0.94)]), 0.012)


def orb_spider(c, rng):
    for i in range(14):
        a = i * 360 / 14
        c.line([(0, 0), polar(1.04, a)], 0.008)
    for r in (0.16, 0.27, 0.4, 0.54, 0.7, 0.86, 1.0):
        pts = []
        for i in range(15):
            a = i * 360 / 14
            p0, p1 = polar(r, a), polar(r, a + 360 / 14)
            mid = ((p0[0] + p1[0]) / 2 * 0.93, (p0[1] + p1[1]) / 2 * 0.93)
            pts.extend([p0, mid])
        c.line(spline(pts, steps=4), 0.008)
    _both_legs(c, ([(0.08, -0.08), (0.34, -0.3), (0.42, -0.56), (0.56, -0.78)],
                   [(0.1, -0.03), (0.46, -0.1), (0.62, -0.26), (0.86, -0.34)],
                   [(0.1, 0.03), (0.44, 0.06), (0.62, 0.22), (0.84, 0.34)],
                   [(0.08, 0.08), (0.3, 0.3), (0.42, 0.56), (0.6, 0.74)]))
    abdomen = spline([(0, 0.0), (0.2, 0.06), (0.26, 0.28), (0.18, 0.5), (0, 0.58), (-0.18, 0.5), (-0.26, 0.28), (-0.2, 0.06)], closed=True)
    _stip(c, abdomen, rng, depth=0.09, edge=1.24)
    c.fill(place(star(0, 0, 0.14, 0.04, 4), 0, 0.27, 1.0, sy=1.3), 0)
    c.line(place(star(0, 0, 0.14, 0.04, 4), 0, 0.27, 1.0, sy=1.3), 0.011, closed=True)
    head = circle(0, -0.06, 0.12, 40)
    _stip(c, head, rng, depth=0.05, edge=1.3)
    for sx in (-1, 1):
        c.disc(sx * 0.04, -0.14, 0.012)
        c.line([(sx * 0.03, -0.17), (sx * 0.05, -0.25)], 0.016)


def plate_dragonfly(c, rng):
    for sx in (-1, 1):
        for root, tip, w in (((0.04, -0.34), (1.04, -0.56), 0.2), ((0.04, -0.2), (0.96, 0.02), 0.22)):
            mx, my = (root[0] + tip[0]) / 2, (root[1] + tip[1]) / 2
            wing = spline([(sx * root[0], root[1]), (sx * mx, my - w * 0.5), (sx * tip[0], tip[1] - 0.04), (sx * tip[0], tip[1] + 0.05), (sx * mx, my + w * 0.5)], closed=True, steps=10)
            c.shape(wing, 0.014)
            mask = c.mask_of(wing)
            layer = Canvas()
            for k in range(1, 5):
                u = k / 5
                layer.line([(sx * root[0], root[1]), (sx * tip[0], tip[1] + (u - 0.5) * w * 1.1)], 0.007)
            for k in range(1, 30):
                x = root[0] + (tip[0] - root[0]) * k / 30
                y = root[1] + (tip[1] - root[1]) * k / 30
                layer.line([(sx * x, y - 0.14), (sx * (x + 0.012), y + 0.14)], 0.005)
            c.stamp(layer, mask)
            field = mask.field()
            c.stipple(mask, lambda x, y, f=field, sx=sx, root=root: 0.65 if abs(x) < 0.3 else 0.0, 0.012, 0.005, rng)
            c.fill(ngon(sx * (tip[0] - 0.14), tip[1] - 0.03 + 0.0, 0.03, 4))
    thorax = sym([(0, -0.44), (0.1, -0.4), (0.12, -0.2), (0.07, -0.06), (0, -0.04)], 8)
    _stip(c, thorax, rng, depth=0.07, edge=1.3)
    for i in range(9):
        y = -0.04 + i * 0.118
        seg = sym([(0, y), (0.045 - i * 0.002, y + 0.02), (0.04 - i * 0.002, y + 0.09), (0, y + 0.12)], 6)
        _stip(c, seg, rng, depth=0.03, edge=1.5, gap=0.009, line=0.01)
    c.shape(circle(0, -0.5, 0.075, 30), 0.012)
    for sx in (-1, 1):
        c.fill(circle(sx * 0.07, -0.53, 0.058, 24))
        c.fill(circle(sx * 0.07 - 0.015, -0.545, 0.014, 10), 0)


def swallowtail(c, rng):
    fore = spline([(0.04, -0.3), (0.42, -0.66), (0.92, -0.86), (1.02, -0.6), (0.82, -0.2), (0.42, -0.02), (0.08, -0.04)], closed=True, steps=10)
    hind = spline([(0.05, -0.04), (0.42, 0.0), (0.74, 0.14), (0.76, 0.4), (0.52, 0.56), (0.48, 0.96), (0.38, 0.62), (0.16, 0.5), (0.05, 0.22)], closed=True, steps=8)
    for w in (hind, fore):
        for shape in (w, mirror(w)):
            _stip(c, shape, rng, depth=0.13, edge=1.15)
    for sx in (-1, 1):
        for a, l in ((48, 0.96), (60, 0.96), (72, 0.92), (86, 0.76), (102, 0.54)):
            c.line([(sx * 0.05, -0.28), polar(l, sx * a, sx * 0.05, -0.28)], 0.01)
        for a, l in ((100, 0.7), (124, 0.68), (146, 0.62), (166, 0.48)):
            c.line([(sx * 0.06, -0.02), polar(l, sx * a, sx * 0.06, -0.02)], 0.01)
        for i in range(6):
            p = (sx * (0.46 + i * 0.09), -0.62 + i * 0.08 + 0.004 * i * i)
            c.fill(circle(p[0], p[1], 0.024, 12), 0)
            c.ring(p[0], p[1], 0.024, 0.006)
        c.fill(circle(sx * 0.44, 0.34, 0.06, 20))
        c.fill(circle(sx * 0.44, 0.34, 0.03, 12), 0)
    body = sym([(0, -0.46), (0.07, -0.38), (0.09, -0.12), (0.07, 0.26), (0, 0.46)])
    _stip(c, body, rng, depth=0.05, edge=1.5)
    for sx in (-1, 1):
        c.line(spline([(sx * 0.02, -0.46), (sx * 0.14, -0.72), (sx * 0.28, -0.84)]), 0.01)
        c.disc(sx * 0.29, -0.85, 0.016)


# --- 19. Snipsy the Paper Goblin: folk paper-cut, black panels, cut-out shapes -


def _scallop(c, contour, bump=0.04, count=60):
    """A panel with a bitten, snipped edge."""
    c.fill(contour)
    for x, y in resample(contour, count, closed=True):
        c.disc(x, y, bump, 0)


def _punch_row(c, points, r=0.015):
    for x, y in points:
        c.disc(x, y, r, 0)


def _cut_leaf(c, x, y, a, l, w, vein=True):
    c.fill(leaf(x, y, a, l, w), 0)
    if vein:
        c.line([polar(l * 0.12, a, x, y), polar(l * 0.86, a, x, y)], 0.01)


def _cut_flower(c, x, y, s, petals=6):
    for i in range(petals):
        c.fill(petal(x, y, 360 * i / petals, s, s * 0.56), 0)
    c.disc(x, y, s * 0.26)
    c.disc(x, y, s * 0.1, 0)


def _round_panel(c):
    outer = circle(0, 0, 1.03, 180)
    _scallop(c, outer, 0.042, 48)
    c.ring(0, 0, 0.9, 0.012, 0)
    _punch_row(c, [polar(0.945, i * 7.5) for i in range(48)])


def folk_bird(c, rng):
    _round_panel(c)
    body = spline([(-0.56, -0.34), (-0.42, -0.5), (-0.26, -0.44), (-0.12, -0.14), (0.26, -0.08), (0.66, -0.34), (0.84, -0.4), (0.74, -0.04), (0.5, 0.28), (0.1, 0.4), (-0.3, 0.2), (-0.46, -0.14), (-0.5, -0.26)], closed=True, steps=8)
    c.fill(body, 0)
    c.fill([(-0.54, -0.42), (-0.72, -0.34), (-0.52, -0.3)], 0)
    c.disc(-0.41, -0.37, 0.034)
    c.disc(-0.41, -0.37, 0.012, 0)
    wing = spline([(-0.16, -0.02), (0.14, -0.08), (0.4, 0.02), (0.3, 0.2), (0.0, 0.26), (-0.2, 0.12)], closed=True, steps=8)
    c.fill(wing)
    for i in range(5):
        c.fill(leaf(-0.1 + i * 0.09, 0.08, 96, 0.2 - i * 0.012, 0.07), 0)
    for x, y, s in ((-0.32, -0.08, 0.05), (-0.22, 0.12, 0.05), (-0.1, 0.3, 0.05), (0.14, 0.32, 0.05), (0.36, 0.22, 0.05)):
        c.disc(x, y, s * 0.5)
    for k in range(4):
        c.line([(0.3 + k * 0.1, -0.1 - k * 0.05), (0.45 + k * 0.08, 0.1 - k * 0.06)], 0.012)
    for sx, y in ((-0.12, 0.4), (0.08, 0.42)):
        c.line([(sx, y), (sx, 0.56)], 0.022, 0)
        for a in (135, 180, 225):
            c.line([(sx, 0.56), polar(0.06, a, sx, 0.56)], 0.016, 0)
    c.line(spline([(-0.76, 0.6), (-0.3, 0.6), (0.3, 0.6), (0.76, 0.6)]), 0.026, 0)
    _cut_flower(c, -0.6, 0.3, 0.11)
    _cut_flower(c, 0.62, 0.32, 0.1)
    _cut_flower(c, 0.02, -0.66, 0.13)
    for x, y, a in ((-0.28, -0.72, 250), (0.3, -0.72, 110), (-0.74, -0.02, 310), (0.76, -0.56 + 0.76, 50), (-0.4, 0.74, 240), (0.42, 0.74, 120)):
        _cut_leaf(c, x, y, a, 0.2, 0.09)


def tree_of_life(c, rng):
    arch = [(-0.84, 1.03), (-0.84, -0.22)] + arc(0, -0.22, 0.84, 270, 450, 40) + [(0.84, 1.03)]
    _scallop(c, arch, 0.036, 64)
    inner = [(-0.74, 0.94), (-0.74, -0.22)] + arc(0, -0.22, 0.74, 270, 450, 40) + [(0.74, 0.94)]
    c.line(inner, 0.012, 0, closed=True)
    c.line([(0, 0.88), (0, -0.74)], taper(0.09, 0.02, 0.012, 0.01), 0)
    for y, l, a in ((0.48, 0.56, 62), (0.14, 0.54, 58), (-0.2, 0.46, 50), (-0.5, 0.3, 42)):
        for sx in (-1, 1):
            pts = spline([(0, y), polar(l * 0.5, sx * (a + 16), 0, y), polar(l, sx * a, 0, y)], steps=10)
            c.line(pts, taper(0.028, 0.018, 0.008, 0.01), 0)
            for t in (0.4, 0.7):
                base = pts[int(t * (len(pts) - 1))]
                c.fill(leaf(base[0], base[1], sx * (a + 58), 0.14, 0.06), 0)
                c.fill(leaf(base[0], base[1], sx * (a - 42), 0.14, 0.06), 0)
            _cut_flower(c, pts[-1][0], pts[-1][1], 0.085, 6)
    _cut_flower(c, 0, -0.82, 0.1, 8)
    for sx in (-1, 1):
        bird = spline([(sx * 0.14, 0.76), (sx * 0.3, 0.62), (sx * 0.44, 0.6), (sx * 0.56, 0.5), (sx * 0.58, 0.68), (sx * 0.42, 0.82), (sx * 0.22, 0.84)], closed=True, steps=6)
        c.fill(bird, 0)
        c.disc(sx * 0.48, 0.61, 0.012)
        c.line([(sx * 0.24, 0.74), (sx * 0.42, 0.72)], 0.012)
    c.line([(-0.72, 0.9), (0.72, 0.9)], 0.018, 0)


def marigold_skull(c, rng):
    _round_panel(c)
    skull = place(SKULL, 0, 0.0, 0.62)
    c.fill(skull, 0)
    for sx in (-1, 1):
        c.fill(place(SOCKET, sx * 0.19, -0.05, 0.62, flip=sx < 0))
        for i in range(8):
            c.disc(*polar(0.17, 45 * i, sx * 0.19, -0.06), 0.012)
        c.fill(star(sx * 0.19, -0.06, 0.07, 0.02, 4), 0)
    c.fill(place(NOSE, 0, 0.0, 0.62))
    for i in range(-3, 4):
        c.line([(i * 0.07, 0.28), (i * 0.066, 0.42)], 0.014)
    c.line(spline([(-0.24, 0.28), (0, 0.31), (0.24, 0.28)]), 0.012)
    forehead = (0, -0.42)
    for i in range(6):
        c.fill(petal(forehead[0], forehead[1], 60 * i, 0.14, 0.09))
    c.disc(forehead[0], forehead[1], 0.03, 0)
    for sx in (-1, 1):
        c.fill(leaf(sx * 0.12, -0.5, sx * 70, 0.2, 0.05))
        c.fill(leaf(sx * 0.3, 0.2, sx * 40, 0.1, 0.04))
    for a in (225, 262, 298, 335, 25, 62, 98, 135):
        x, y = polar(0.74, a)
        _cut_flower(c, x, y, 0.13, 8)


def twin_deer(c, rng):
    panel = [(-1.0, -0.86), (1.0, -0.86), (1.0, 0.86), (-1.0, 0.86)]
    _scallop(c, panel, 0.034, 72)
    c.line(place(panel, s=0.92), 0.012, 0, closed=True)
    for sx in (-1, 1):
        body = spline([(sx * 0.1, -0.06), (sx * 0.34, -0.04), (sx * 0.72, -0.02), (sx * 0.82, 0.12), (sx * 0.72, 0.3), (sx * 0.34, 0.3), (sx * 0.14, 0.2)], closed=True, steps=8)
        c.fill(body, 0)
        c.line(spline([(sx * 0.2, 0.0), (sx * 0.16, -0.26), (sx * 0.12, -0.36)]), 0.09, 0)
        c.fill(spline([(sx * 0.04, -0.42), (sx * 0.2, -0.46), (sx * 0.2, -0.32), (sx * 0.1, -0.28), (sx * 0.0, -0.28)], closed=True), 0)
        c.disc(sx * 0.1, -0.38, 0.016)
        c.fill(leaf(sx * 0.2, -0.42, sx * 70, 0.14, 0.05), 0)
        for lx in (0.22, 0.32, 0.64, 0.74):
            c.line([(sx * lx, 0.25), (sx * (lx - 0.01), 0.6)], 0.036, 0)
        c.line([(sx * 0.76, 0.0), (sx * 0.86, -0.08)], 0.05, 0)
        c.line(spline([(sx * 0.14, -0.46), (sx * 0.2, -0.62), (sx * 0.36, -0.7)]), 0.024, 0)
        c.line(spline([(sx * 0.2, -0.62), (sx * 0.1, -0.74)]), 0.02, 0)
        c.line(spline([(sx * 0.28, -0.67), (sx * 0.3, -0.78)]), 0.02, 0)
        for x, y in ((0.32, 0.06), (0.46, 0.14), (0.6, 0.06), (0.4, 0.2), (0.58, 0.2)):
            c.disc(sx * x, y, 0.018)
        _cut_flower(c, sx * 0.76, -0.54, 0.12)
    c.line([(-0.88, 0.62), (0.88, 0.62)], 0.022, 0)
    _cut_flower(c, 0, 0.1, 0.1)
    c.fill(sym([(0, -0.74), (0.04, -0.6), (0.03, -0.42), (0, -0.28)]), 0)


def sun_and_moon(c, rng):
    _round_panel(c)
    c.fill(circle(0, 0, 0.76, 120), 1)
    for i in range(24):
        a = i * 15
        if 0 <= a <= 180:
            c.fill(leaf(*polar(0.44, a), a, 0.32 if i % 2 == 0 else 0.22, 0.09), 0)
        else:
            x, y = polar(0.66, a)
            c.fill(star(x, y, 0.05 if i % 2 == 0 else 0.03, 0.012, 4), 0)
    disc = circle(0, 0, 0.42, 90)
    c.fill(disc, 0)
    layer = Canvas()
    layer.fill([(-0.5, -0.5), (0, -0.5), (0, 0.5), (-0.5, 0.5)])
    c.stamp(layer, c.mask_of(disc))
    c.fill(crescent(-0.1, 0, 0.3, 0.2, 40), 0)
    c.disc(0.17, -0.1, 0.03)
    c.line(spline([(0.11, -0.17), (0.17, -0.2), (0.25, -0.17)]), 0.012)
    c.line(spline([(0.1, 0.12), (0.2, 0.18), (0.29, 0.1)]), 0.016)
    c.line([(0.17, -0.04), (0.13, 0.05), (0.18, 0.06)], 0.012)
    c.line([(0, -0.42), (0, 0.42)], 0.018)


def paper_lantern(c, rng):
    body = sym([(0, -0.74), (0.42, -0.74), (0.72, -0.4), (0.8, 0.0), (0.72, 0.4), (0.42, 0.74), (0, 0.74)], 10)
    _scallop(c, body, 0.024, 90)
    for k in range(-3, 4):
        u = k / 4
        pts = spline([(u * 0.46, -0.72), (u * 0.8, 0.0), (u * 0.46, 0.72)])
        c.line(pts, 0.014, 0)
    for y in (-0.62, 0.62):
        c.line([(-0.48, y), (0.48, y)], 0.016, 0)
    _cut_flower(c, 0, 0, 0.26, 8)
    c.ring(0, 0, 0.36, 0.014, 0)
    for sx in (-1, 1):
        _cut_flower(c, sx * 0.58, 0, 0.1, 6)
        for y in (-0.4, 0.4):
            _cut_flower(c, sx * 0.34, y, 0.09, 6)
    for y in (-0.42, 0.42):
        c.fill(ngon(0, y, 0.06, 4), 0)
    cap = [(-0.42, -0.9), (0.42, -0.9), (0.42, -0.76), (-0.42, -0.76)]
    c.fill(cap)
    c.line([(0, -0.9), (0, -1.05)], 0.02)
    for y0 in (0.76,):
        c.fill([(-0.42, y0), (0.42, y0), (0.42, y0 + 0.12), (-0.42, y0 + 0.12)])
    for k in range(-4, 5):
        c.line([(k * 0.09, 0.88), (k * 0.1, 1.04 - abs(k) * 0.01)], 0.014)


# --- 20. Prismella Leadglass: stained glass, heavy leading, patterned cells ---

LEAD = 0.03


def _glass(c, cell, kind, rng, degrees=45):
    mask = None
    if kind == "k":
        c.fill(cell)
    elif kind == "h":
        c.hatch(c.mask_of(cell), degrees, 0.034, 0.012)
    elif kind == "x":
        mask = c.mask_of(cell)
        c.hatch(mask, degrees, 0.04, 0.01)
        c.hatch(mask, degrees + 90, 0.04, 0.01)
    elif kind == "d":
        c.stipple(c.mask_of(cell), lambda x, y: 0.8, 0.02, 0.008, rng)


def _clip_cells(c, cells, kinds, clip, rng, lead=LEAD, outline=True):
    """Glass cells stamped through a shape, with their leading on top."""
    layer = Canvas()
    leads = Canvas()
    for i, cell in enumerate(cells):
        _glass(layer, cell, kinds[i % len(kinds)], rng, 30 + i * 37)
        leads.line(cell, lead, closed=True)
    mask = c.mask_of(clip)
    c.fill(clip, 0)
    c.stamp(layer, mask)
    c.stamp(leads, mask)
    if outline:
        c.line(clip, lead * 1.5, closed=True)


def _sectors(x, y, r0, r1, count, rot=0.0):
    cells = []
    for i in range(count):
        a0 = rot + i * 360 / count
        a1 = a0 + 360 / count
        cells.append(arc(x, y, r1, a0, a1, 10) + arc(x, y, r0, a1, a0, 10))
    return cells


def rose_window(c, rng):
    for r0, r1, n, rot, pat in ((0.8, 1.0, 24, 0, "wkwd"), (0.52, 0.8, 12, 7.5, "hwx"), (0.26, 0.52, 12, 0, "dkw"), (0.08, 0.26, 6, 15, "wh")):
        for i, cell in enumerate(_sectors(0, 0, r0, r1, n, rot)):
            _glass(c, cell, pat[i % len(pat)], rng, rot + i * 30)
            c.line(cell, LEAD, closed=True)
    for i in range(12):
        a = 7.5 + i * 30
        x, y = polar(0.66, a)
        c.fill(petal(*polar(0.54, a), a, 0.24, 0.13), 0)
        c.line(petal(*polar(0.54, a), a, 0.24, 0.13), LEAD * 0.8, closed=True)
    c.fill(star(0, 0, 0.1, 0.04, 6))
    c.line(circle(0, 0, 1.0, 160), LEAD * 1.8, closed=True)


def glass_butterfly(c, rng):
    fore = spline([(0.06, -0.34), (0.44, -0.8), (0.94, -0.92), (1.04, -0.56), (0.74, -0.14), (0.3, 0.0), (0.06, -0.02)], closed=True, steps=8)
    hind = spline([(0.06, 0.0), (0.46, 0.02), (0.82, 0.22), (0.76, 0.66), (0.42, 0.92), (0.12, 0.5)], closed=True, steps=8)
    for wing, root, rot, pat in ((fore, (0.06, -0.2), 0, "kwhdwxkw"), (hind, (0.06, 0.02), 0, "wkdwhx")):
        for flip in (1, -1):
            shape = wing if flip > 0 else mirror(wing)
            cells = []
            rx, ry = (root[0] * flip, root[1])
            for a0 in range(0, 360, 24):
                for r0, r1 in ((0.0, 0.4), (0.4, 0.78), (0.78, 1.5)):
                    cells.append(arc(rx, ry, r1, a0, a0 + 24, 4) + (arc(rx, ry, r0, a0 + 24, a0, 4) if r0 else [(rx, ry)]))
            _clip_cells(c, cells, pat, shape, rng)
    body = sym([(0, -0.5), (0.09, -0.4), (0.1, -0.1), (0.07, 0.4), (0, 0.72)])
    c.shape(body, LEAD, solid=True)
    for i in range(5):
        c.line([(-0.08, 0.04 + i * 0.1), (0.08, 0.04 + i * 0.1)], 0.012, 0)
    for sx in (-1, 1):
        c.line(spline([(sx * 0.03, -0.5), (sx * 0.12, -0.78), (sx * 0.3, -0.94)]), 0.022)
        c.disc(sx * 0.31, -0.96, 0.03)


def lancet_lily(c, rng):
    arch = [(-0.62, 1.02), (-0.62, 0.05)] + [polar(1.24, a, 0.62, 0.05) for a in range(270, 330, 4)] + [polar(1.24, a, -0.62, 0.05) for a in range(30, 92, 4)] + [(0.62, 1.02)]
    step = 0.26
    cells = []
    for j in range(-6, 7):
        for i in range(-6, 7):
            cx, cy = (i + j) * step, (i - j) * step
            cells.append([(cx, cy - step), (cx + step, cy), (cx, cy + step), (cx - step, cy)])
    _clip_cells(c, cells, "wwhwwdww", arch, rng, lead=LEAD * 0.7)
    stem = spline([(0, 1.02), (0.02, 0.5), (0, 0.0)], steps=8)
    c.line(stem, 0.06)
    c.line(stem, 0.02, 0)
    for sx in (-1, 1):
        lf = leaf(0, 0.86, sx * 42, 0.7, 0.24)
        c.shape(lf, LEAD)
        c.line([(0, 0.86), polar(0.6, sx * 42, 0, 0.86)], 0.016)
        for a, l, w in ((sx * 50, 0.72, 0.3),):
            pet = petal(0, -0.08, a, l, w)
            c.shape(pet, LEAD)
            c.hatch(c.mask_of(pet), a, 0.04, 0.012)
        pet = petal(0, -0.1, sx * 16, 0.8, 0.26)
        c.shape(pet, LEAD)
        c.fill(leaf(0, -0.14, sx * 16, 0.48, 0.09))
    cen = petal(0, -0.08, 0, 0.86, 0.26)
    c.shape(cen, LEAD, solid=True)
    c.line([(0, -0.14), (0, -0.84)], 0.016, 0)


def glass_fish(c, rng):
    body = spline([(-1.0, 0.0), (-0.66, -0.42), (-0.1, -0.56), (0.42, -0.34), (0.72, -0.06), (0.72, 0.06), (0.42, 0.34), (-0.1, 0.56), (-0.66, 0.42)], closed=True, steps=10)
    tail = [(0.64, 0.0), (1.04, -0.5), (0.94, 0.0), (1.04, 0.5)]
    cells = []
    tail_cells = []
    for i in range(6):
        y0 = -0.6 + i * 0.2
        tail_cells.append([(0.5, 0.0), (1.2, y0), (1.2, y0 + 0.2)])
    _clip_cells(c, tail_cells, "khwd", tail, rng)
    step = 0.17
    for row in range(-5, 6):
        for col in range(-8, 8):
            cx = col * step * 1.0 + (row % 2) * step * 0.5
            cy = row * step * 0.72
            cells.append(ngon(cx, cy, step * 0.62, 6, 30))
    _clip_cells(c, cells, "wkwhwdwx", body, rng, lead=LEAD * 0.7)
    head = [(p[0], p[1]) for p in body if p[0] < -0.5]
    c.fill(head, 0)
    c.line(body, LEAD * 1.5, closed=True)
    head_arc = spline([(-0.52, -0.46), (-0.4, 0.0), (-0.52, 0.46)])
    c.line(head_arc, LEAD)
    c.fill(circle(-0.72, -0.1, 0.075, 30))
    c.fill(circle(-0.74, -0.12, 0.028, 16), 0)
    for sx, pts in ((1, [(-0.14, -0.54), (0.1, -0.86), (0.38, -0.82), (0.32, -0.4)]), (1, [(-0.16, 0.54), (0.06, 0.82), (0.32, 0.76), (0.3, 0.38)])):
        fin = spline(pts + [(0.1, -0.46 if pts[0][1] < 0 else 0.46)], closed=True, steps=6)
        c.fill(fin, 0)
        c.hatch(c.mask_of(fin), 80, 0.04, 0.012)
        c.line(fin, LEAD, closed=True)


def glass_heart(c, rng):
    shape = place(HEART, 0, 0, 1.04)
    cells = []
    for a0 in range(0, 360, 20):
        for r0, r1 in ((0, 0.26), (0.26, 0.54), (0.54, 0.84), (0.84, 1.6)):
            cells.append(arc(0, -0.04, r1, a0, a0 + 20, 3) + (arc(0, -0.04, r0, a0 + 20, a0, 3) if r0 else [(0, -0.04)]))
    _clip_cells(c, cells, "wkwhdwxwkh", shape, rng, lead=LEAD * 0.85)
    c.fill(star(0, -0.04, 0.2, 0.08, 8))
    c.fill(star(0, -0.04, 0.09, 0.04, 8), 0)


def sun_lancet(c, rng):
    arch = [(-0.72, 1.02), (-0.72, -0.24)] + arc(0, -0.24, 0.72, 270, 450, 40) + [(0.72, 1.02)]
    sky_cells = []
    for a0 in range(-90, 90, 15):
        sky_cells.append([(0, 0.2), polar(2.0, a0, 0, 0.2), polar(2.0, a0 + 15, 0, 0.2)])
    _clip_cells(c, sky_cells, "whwdwxw", arch, rng, lead=LEAD * 0.8)
    disc = circle(0, 0.2, 0.34, 70)
    c.fill(disc, 0)
    c.fill(circle(0, 0.2, 0.34, 70))
    for i in range(16):
        c.line([polar(0.1, i * 22.5, 0, 0.2), polar(0.3, i * 22.5, 0, 0.2)], taper(0.006, 0.016, 0.002), 0)
    c.fill(circle(0, 0.2, 0.08, 20), 0)
    hills = (
        spline([(-0.8, 0.5), (-0.4, 0.28), (-0.1, 0.5), (0.3, 0.42), (0.8, 0.62), (0.8, 1.1), (-0.8, 1.1)], closed=True, steps=8),
        spline([(-0.8, 0.8), (-0.3, 0.56), (0.2, 0.72), (0.8, 0.5), (0.8, 1.1), (-0.8, 1.1)], closed=True, steps=8),
    )
    for hill, pat in zip(hills, ("h", "k")):
        cut = c.mask_of(arch)
        hill_mask = Canvas()
        hill_mask.fill(hill)
        layer = Canvas()
        layer.fill(hill)
        c.stamp(layer, cut, 0)
        if pat == "h":
            c.hatch(_both_masks(hill_mask, cut), 20, 0.03, 0.014)
        else:
            c.stamp(layer, cut)
        layer2 = Canvas()
        layer2.line(hill, LEAD, closed=True)
        c.stamp(layer2, cut)
    c.line(arch, LEAD * 1.6, closed=True)


def _both_masks(a, b):
    out = Canvas()
    out.stamp(a, b)
    return out
