"""A small black-ink raster: filled polygons, tapered strokes and shading.

Drawing happens in normalized units: x and y run from -1 to 1 around the centre
of the image, y pointing down, and that span covers MARGIN of the image, so a
design that stays inside the unit square keeps clear of the image edge.

Ink is 1 and paper is 0 in rows of bytes, three subpixels per final pixel.
Rows are bytes so that whole spans are slice assignments, and whole rows can be
masked and summed as big integers, which keeps pure Python fast at this size.
"""

import math
import struct
import zlib

FINAL_SIZE = 1024
SUPERSAMPLE = 3
SIZE = FINAL_SIZE * SUPERSAMPLE
MARGIN = 0.84
SCALE = SIZE * MARGIN / 2
CENTRE = SIZE / 2

PAPER = (0xE6, 0xDC, 0xC8)
INK = (0x12, 0x10, 0x0E)

_ONES = bytes([1]) * SIZE
_ZEROS = bytes(SIZE)
_DISCS = {}
_FIELD_CELLS = 128


# --- Geometry -------------------------------------------------------------


def polar(radius, degrees, x=0.0, y=0.0):
    """The point at a distance and a compass angle: 0 is up, 90 is right."""
    angle = math.radians(degrees)
    return (x + radius * math.sin(angle), y - radius * math.cos(angle))


def spline(points, closed=False, steps=10):
    """A Catmull-Rom curve through the points."""
    count = len(points)
    out = []
    last = count if closed else count - 1
    for i in range(last):
        if closed:
            p0, p1, p2, p3 = (points[(i + k) % count] for k in (-1, 0, 1, 2))
        else:
            p0 = points[max(i - 1, 0)]
            p1 = points[i]
            p2 = points[i + 1]
            p3 = points[min(i + 2, count - 1)]
        for s in range(steps):
            t = s / steps
            out.append(
                tuple(
                    0.5
                    * (
                        2 * p1[k]
                        + (p2[k] - p0[k]) * t
                        + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t
                        + (3 * p1[k] - p0[k] - 3 * p2[k] + p3[k]) * t * t * t
                    )
                    for k in (0, 1)
                )
            )
    if not closed:
        out.append(tuple(points[-1]))
    return out


def sym(points, closed_steps=8):
    """A smooth closed shape from its right side, listed from top to bottom."""
    mirrored = [(-x, y) for x, y in reversed(points) if abs(x) > 1e-9]
    return spline(list(points) + mirrored, closed=True, steps=closed_steps)


def place(points, x=0.0, y=0.0, s=1.0, rot=0.0, flip=False, sy=None):
    """Scales, optionally mirrors, rotates clockwise by degrees and then moves."""
    cos_a, sin_a = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    scale_y = s if sy is None else sy
    out = []
    for px, py in points:
        px, py = (-px if flip else px) * s, py * scale_y
        out.append((x + px * cos_a - py * sin_a, y + px * sin_a + py * cos_a))
    return out


def mirror(points):
    return [(-x, y) for x, y in points]


def circle(x, y, r, steps=120, ry=None):
    other = r if ry is None else ry
    return [
        (
            x + r * math.cos(2 * math.pi * i / steps),
            y + other * math.sin(2 * math.pi * i / steps),
        )
        for i in range(steps)
    ]


def arc(x, y, r, start, end, steps=48):
    """Points along a circle between two compass angles."""
    return [polar(r, start + (end - start) * i / steps, x, y) for i in range(steps + 1)]


def leaf(x, y, degrees, length, width, steps=18, belly=0.5):
    """A pointed lens from (x, y) to its tip, in a compass direction."""
    left, right = [], []
    for i in range(steps + 1):
        t = i / steps
        shaped = t ** (math.log(0.5) / math.log(belly))
        half = width / 2 * math.sin(math.pi * shaped)
        cx, cy = polar(length * t, degrees, x, y)
        ox, oy = polar(half, degrees + 90)
        left.append((cx + ox, cy + oy))
        right.append((cx - ox, cy - oy))
    return left + right[::-1][1:-1]


def petal(x, y, degrees, length, width, steps=18):
    """A round-tipped petal, widest near its tip."""
    return leaf(x, y, degrees, length, width, steps, belly=0.66)


def star(x, y, outer, inner, points=5, rot=0.0):
    return [
        polar(outer if i % 2 == 0 else inner, rot + 180.0 * i / points, x, y)
        for i in range(points * 2)
    ]


def ngon(x, y, r, sides, rot=0.0):
    return [polar(r, rot + 360.0 * i / sides, x, y) for i in range(sides)]


def ribbon(spine, width):
    """The outline around a spine. width(t) is the full width at t, 0 to 1."""
    left, right = [], []
    last = len(spine) - 1
    for i, p in enumerate(spine):
        a, b = spine[max(i - 1, 0)], spine[min(i + 1, last)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy) or 1.0
        half = width(i / last) / 2
        left.append((p[0] - dy / length * half, p[1] + dx / length * half))
        right.append((p[0] + dy / length * half, p[1] - dx / length * half))
    return left + right[::-1]


def resample(points, count, closed=False):
    """Points at even distances along a polyline."""
    pts = list(points) + ([points[0]] if closed else [])
    lengths = [0.0]
    for a, b in zip(pts, pts[1:]):
        lengths.append(lengths[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    total = lengths[-1]
    out = []
    j = 0
    span = count if closed else count - 1
    for i in range(count):
        target = total * i / span
        while j < len(lengths) - 2 and lengths[j + 1] < target:
            j += 1
        gap = (lengths[j + 1] - lengths[j]) or 1.0
        t = (target - lengths[j]) / gap
        out.append(
            (pts[j][0] + (pts[j + 1][0] - pts[j][0]) * t, pts[j][1] + (pts[j + 1][1] - pts[j][1]) * t)
        )
    return out


def taper(start, peak, end=None, at=0.5):
    """A width function rising from start to peak at `at`, and falling to end."""
    final = start if end is None else end

    def width(t):
        if t < at:
            return start + (peak - start) * math.sin(math.pi / 2 * t / at)
        return final + (peak - final) * math.cos(math.pi / 2 * (t - at) / (1 - at))

    return width


def _px(value):
    return value * SCALE + CENTRE


# --- Canvas ---------------------------------------------------------------


class Canvas:
    def __init__(self):
        self.rows = [bytearray(SIZE) for _ in range(SIZE)]

    # Filling ---------------------------------------------------------------

    def fill(self, contours, ink=1):
        """Fills one contour, or several by the even-odd rule (for holes)."""
        if contours and isinstance(contours[0][0], (int, float)):
            contours = [contours]
        crossings = {}
        for contour in contours:
            previous = contour[-1]
            for point in contour:
                x0, y0, x1, y1 = previous[0], previous[1], point[0], point[1]
                previous = point
                y0, y1 = y0 * SCALE + CENTRE, y1 * SCALE + CENTRE
                if y0 == y1:
                    continue
                x0, x1 = x0 * SCALE + CENTRE, x1 * SCALE + CENTRE
                if y0 > y1:
                    x0, y0, x1, y1 = x1, y1, x0, y0
                first = max(int(math.ceil(y0 - 0.5)), 0)
                stop = min(int(math.ceil(y1 - 0.5)), SIZE)
                slope = (x1 - x0) / (y1 - y0)
                for row in range(first, stop):
                    x = x0 + (row + 0.5 - y0) * slope
                    if row in crossings:
                        crossings[row].append(x)
                    else:
                        crossings[row] = [x]
        source = _ONES if ink else _ZEROS
        rows = self.rows
        for row, xs in crossings.items():
            xs.sort()
            line = rows[row]
            for i in range(0, len(xs) - 1, 2):
                a = max(int(xs[i] + 0.5), 0)
                b = min(int(xs[i + 1] + 0.5), SIZE)
                if b > a:
                    line[a:b] = source[:b - a]

    def disc(self, x, y, r, ink=1):
        radius = r * SCALE
        key = int(radius * 4)
        spans = _DISCS.get(key)
        if spans is None:
            rr = key / 4 + 0.25
            top = int(rr)
            spans = [
                (dy, int(math.sqrt(max(rr * rr - dy * dy, 0.0)) + 0.5))
                for dy in range(-top, top + 1)
            ]
            _DISCS[key] = spans
        cx, cy = int(_px(x)), int(_px(y))
        source = _ONES if ink else _ZEROS
        rows = self.rows
        for dy, half in spans:
            row = cy + dy
            if 0 <= row < SIZE:
                a, b = max(cx - half, 0), min(cx + half + 1, SIZE)
                if b > a:
                    rows[row][a:b] = source[:b - a]

    def line(self, points, width, ink=1, closed=False):
        """A round-jointed stroke. width is a number, or a function of t, 0 to 1."""
        pts = list(points) + ([points[0]] if closed else [])
        if len(pts) < 2:
            return
        fixed = None if callable(width) else width
        if fixed is None and len(pts) < 8:
            # A taper needs joints to swell at, even on a straight line.
            pts = resample(pts, 16)
        last = len(pts) - 1
        w0 = fixed if fixed is not None else width(0.0)
        self.disc(pts[0][0], pts[0][1], w0 / 2, ink)
        for i in range(last):
            ax, ay = pts[i]
            bx, by = pts[i + 1]
            w1 = fixed if fixed is not None else width((i + 1) / last)
            dx, dy = bx - ax, by - ay
            length = math.hypot(dx, dy)
            if length > 0:
                nx, ny = -dy / length / 2, dx / length / 2
                self.fill(
                    [
                        (ax + nx * w0, ay + ny * w0),
                        (bx + nx * w1, by + ny * w1),
                        (bx - nx * w1, by - ny * w1),
                        (ax - nx * w0, ay - ny * w0),
                    ],
                    ink,
                )
            self.disc(bx, by, w1 / 2, ink)
            w0 = w1

    def shape(self, contour, width, solid=False):
        """A shape that hides what is under it: paper or ink inside, an outline."""
        self.fill(contour, 1 if solid else 0)
        if width:
            self.line(contour, width, closed=True)

    def ring(self, x, y, r, width, ink=1):
        self.line(circle(x, y, r), width, ink, closed=True)

    def dotted(self, points, gap, r, closed=False, ink=1):
        """A line made of separate dots, as a hand-poked line is."""
        pts = list(points) + ([points[0]] if closed else [])
        total = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))
        count = max(int(total / gap), 1)
        for x, y in resample(pts, count + (0 if closed else 1)):
            self.disc(x, y, r, ink)

    # Masks and shading -----------------------------------------------------

    def mask_of(self, contours):
        mask = Canvas()
        mask.fill(contours)
        return mask

    def stamp(self, layer, mask, ink=1):
        """Puts a layer's ink on this canvas, only where the mask has ink."""
        for row, (over, shape) in enumerate(zip(layer.rows, mask.rows)):
            if shape.find(1) < 0 or over.find(1) < 0:
                continue
            cut = int.from_bytes(over, "little") & int.from_bytes(shape, "little")
            value = int.from_bytes(self.rows[row], "little")
            value = value | cut if ink else value ^ (value & cut)
            self.rows[row][:] = value.to_bytes(SIZE, "little")

    def hatch(self, mask, degrees, gap, width, ink=1, wobble=None, swell=None):
        """Parallel lines through the mask. swell(t) varies each line's width."""
        layer = Canvas()
        steps = int(3.0 / gap)
        for i in range(-steps, steps + 1):
            cx, cy = polar(i * gap, degrees + 90)
            line = []
            count = 90 if (wobble or swell) else 1
            for j in range(count + 1):
                t = -1.5 + 3.0 * j / count
                px, py = polar(t, degrees, cx, cy)
                if wobble:
                    ox, oy = polar(wobble(px, py), degrees + 90)
                    px, py = px + ox, py + oy
                line.append((px, py))
            if swell:
                _swell_line(layer, line, width, swell)
            else:
                layer.line(line, width)
        self.stamp(layer, mask, ink)

    def field(self):
        """Distance to the nearest paper, on a coarse grid, in normalized units."""
        cell = SIZE // _FIELD_CELLS
        inf = 1e9
        n = _FIELD_CELLS
        grid = [
            [0.0 if not self.rows[y * cell + cell // 2][x * cell + cell // 2] else inf for x in range(n)]
            for y in range(n)
        ]
        step = cell / SCALE
        diag = step * 1.414
        for y in range(n):
            line = grid[y]
            above = grid[y - 1] if y else None
            for x in range(n):
                if line[x]:
                    best = line[x]
                    if x:
                        best = min(best, line[x - 1] + step)
                    if above:
                        best = min(best, above[x] + step)
                        if x:
                            best = min(best, above[x - 1] + diag)
                        if x + 1 < n:
                            best = min(best, above[x + 1] + diag)
                    line[x] = best
        for y in range(n - 1, -1, -1):
            line = grid[y]
            below = grid[y + 1] if y + 1 < n else None
            for x in range(n - 1, -1, -1):
                if line[x]:
                    best = line[x]
                    if x + 1 < n:
                        best = min(best, line[x + 1] + step)
                    if below:
                        best = min(best, below[x] + step)
                        if x + 1 < n:
                            best = min(best, below[x + 1] + diag)
                        if x:
                            best = min(best, below[x - 1] + diag)
                    line[x] = best
        return lambda x, y: grid[min(max(int(_px(y)) // cell, 0), n - 1)][min(max(int(_px(x)) // cell, 0), n - 1)]

    def has(self, x, y):
        col, row = int(_px(x)), int(_px(y))
        return 0 <= row < SIZE and 0 <= col < SIZE and self.rows[row][col] == 1

    def stipple(self, mask, density, gap, r, rng, ink=1):
        """Jittered dots inside the mask. density(x, y) is their chance, 0 to 1."""
        count = int(1.25 / gap)
        for iy in range(-count, count + 1):
            for ix in range(-count, count + 1):
                x = (ix + rng.random() * 0.9 + (iy % 2) * 0.5) * gap
                y = (iy + rng.random() * 0.9) * gap
                if mask.has(x, y) and rng.random() < density(x, y):
                    self.disc(x, y, r * (0.8 + 0.4 * rng.random()), ink)

    def whip(self, contour, mask, width, length, every, rng, keep=None, ink=1):
        """Traditional whip shading: tapered flicks from an edge into the shape."""
        layer = Canvas()
        pts = resample(contour, max(int(_perimeter(contour) / every), 3), closed=True)
        count = len(pts)
        for i, p in enumerate(pts):
            if keep and not keep(p[0], p[1]):
                continue
            a, b = pts[i - 1], pts[(i + 1) % count]
            dx, dy = b[0] - a[0], b[1] - a[1]
            size = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / size, dx / size
            if not mask.has(p[0] + nx * 0.02, p[1] + ny * 0.02):
                nx, ny = -nx, -ny
            run = length * (0.6 + 0.6 * rng.random())
            tip = (p[0] + nx * run, p[1] + ny * run)
            layer.line([p, tip], lambda t: width * (1 - t))
        self.stamp(layer, mask, ink)

    # Output ----------------------------------------------------------------

    def levels(self):
        """Final rows, each byte the count of inked subpixels, 0 to 9."""
        rows = self.rows
        out = []
        for y in range(FINAL_SIZE):
            total = 0
            for line in (rows[y * 3], rows[y * 3 + 1], rows[y * 3 + 2]):
                if line.find(1) >= 0:
                    for k in (0, 1, 2):
                        total += int.from_bytes(line[k::3], "little")
            out.append(total.to_bytes(FINAL_SIZE, "little"))
        return out


def _swell_line(layer, line, width, swell):
    for i in range(len(line) - 1):
        w = width * swell((line[i][0] + line[i + 1][0]) / 2, (line[i][1] + line[i + 1][1]) / 2)
        if w > 0.0005:
            layer.line([line[i], line[i + 1]], w)


def _perimeter(contour):
    return sum(
        math.hypot(contour[i][0] - contour[i - 1][0], contour[i][1] - contour[i - 1][1])
        for i in range(len(contour))
    )


# --- PNG ------------------------------------------------------------------


def levels_palette():
    """Ten colours from paper to ink, one per count of inked subpixels."""
    count = SUPERSAMPLE * SUPERSAMPLE
    out = bytearray()
    for level in range(count + 1):
        t = level / count
        out.extend(round(PAPER[k] + (INK[k] - PAPER[k]) * t) for k in range(3))
    return bytes(out)


def palette_png(rows, palette):
    """An 8-bit, non-interlaced palette PNG from rows of palette indices."""

    def chunk(kind, body):
        crc = zlib.crc32(kind + body) & 0xFFFFFFFF
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", crc)

    header = struct.pack(">IIBBBBB", len(rows[0]), len(rows), 8, 3, 0, 0, 0)
    raw = b"".join(b"\x00" + bytes(row) for row in rows)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"PLTE", palette)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
