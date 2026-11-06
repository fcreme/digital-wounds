#!/usr/bin/env python3
"""Maps painting rectangles marked on the gallery's texture to world positions.

python3 tools/build_paintings.py --overlay out.png
    writes the atlas with every rectangle outlined and numbered. Add
    --crop X0 Y0 X1 Y1, --zoom N and --grid N to check one region up close.

python3 tools/build_paintings.py --assign
    gives every rectangle one design from assets/artists and writes
    assets/paintings/museum.json. Output is identical between runs. This
    replaces every assignment in the file, hand edits included.

python3 tools/build_paintings.py --driver-script
    writes tests/scripts/every_painting.txt (a test-driver script that aims at
    each painting, opens it and closes it) and every_painting.expected next to
    it, from assets/paintings/museum.json. Check a run with
    tests/check_every_painting.py.
"""

import argparse
import json
import os
import random
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import glb_walls  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLB_PATH = os.path.join(ROOT, "props", "the_picture_gallery_low_poly__vr.glb")
RECTS_PATH = os.path.join(ROOT, "tools", "data", "painting_rects.json")
ARTISTS_DIR = os.path.join(ROOT, "assets", "artists")
PAINTINGS_PATH = os.path.join(ROOT, "assets", "paintings", "museum.json")

WALL_OFFSET = 0.03
NORMAL_PROBE = 0.3
BARYCENTRIC_TOLERANCE = 1e-4
UV_MATCH = 1e-4
PLANE_MIN_DOT = 0.99
PLANE_MAX_GAP = 0.05
CONTAINMENT_SAMPLES = 8

ASSIGN_SEED = 20261106
ASSIGN_ATTEMPTS = 200
NEIGHBOUR_DISTANCE = 4.0
SAME_WALL_MAX_GAP = 1.0


def _group_walls(triangles):
    """Groups triangles that share a plane and touch in texture space.

    A wall's quads are continuous in the texture, so a rectangle may span them.
    Atlas regions that merely sit side by side belong to different planes.
    """
    walls = []
    for triangle in triangles:
        touching = [
            wall
            for wall in walls
            if _same_plane(wall["triangles"][0], triangle)
            and _shares_uv(wall["triangles"], triangle)
        ]
        merged = [triangle]
        for wall in touching:
            merged.extend(wall["triangles"])
            walls.remove(wall)
        walls.append({"triangles": merged})
    return walls


def _same_plane(a, b):
    """A plane and its flip are the same wall; the winding varies per triangle."""
    dot = sum(a["normal"][k] * b["normal"][k] for k in range(3))
    if abs(dot) < PLANE_MIN_DOT:
        return False
    return (
        abs(sum(a["normal"][k] * (a["positions"][0][k] - b["positions"][0][k]) for k in range(3)))
        < PLANE_MAX_GAP
    )


def _shares_uv(triangles, triangle):
    for other in triangles:
        for a in other["uvs"]:
            for b in triangle["uvs"]:
                if abs(a[0] - b[0]) < UV_MATCH and abs(a[1] - b[1]) < UV_MATCH:
                    return True
    return False


def _barycentric(uv, triangle):
    (x0, y0), (x1, y1), (x2, y2) = triangle["uvs"]
    determinant = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(determinant) < 1e-12:
        return None
    a = ((y1 - y2) * (uv[0] - x2) + (x2 - x1) * (uv[1] - y2)) / determinant
    b = ((y2 - y0) * (uv[0] - x2) + (x0 - x2) * (uv[1] - y2)) / determinant
    return a, b, 1.0 - a - b


def _uv_to_world(uv, wall):
    """World position of uv on the wall, or None when uv is outside the wall."""
    best = None
    best_margin = -BARYCENTRIC_TOLERANCE
    for triangle in wall["triangles"]:
        weights = _barycentric(uv, triangle)
        if weights is not None and min(weights) >= best_margin:
            best_margin = min(weights)
            best = (weights, triangle)
    if best is None:
        return None
    weights, triangle = best
    return tuple(
        sum(weights[i] * triangle["positions"][i][k] for i in range(3))
        for k in range(3)
    )


def _sample_points(u0, v0, u1, v1):
    steps = CONTAINMENT_SAMPLES
    for i in range(steps + 1):
        for j in range(steps + 1):
            yield (u0 + (u1 - u0) * i / steps, v0 + (v1 - v0) * j / steps)


def _wall_normal(wall, center):
    """The wall's horizontal unit normal, signed to point onto the hall floor."""
    nx, nz = wall["triangles"][0]["normal"][0], wall["triangles"][0]["normal"][2]
    length = (nx * nx + nz * nz) ** 0.5
    nx, nz = nx / length, nz / length
    for sign in (1.0, -1.0):
        if glb_walls.inside_floor(
            center[0] + sign * NORMAL_PROBE * nx, center[2] + sign * NORMAL_PROBE * nz
        ):
            return [round(sign * nx, 6) + 0.0, 0.0, round(sign * nz, 6) + 0.0]
    raise ValueError("no side of the wall at %s faces the hall floor" % (center,))


def rect_to_world(rect, triangles):
    """Places a texture rectangle on its wall, 0.03 units into the room.

    Returns center, right, normal and size ([width, height]). `right` is such
    that normal x right is world up. Raises ValueError unless the rectangle lies
    wholly inside one wall in texture space.
    """
    u0, v0, u1, v1 = rect["uv"]
    if not (u0 < u1 and v0 < v1):
        raise ValueError("rect %s is empty: %s" % (rect.get("id"), rect["uv"]))

    for wall in _group_walls(triangles):
        points = [_uv_to_world(p, wall) for p in _sample_points(u0, v0, u1, v1)]
        if all(p is not None for p in points):
            break
    else:
        raise ValueError(
            "rect %s is not inside one wall: %s" % (rect.get("id"), rect["uv"])
        )

    mid = tuple(sum(p[k] for p in points) / len(points) for k in range(3))
    normal = _wall_normal(wall, mid)
    right = [normal[2], 0.0, -normal[0] + 0.0]

    # The texture is slightly skewed on some quads, so a rectangle maps to a
    # near-rectangle; its bounding box still covers all of it.
    along = [p[0] * right[0] + p[2] * right[2] for p in points]
    up = [p[1] for p in points]
    plane = sum(mid[k] * normal[k] for k in range(3))
    mid_along = (min(along) + max(along)) / 2
    mid_up = (min(up) + max(up)) / 2
    center = [
        right[0] * mid_along + normal[0] * (plane + WALL_OFFSET),
        mid_up,
        right[2] * mid_along + normal[2] * (plane + WALL_OFFSET),
    ]
    return {
        "center": [round(c, 5) + 0.0 for c in center],
        "right": right,
        "normal": normal,
        "size": [round(max(along) - min(along), 5), round(max(up) - min(up), 5)],
    }


def load_rects(path=RECTS_PATH):
    with open(path) as f:
        return json.load(f)["rects"]


def placed_rects(rects=None):
    """Every marked rectangle with its id and world placement."""
    triangles = glb_walls.load_wall_triangles(GLB_PATH)
    return [
        dict(id=rect["id"], **rect_to_world(rect, triangles))
        for rect in (load_rects() if rects is None else rects)
    ]


# --- Assignment -----------------------------------------------------------


def load_artists(directory=ARTISTS_DIR):
    """[{"id", "designs": [design id, ...]}], sorted by id."""
    artists = []
    for name in sorted(os.listdir(directory)):
        path = os.path.join(directory, name, "artist.json")
        if os.path.exists(path):
            with open(path) as f:
                designs = json.load(f)["designs"]
            artists.append({"id": name, "designs": [d["id"] for d in designs]})
    return artists


def _dot(a, b):
    return sum(a[k] * b[k] for k in range(3))


def _plane(frame):
    return _dot(frame["center"], frame["normal"])


def wall_key(frame):
    """Names the wall a frame hangs on: its facing, and its plane to the unit."""
    return (tuple(frame["normal"]), round(_plane(frame)))


def frames_near(a, b):
    """True when two frames share a wall and their edges are within 4 units."""
    if a["normal"] != b["normal"] or abs(_plane(a) - _plane(b)) >= SAME_WALL_MAX_GAP:
        return False
    across = abs(_dot(a["center"], a["right"]) - _dot(b["center"], a["right"]))
    high = abs(a["center"][1] - b["center"][1])
    gap_x = max(0.0, across - (a["size"][0] + b["size"][0]) / 2)
    gap_y = max(0.0, high - (a["size"][1] + b["size"][1]) / 2)
    return (gap_x * gap_x + gap_y * gap_y) ** 0.5 <= NEIGHBOUR_DISTANCE


def _try_assign(placed, artists, rng):
    """Greedy pass: the artist with most designs left who is not used nearby.

    Ties go to the artist with least on this wall, so works spread around the
    hall. Returns None when some frame has no artist left to take.
    """
    remaining = {a["id"]: list(a["designs"]) for a in artists}
    for designs in remaining.values():
        rng.shuffle(designs)
    order = list(placed)
    rng.shuffle(order)
    on_wall = {}
    paintings = []
    for frame in order:
        banned = {p["artist"] for p in paintings if frames_near(frame, p)}
        wall = wall_key(frame)
        candidates = [a for a in remaining if remaining[a] and a not in banned]
        if not candidates:
            return None
        rng.shuffle(candidates)
        artist = max(
            candidates,
            key=lambda a: (len(remaining[a]), -on_wall.get((a, wall), 0)),
        )
        on_wall[(artist, wall)] = on_wall.get((artist, wall), 0) + 1
        paintings.append(dict(frame, artist=artist, design=remaining[artist].pop()))

    walls = {}
    for painting in paintings:
        walls.setdefault(painting["artist"], set()).add(wall_key(painting))
    if any(len(seen) < 2 for seen in walls.values()):
        return None
    return sorted(paintings, key=lambda p: p["id"])


def assign_paintings(placed, artists, seed=ASSIGN_SEED):
    """One design per frame, using each design once. Same input, same output."""
    designs = sum(len(a["designs"]) for a in artists)
    if designs != len(placed):
        raise ValueError("%d designs for %d frames" % (designs, len(placed)))
    rng = random.Random(seed)
    for _ in range(ASSIGN_ATTEMPTS):
        paintings = _try_assign(placed, artists, rng)
        if paintings is not None:
            return paintings
    raise ValueError("no valid assignment in %d attempts" % ASSIGN_ATTEMPTS)


def write_paintings(paintings, path=PAINTINGS_PATH):
    keys = ("id", "center", "right", "normal", "size", "artist", "design")
    lines = [
        "    " + json.dumps({key: painting[key] for key in keys}) for painting in paintings
    ]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write('{\n  "paintings": [\n' + ",\n".join(lines) + "\n  ]\n}\n")


# --- Test-driver script ---------------------------------------------------

SCRIPTS_DIR = os.path.join(ROOT, "tests", "scripts")


def read_paintings(path=PAINTINGS_PATH):
    with open(path) as f:
        return json.load(f)["paintings"]


def driver_script(paintings, artists):
    """(script text, expected text): one aim/open/close visit per painting.

    Expected lines are tab separated: id, artist, 0-based design index.
    """
    index = {a["id"]: a["designs"] for a in artists}
    script = [
        "# Generated by tools/build_paintings.py --driver-script. Do not edit.",
        "# Run from build-test, then check the log with tests/check_every_painting.py.",
        "wait 1",
    ]
    expected = []
    for p in paintings:
        pid = p["id"]
        script += [
            "aim %s" % pid,
            "wait 0.3",
            "state %s_aimed" % pid,
            "key tap E",
            "wait 0.5",
            "state %s_open" % pid,
            "key tap Q",
            "wait 0.5",
            "state %s_closed" % pid,
        ]
        expected.append(
            "%s\t%s\t%d" % (pid, p["artist"], index[p["artist"]].index(p["design"]))
        )
    script.append("quit")
    return "\n".join(script) + "\n", "\n".join(expected) + "\n"


def write_driver_script(directory=SCRIPTS_DIR):
    script, expected = driver_script(read_paintings(), load_artists())
    for name, text in (("every_painting.txt", script), ("every_painting.expected", expected)):
        with open(os.path.join(directory, name), "w") as f:
            f.write(text)


# --- PNG, standard library only -------------------------------------------


def decode_png(data):
    """Returns (width, height, rows), rows being lists of [r, g, b] per pixel."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    offset = 8
    compressed = b""
    while offset < len(data):
        length, kind = struct.unpack_from(">I4s", data, offset)
        body = data[offset + 8 : offset + 8 + length]
        if kind == b"IHDR":
            width, height, depth, color, _, _, interlace = struct.unpack(">IIBBBBB", body)
            if depth != 8 or color not in (2, 6) or interlace:
                raise ValueError("unsupported PNG format")
            channels = 3 if color == 2 else 4
        elif kind == b"IDAT":
            compressed += body
        offset += 12 + length

    raw = zlib.decompress(compressed)
    stride = width * channels
    rows = []
    previous = bytearray(stride)
    position = 0
    for _ in range(height):
        kind = raw[position]
        line = bytearray(raw[position + 1 : position + 1 + stride])
        position += 1 + stride
        _unfilter(kind, line, previous, channels)
        rows.append(
            [list(line[x * channels : x * channels + 3]) for x in range(width)]
        )
        previous = line
    return width, height, rows


def _unfilter(kind, line, previous, bpp):
    if kind == 0:
        return
    for i in range(len(line)):
        a = line[i - bpp] if i >= bpp else 0
        b = previous[i]
        if kind == 1:
            line[i] = (line[i] + a) & 255
        elif kind == 2:
            line[i] = (line[i] + b) & 255
        elif kind == 3:
            line[i] = (line[i] + (a + b) // 2) & 255
        elif kind == 4:
            c = previous[i - bpp] if i >= bpp else 0
            p = a + b - c
            pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
            line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        else:
            raise ValueError("bad PNG filter %d" % kind)


def encode_png(rows):
    height = len(rows)
    width = len(rows[0])
    raw = bytearray()
    for row in rows:
        raw.append(0)
        for pixel in row:
            raw.extend(pixel)

    def chunk(kind, body):
        crc = zlib.crc32(kind + body) & 0xFFFFFFFF
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", crc)

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
        + chunk(b"IEND", b"")
    )


# --- Overlay --------------------------------------------------------------

DIGITS = {
    "0": "111101101101111",
    "1": "010110010010111",
    "2": "111001111100111",
    "3": "111001111001111",
    "4": "101101111001001",
    "5": "111100111001111",
    "6": "111100111101111",
    "7": "111001010010010",
    "8": "111101111101111",
    "9": "111101111001111",
}
OUTLINE_COLORS = ([255, 0, 255], [0, 255, 255], [255, 255, 0], [0, 255, 0])
GRID_COLOR = [255, 255, 255]
LABEL_COLOR = [255, 255, 255]
LABEL_BACKGROUND = [0, 0, 0]


def _set(rows, x, y, color):
    if 0 <= y < len(rows) and 0 <= x < len(rows[0]):
        rows[y][x] = list(color)


def _draw_text(rows, x, y, text, color, scale=1, background=None):
    if background is not None:
        for dy in range(-scale, 5 * scale + scale):
            for dx in range(-scale, len(text) * 4 * scale):
                _set(rows, x + dx, y + dy, background)
    for n, char in enumerate(text):
        glyph = DIGITS[char]
        for gy in range(5):
            for gx in range(3):
                if glyph[gy * 3 + gx] == "1":
                    for sy in range(scale):
                        for sx in range(scale):
                            _set(rows, x + n * 4 * scale + gx * scale + sx, y + gy * scale + sy, color)


def render_overlay(rects, crop=None, zoom=1, grid=0, label_scale=None):
    """The atlas, cropped and zoomed, with every rectangle outlined and numbered."""
    width, height, atlas = decode_png(glb_walls.load_emissive_png(GLB_PATH))
    x0, y0, x1, y1 = crop if crop else (0, 0, width, height)
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, width), min(y1, height)

    rows = []
    for y in range(y0, y1):
        line = [atlas[y][x] for x in range(x0, x1) for _ in range(zoom)]
        for _ in range(zoom):
            rows.append([list(p) for p in line])

    if grid:
        for gx in range(x0 - x0 % grid + grid, x1, grid):
            for py in range(0, len(rows), 2):
                _set(rows, (gx - x0) * zoom, py, GRID_COLOR)
        for gy in range(y0 - y0 % grid + grid, y1, grid):
            for px in range(0, len(rows[0]), 2):
                _set(rows, px, (gy - y0) * zoom, GRID_COLOR)

    scale = label_scale or (1 if zoom < 3 else 2)
    for index, rect in enumerate(rects):
        u0, v0, u1, v1 = rect["uv"]
        left = round((u0 * width - x0) * zoom)
        top = round((v0 * height - y0) * zoom)
        right = round((u1 * width - x0) * zoom)
        bottom = round((v1 * height - y0) * zoom)
        if right < 0 or bottom < 0 or left >= len(rows[0]) or top >= len(rows):
            continue
        color = OUTLINE_COLORS[index % len(OUTLINE_COLORS)]
        # The outline's outer pixel sits exactly on the rectangle's edge.
        for px in range(left, right):
            _set(rows, px, top, color)
            _set(rows, px, bottom - 1, color)
        for py in range(top, bottom):
            _set(rows, left, py, color)
            _set(rows, right - 1, py, color)
        number = rect["id"].lstrip("r").lstrip("0") or "0"
        _draw_text(rows, left + 2, top + 2, number, color, scale, LABEL_BACKGROUND)

    if grid:
        for gx in range(x0 - x0 % grid + grid, x1, grid):
            _draw_text(rows, (gx - x0) * zoom + 2, 2, str(gx), LABEL_COLOR, scale, LABEL_BACKGROUND)
        for gy in range(y0 - y0 % grid + grid, y1, grid):
            _draw_text(rows, 2, (gy - y0) * zoom + 2, str(gy), LABEL_COLOR, scale, LABEL_BACKGROUND)
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--overlay", metavar="OUT.png")
    mode.add_argument("--assign", action="store_true")
    mode.add_argument("--driver-script", action="store_true")
    parser.add_argument("--crop", nargs=4, type=int, metavar=("X0", "Y0", "X1", "Y1"))
    parser.add_argument("--zoom", type=int, default=1)
    parser.add_argument("--grid", type=int, default=0)
    parser.add_argument("--rects", default=RECTS_PATH)
    args = parser.parse_args(argv)

    if args.assign:
        paintings = assign_paintings(placed_rects(load_rects(args.rects)), load_artists())
        write_paintings(paintings)
        print("assigned %d paintings to %s" % (len(paintings), PAINTINGS_PATH))
        return 0

    if args.driver_script:
        write_driver_script()
        print("wrote every_painting.txt and every_painting.expected in %s" % SCRIPTS_DIR)
        return 0

    rects = load_rects(args.rects) if os.path.exists(args.rects) else []
    rows = render_overlay(rects, args.crop, args.zoom, args.grid)
    with open(args.overlay, "wb") as f:
        f.write(encode_png(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
