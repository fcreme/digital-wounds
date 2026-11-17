#!/usr/bin/env python3
"""Checks the shots from tests/scripts/wall_closeup.txt show the wall, not black.

cd build-test && ./digital_wounds --script ../tests/scripts/wall_closeup.txt > walls.log 2>&1
python3 ../tests/check_wall_closeup.py shots

Each shot has a region where the nearby wall must appear. The check fails when
that region's mean brightness is below MIN_BRIGHTNESS out of 255. Exits 1 on any
failure.
"""

import os
import struct
import sys

MIN_BRIGHTNESS = 20.0

# Shot name -> region (left, top, right, bottom) as fractions of the frame,
# measured from the top-left corner.
REGIONS = {
    "west_facing": (0.25, 0.2, 0.75, 0.7),
    "west_along": (0.7, 0.1, 0.95, 0.8),
    "notch_facing": (0.25, 0.2, 0.75, 0.7),
}


def _channel_shift(mask):
    shift = 0
    while mask and not mask & 1:
        mask >>= 1
        shift += 1
    return shift


def read_bmp(path):
    """(width, height, pixel(x, y) -> (r, g, b)) for a 32-bit BMP, top-left origin."""
    with open(path, "rb") as f:
        data = f.read()
    offset = struct.unpack_from("<I", data, 10)[0]
    width, height = struct.unpack_from("<ii", data, 18)
    bits, compression = struct.unpack_from("<HI", data, 28)
    if bits != 32:
        raise ValueError("%s: %d-bit BMP, want 32" % (path, bits))
    if compression == 3:  # BI_BITFIELDS: the masks follow the 40-byte header
        masks = struct.unpack_from("<III", data, 54)
    else:
        masks = (0x00FF0000, 0x0000FF00, 0x000000FF)
    shifts = [_channel_shift(m) for m in masks]
    bottom_up = height > 0
    height = abs(height)

    def pixel(x, y):
        row = height - 1 - y if bottom_up else y
        value = struct.unpack_from("<I", data, offset + (row * width + x) * 4)[0]
        return tuple((value >> s) & 0xFF for s in shifts)

    return width, height, pixel


def mean_brightness(path, region, step=4):
    width, height, pixel = read_bmp(path)
    left, top, right, bottom = region
    total = 0
    count = 0
    for y in range(int(top * height), int(bottom * height), step):
        for x in range(int(left * width), int(right * width), step):
            r, g, b = pixel(x, y)
            total += (r + g + b) / 3.0
            count += 1
    return total / count


def check(shot_dir):
    """Returns a list of failure messages, one per dark or missing shot."""
    failures = []
    for name, region in REGIONS.items():
        path = os.path.join(shot_dir, name + ".bmp")
        if not os.path.exists(path):
            failures.append("%s: shot missing" % name)
            continue
        brightness = mean_brightness(path, region)
        if brightness < MIN_BRIGHTNESS:
            failures.append(
                "%s: wall region brightness %.1f, want at least %.0f"
                % (name, brightness, MIN_BRIGHTNESS)
            )
        else:
            print("ok   %s: wall region brightness %.1f" % (name, brightness))
    return failures


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    failures = check(argv[1])
    for failure in failures:
        print("FAIL " + failure)
    print("%d of %d passed" % (len(REGIONS) - len(failures), len(REGIONS)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
