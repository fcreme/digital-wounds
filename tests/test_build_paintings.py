"""Tests for mapping marked texture rectangles to world positions.

Run from the repo root: python3 -m unittest tests/test_build_paintings.py
"""

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import build_paintings  # noqa: E402
import glb_walls  # noqa: E402

GLB = os.path.join(ROOT, "props", "the_picture_gallery_low_poly__vr.glb")


def px(x0, y0, x1, y1):
    """A rect dict from texture pixel coordinates."""
    return {"id": "t", "uv": [x0 / 1024, y0 / 1024, x1 / 1024, y1 / 1024]}


class RectToWorld(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.triangles = glb_walls.load_wall_triangles(GLB)

    def world(self, rect):
        return build_paintings.rect_to_world(rect, self.triangles)

    def test_rect_on_known_wall_maps_to_expected_world_position(self):
        # West wall: x=-10, z from -33.24 to -7.49, y 0 to about 10.9, on
        # u 0.58..0.72, v 0.19..0.52. Height runs along u, floor at the high u.
        u = (597 + 739) / 2 / 1024
        v = (192 + 528) / 2 / 1024
        d = 0.01
        result = self.world({"id": "t", "uv": [u - d, v - d, u + d, v + d]})
        self.assertAlmostEqual(result["center"][0], -9.97, places=4)
        self.assertAlmostEqual(result["center"][2], (-33.24 - 7.49) / 2, delta=0.1)
        self.assertAlmostEqual(result["center"][1], 5.45, delta=0.1)

    def test_size_comes_out_in_world_units_with_width_along_the_wall(self):
        # 13.04 pixels per world unit on this wall; 26 px of v is 2 units of z
        # and 13 px of u is 1 unit of height.
        result = self.world(px(650, 300, 663, 326))
        self.assertAlmostEqual(result["size"][0], 26 * 25.75 / 336, delta=0.02)
        self.assertAlmostEqual(result["size"][1], 13 * 10.9 / 142, delta=0.02)
        self.assertEqual(result["right"][1], 0.0)

    def test_normal_faces_into_the_room(self):
        # Ruling replacing dot(normal, hall_centre - center) > 0: a point 0.3
        # units along the normal from the centre must fall inside the floor.
        for rect in (
            px(650, 300, 680, 340),  # west wall
            px(800, 400, 830, 440),  # east wall, far half
            px(800, 800, 830, 840),  # east wall, near half
            px(800, 100, 830, 140),  # north wall
            px(950, 100, 980, 140),  # south wall
            px(50, 100, 70, 120),    # notch back wall
        ):
            result = self.world(rect)
            probe = [result["center"][i] + 0.3 * result["normal"][i] for i in range(3)]
            self.assertTrue(
                glb_walls.inside_floor(probe[0], probe[2]), (rect["uv"], result)
            )

    def test_normal_on_notch_end_faces_points_away_from_hall_centre(self):
        # These two faces look away from the hall centre, which is why the
        # floor outline decides the sign and not the centre.
        south_of_notch = self.world(px(885, 400, 900, 440))  # z = 2.08
        self.assertAlmostEqual(south_of_notch["center"][2], 2.08 + 0.03, delta=0.005)
        self.assertEqual(south_of_notch["normal"], [0.0, 0.0, 1.0])
        north_of_notch = self.world(px(885, 540, 900, 580))  # z = -7.49
        self.assertAlmostEqual(north_of_notch["center"][2], -7.49 - 0.03, delta=0.005)
        self.assertEqual(north_of_notch["normal"], [0.0, 0.0, -1.0])

    def test_up_derived_from_normal_and_right_is_world_up(self):
        # PaintingData computes up = normal x right; a frame must not be flipped.
        for rect in (
            px(650, 300, 680, 340),
            px(800, 400, 830, 440),
            px(800, 100, 830, 140),
            px(950, 100, 980, 140),
            px(885, 400, 900, 440),
        ):
            r = self.world(rect)
            n, h = r["normal"], r["right"]
            up = [
                n[1] * h[2] - n[2] * h[1],
                n[2] * h[0] - n[0] * h[2],
                n[0] * h[1] - n[1] * h[0],
            ]
            self.assertEqual([round(c, 6) for c in up], [0.0, 1.0, 0.0])

    def test_rect_outside_any_wall_raises(self):
        for rect in (
            px(100, 400, 150, 450),  # floor
            px(500, 100, 550, 150),  # empty texture area
            px(400, 400, 420, 420),  # ceiling
            px(960, 500, 1000, 540),  # empty, right of the notch faces
        ):
            with self.assertRaises(ValueError):
                self.world(rect)

    def test_rect_crossing_two_walls_in_texture_space_raises(self):
        # North wall ends and east wall begins at v=317; the atlas places them
        # edge to edge but they are different walls.
        with self.assertRaises(ValueError):
            self.world(px(800, 300, 830, 330))

    def test_rect_hanging_past_a_wall_edge_raises(self):
        with self.assertRaises(ValueError):
            self.world(px(800, 5, 830, 40))  # north wall starts at v=17

    def test_rect_spanning_two_triangles_of_a_wall_works(self):
        # Centred on the north wall's diagonal.
        result = self.world(px(790, 150, 830, 190))
        self.assertAlmostEqual(result["center"][2], -33.24 + 0.03, delta=0.005)
        self.assertGreater(result["size"][0], 0)

    def test_rect_spanning_two_quads_of_a_wall_works(self):
        # West wall quads meet at v=528, the texture is continuous across it.
        result = self.world(px(610, 480, 670, 560))
        self.assertAlmostEqual(result["center"][0], -9.97, places=4)


class MarkedRects(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.triangles = glb_walls.load_wall_triangles(GLB)
        cls.rects = build_paintings.load_rects()

    def test_every_rect_lies_inside_one_wall_facing_the_floor(self):
        for rect in self.rects:
            result = build_paintings.rect_to_world(rect, self.triangles)
            probe = [result["center"][i] + 0.3 * result["normal"][i] for i in range(3)]
            self.assertTrue(glb_walls.inside_floor(probe[0], probe[2]), rect["id"])
            self.assertGreater(result["center"][1], 0.0, rect["id"])

    def test_ids_are_unique(self):
        ids = [rect["id"] for rect in self.rects]
        self.assertEqual(len(ids), len(set(ids)))

    def test_adjacent_frames_overlap_by_at_most_two_pixels(self):
        for i, a in enumerate(self.rects):
            for b in self.rects[i + 1 :]:
                x = min(a["uv"][2], b["uv"][2]) - max(a["uv"][0], b["uv"][0])
                y = min(a["uv"][3], b["uv"][3]) - max(a["uv"][1], b["uv"][1])
                self.assertLessEqual(
                    min(x, y) * 1024, 2.01, "%s and %s" % (a["id"], b["id"])
                )


class Assignment(unittest.TestCase):
    """The assignment over the real rectangles, with a catalog made up here."""

    @classmethod
    def setUpClass(cls):
        cls.placed = build_paintings.placed_rects()
        count = len(cls.placed)
        # 20 artists with 5 or 6 designs each, as the real catalog has.
        sizes = [count // 20 + (1 if i < count % 20 else 0) for i in range(20)]
        cls.artists = [
            {"id": "a%02d" % i, "designs": ["d%d" % d for d in range(size)]}
            for i, size in enumerate(sizes)
        ]
        cls.paintings = build_paintings.assign_paintings(cls.placed, cls.artists)

    def test_every_rect_gets_exactly_one_design(self):
        self.assertEqual(
            sorted(p["id"] for p in self.paintings),
            sorted(r["id"] for r in self.placed),
        )
        used = sorted((p["artist"], p["design"]) for p in self.paintings)
        everything = sorted(
            (a["id"], d) for a in self.artists for d in a["designs"]
        )
        self.assertEqual(used, everything)

    def test_painting_keeps_its_rect_placement(self):
        placed = {r["id"]: r for r in self.placed}
        for painting in self.paintings:
            for key in ("center", "right", "normal", "size"):
                self.assertEqual(painting[key], placed[painting["id"]][key])

    def test_same_artist_not_side_by_side(self):
        # Distance is between frame edges, so that a wide frame's next-door
        # neighbour counts even when their centres are more than 4 units apart.
        for i, a in enumerate(self.paintings):
            for b in self.paintings[i + 1 :]:
                if build_paintings.frames_near(a, b):
                    self.assertNotEqual(a["artist"], b["artist"], (a["id"], b["id"]))

    def test_frames_near_measures_edges_on_the_same_wall_only(self):
        def frame(x, z=0.0, width=2.0, normal=(0.0, 0.0, 1.0)):
            return {
                "center": [x, 5.0, z],
                "right": [normal[2], 0.0, -normal[0]],
                "normal": list(normal),
                "size": [width, 2.0],
            }

        # Centres 7 apart, edges 3 apart.
        self.assertTrue(build_paintings.frames_near(frame(0.0, width=8.0), frame(7.0)))
        self.assertFalse(build_paintings.frames_near(frame(0.0), frame(7.0)))
        # Opposite walls, facing each other across the hall.
        self.assertFalse(
            build_paintings.frames_near(
                frame(0.0), frame(0.0, z=5.0, normal=(0.0, 0.0, -1.0))
            )
        )
        # Same direction, but set back on another plane.
        self.assertFalse(build_paintings.frames_near(frame(0.0), frame(0.0, z=3.0)))

    def test_assignment_is_deterministic(self):
        self.assertEqual(
            build_paintings.assign_paintings(self.placed, self.artists), self.paintings
        )

    def test_each_artist_appears_on_at_least_two_walls(self):
        walls = {}
        for painting in self.paintings:
            walls.setdefault(painting["artist"], set()).add(
                build_paintings.wall_key(painting)
            )
        self.assertEqual(len(walls), 20)
        for artist, seen in walls.items():
            self.assertGreaterEqual(len(seen), 2, artist)

    def test_too_few_designs_is_an_error(self):
        with self.assertRaises(ValueError):
            build_paintings.assign_paintings(
                self.placed, [{"id": "a", "designs": ["d"]}]
            )


class RealAssets(unittest.TestCase):
    """The committed museum.json is what --assign produces from committed artists."""

    def test_museum_json_matches_a_fresh_assignment(self):
        with open(build_paintings.PAINTINGS_PATH) as f:
            committed = json.load(f)["paintings"]
        fresh = build_paintings.assign_paintings(
            build_paintings.placed_rects(), build_paintings.load_artists()
        )
        self.assertEqual(committed, fresh)

    def test_room_names_the_paintings_file(self):
        with open(os.path.join(ROOT, "assets", "rooms", "museum.json")) as f:
            self.assertEqual(json.load(f)["paintings"], "assets/paintings/museum.json")


class PngRoundTrip(unittest.TestCase):
    def test_encoded_png_decodes_to_the_same_pixels(self):
        rows = [[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]]
        self.assertEqual(
            build_paintings.decode_png(build_paintings.encode_png(rows)), (2, 2, rows)
        )


class DriverScript(unittest.TestCase):
    PAINTINGS = [{"id": "r001", "artist": "a", "design": "y"}]
    ARTISTS = [{"id": "a", "designs": ["x", "y"]}]

    def test_every_painting_is_visited_and_expected_by_design_index(self):
        script, expected = build_paintings.driver_script(self.PAINTINGS, self.ARTISTS)
        self.assertIn("aim r001\n", script)
        self.assertIn("state r001_open\n", script)
        self.assertEqual(expected, "r001\ta\t1\n")

    def test_checker_lists_mismatches_and_counts_passes(self):
        sys.path.insert(0, os.path.join(ROOT, "tests"))
        import check_every_painting as check

        good = (
            "DRIVER state r001_aimed near=r001(a#1) view=closed artist=none page=0\n"
            "DRIVER state r001_open near=none view=open artist=a page=1\n"
            "DRIVER state r001_closed near=r001(a#1) view=closed artist=none page=0\n"
        )
        self.assertEqual(check.check(good, "r001\ta\t1\n")[:2], (1, 1))
        bad = good.replace("near=r001(a#1) view=closed artist=none page=0\nDRIVER state r001_open", "near=none view=closed artist=none page=0\nDRIVER state r001_open")
        passed, total, failures = check.check(bad, "r001\ta\t1\n")
        self.assertEqual((passed, total, len(failures)), (0, 1, 1))
        self.assertIn("near=none", failures[0])


if __name__ == "__main__":
    unittest.main()
