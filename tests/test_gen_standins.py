"""Tests for the stand-in artist catalog and its generated assets.

Run from the repo root: python3 -m unittest tests/test_gen_standins.py
"""

import json
import os
import struct
import sys
import tempfile
import unittest
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import build_paintings  # noqa: E402
import gen_standins  # noqa: E402

CONFIG = os.path.join(ROOT, "public", "data", "artists", "dark-ink", "config.json")
LIMITS = {"name": 28, "artist": 120, "title": 40, "design": 200}


def read_png(data):
    """(width, height, depth, colour, interlace, palette, rows) for our own PNGs."""
    offset = 8
    palette = b""
    packed = b""
    while offset < len(data):
        length, kind = struct.unpack_from(">I4s", data, offset)
        body = data[offset + 8 : offset + 8 + length]
        if kind == b"IHDR":
            width, height, depth, colour, _, _, interlace = struct.unpack(">IIBBBBB", body)
        elif kind == b"PLTE":
            palette = body
        elif kind == b"IDAT":
            packed += body
        offset += 12 + length
    raw = zlib.decompress(packed)
    rows = [raw[y * (width + 1) + 1 : (y + 1) * (width + 1)] for y in range(height)]
    return width, height, depth, colour, interlace, palette, rows


def legal(text):
    return all(32 <= ord(ch) <= 122 and ch != "&" for ch in text)


class Catalog(unittest.TestCase):
    def test_twenty_artists_with_unique_ids(self):
        ids = [artist["id"] for artist in gen_standins.ARTISTS]
        self.assertEqual(len(ids), 20)
        self.assertEqual(len(set(ids)), 20)
        self.assertIn("dark-ink", ids)

    def test_dark_ink_keeps_its_text_and_first_four_designs(self):
        with open(CONFIG) as f:
            config = json.load(f)
        artist = next(a for a in gen_standins.ARTISTS if a["id"] == "dark-ink")
        self.assertEqual(artist["name"], config["title"])
        self.assertEqual(artist["description"], config["description"])
        for design, page in zip(artist["designs"], config["pages"][:4]):
            self.assertEqual(design["title"], page["title"])
            self.assertEqual(design["description"], page["description"])

    def test_text_fits_the_catalog_limits_and_character_set(self):
        for artist in gen_standins.ARTISTS:
            self.assertLessEqual(len(artist["name"]), LIMITS["name"], artist["id"])
            self.assertLessEqual(len(artist["description"]), LIMITS["artist"], artist["id"])
            self.assertTrue(legal(artist["name"] + artist["description"]), artist["id"])
            for design in artist["designs"]:
                self.assertLessEqual(len(design["title"]), LIMITS["title"], design["id"])
                self.assertLessEqual(len(design["description"]), LIMITS["design"], design["id"])
                self.assertTrue(legal(design["title"] + design["description"]), design["id"])

    def test_every_design_has_its_own_id_title_and_drawing(self):
        designs = [d for a in gen_standins.ARTISTS for d in a["designs"]]
        for key in ("title", "draw"):
            self.assertEqual(len({d[key] for d in designs}), len(designs), key)
        for artist in gen_standins.ARTISTS:
            ids = [d["id"] for d in artist["designs"]]
            self.assertEqual(len(ids), len(set(ids)), artist["id"])

    def test_same_design_renders_identical_bytes(self):
        artist = gen_standins.ARTISTS[1]
        first = gen_standins.render(artist["id"], artist["designs"][0])
        self.assertEqual(first, gen_standins.render(artist["id"], artist["designs"][0]))


class GeneratedAssets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The generator's own output, in a temporary folder: the committed
        # assets/artists is hand-editable data and is not read here.
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.directory = os.path.join(cls.temp.name, "artists")
        gen_standins.generate(cls.directory)
        cls.images = []
        for artist in gen_standins.ARTISTS:
            for design in artist["designs"]:
                path = os.path.join(cls.directory, artist["id"], design["id"] + ".png")
                with open(path, "rb") as f:
                    cls.images.append((artist["id"] + "/" + design["id"], read_png(f.read())))

    def test_design_counts_cover_the_rects_as_evenly_as_possible(self):
        counts = []
        for artist in gen_standins.ARTISTS:
            with open(os.path.join(self.directory, artist["id"], "artist.json")) as f:
                counts.append(len(json.load(f)["designs"]))
        self.assertEqual(sum(counts), len(build_paintings.load_rects()))
        self.assertLessEqual(max(counts) - min(counts), 1)

    def test_artist_json_matches_the_catalog(self):
        for artist in gen_standins.ARTISTS:
            with open(os.path.join(self.directory, artist["id"], "artist.json")) as f:
                written = json.load(f)
            self.assertEqual(written, gen_standins.artist_json(artist))

    def test_images_are_flat_non_interlaced_8_bit_on_the_paper_colour(self):
        for name, (width, height, depth, colour, interlace, palette, _) in self.images:
            self.assertEqual((width, height), (1024, 1024), name)
            self.assertEqual((depth, colour, interlace), (8, 3, 0), name)
            self.assertEqual(palette[:3], bytes((0xE6, 0xDC, 0xC8)), name)

    def test_design_has_real_ink_and_stays_inside_its_image(self):
        border = 24
        for name, (_, height, _, _, _, _, rows) in self.images:
            for row in rows[:border] + rows[-border:]:
                self.assertEqual(row.count(0), len(row), name + " touches top or bottom")
            for row in rows:
                self.assertEqual(row[:border].count(0), border, name + " touches left")
                self.assertEqual(row[-border:].count(0), border, name + " touches right")
            total = sum(len(row) - row.count(0) for row in rows)
            coverage = total / (height * height)
            self.assertGreater(coverage, 0.02, name + " is nearly blank")
            self.assertLess(coverage, 0.85, name + " is nearly solid")


if __name__ == "__main__":
    unittest.main()
