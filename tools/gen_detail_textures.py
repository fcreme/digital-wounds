#!/usr/bin/env python3
"""Generate the gallery's tiling detail texture (stdlib only, deterministic).

assets/textures/detail_wood.png is a 512x512 greyscale wood grain that tiles in both
directions. Its mean is exactly mid-grey (128), so mesh.frag can multiply it into the
baked room light as fine light-and-dark variation without changing overall brightness:
far away, mipmapping averages it back to 128, which is a factor of 1.

The grain runs along the image's vertical axis. Run from the repo root:
    python3 tools/gen_detail_textures.py
"""
import math
import os
import random
import struct
import sys
import zlib

SIZE = 512


def lattice(px, py, seed):
    rnd = random.Random(seed)
    return [[rnd.random() for _ in range(px)] for _ in range(py)]


def value_noise(grid, px, py, x, y):
    """Smooth value noise that wraps every px cells in x and py cells in y."""
    x0, y0 = math.floor(x), math.floor(y)
    fx, fy = x - x0, y - y0
    fx = fx * fx * (3 - 2 * fx)
    fy = fy * fy * (3 - 2 * fy)
    x0 %= px
    y0 %= py
    x1, y1 = (x0 + 1) % px, (y0 + 1) % py
    a = grid[y0][x0] + (grid[y0][x1] - grid[y0][x0]) * fx
    b = grid[y1][x0] + (grid[y1][x1] - grid[y1][x0]) * fx
    return a + (b - a) * fy


def wood(size=SIZE, seed=7):
    # Octaves with periods that divide evenly into the image, so every one tiles.
    # Grain: noise stretched 16:1 along y (long fibres), plus slow wavy growth rings.
    # Fibres have p cells across and p/16 cells down the tile, so each octave wraps exactly.
    fibre = [(lattice(p, p // 16, seed + i), p, w) for i, (p, w) in enumerate([(64, 0.5), (128, 0.3), (256, 0.2)])]
    rings = lattice(8, 8, seed + 10)
    wobble = lattice(4, 4, seed + 11)
    vals = []
    for py in range(size):
        v = py / size
        row = []
        for px in range(size):
            u = px / size
            f = 0.0
            for grid, period, weight in fibre:
                f += weight * value_noise(grid, period, period // 16, u * period, v * period / 16.0)
            # Growth rings: bands across u, bent by low-frequency noise; 24 bands per tile.
            bend = value_noise(wobble, 4, 4, u * 4, v * 4)
            ring = 0.5 + 0.5 * math.sin(2 * math.pi * (u * 24 + 0.8 * bend))
            ring = ring ** 3  # thin dark late-wood lines
            g = 0.75 * f + 0.25 * (1.0 - ring) + 0.04 * value_noise(rings, 8, 8, u * 8, v * 8)
            row.append(g)
        vals.append(row)
    # Normalise to mean 0.5 and a standard deviation of 0.11.
    flat = [g for row in vals for g in row]
    mean = sum(flat) / len(flat)
    std = math.sqrt(sum((g - mean) ** 2 for g in flat) / len(flat)) or 1.0
    out = bytearray()
    for row in vals:
        out.append(0)  # PNG filter: none
        for g in row:
            out.append(max(0, min(255, round(128 + 255 * 0.11 * (g - mean) / std))))
    # Exact mean 128 after rounding and clipping: nudge the brightest or darkest pixels.
    total = sum(out[i] for i in range(len(out)) if i % (size + 1))
    want = 128 * size * size
    step = 1 if total < want else -1
    i = 0
    while total != want and i < 20 * len(out):
        k = i % len(out)
        i += 1
        if k % (size + 1) == 0:
            continue
        nv = out[k] + step
        if 0 <= nv <= 255 and ((step > 0 and out[k] < 128) or (step < 0 and out[k] > 128)):
            out[k] = nv
            total += step
    return bytes(out)


def write_grey_png(path, size, raw):
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 0, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    out = os.path.join("assets", "textures", "detail_wood.png")
    if not os.path.isdir("assets"):
        sys.exit("run from the repo root")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    write_grey_png(out, SIZE, wood())
    print("wrote", out)


if __name__ == "__main__":
    main()
