#!/usr/bin/env python3
"""Generates the stand-in tattoo artists shown on the gallery walls.

python3 tools/gen_standins.py
    writes assets/artists/<id>/artist.json and one PNG per design. Each artist
    has their own drawing vocabulary (see tools/flash_*.py). Output is identical
    between runs: every design's random numbers are seeded from its own name.

python3 tools/gen_standins.py --contact OUT.png
    also writes a numbered sheet of every design, one row per artist.
"""

import argparse
import json
import multiprocessing
import os
import random
import shutil
import struct
import sys
import time
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import flash_a as a  # noqa: E402
import flash_b as b  # noqa: E402
import flash_c as c  # noqa: E402
import ink  # noqa: E402
from build_paintings import DIGITS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTISTS_DIR = os.path.join(ROOT, "assets", "artists")
DARK_INK_CONFIG = os.path.join(ROOT, "public", "data", "artists", "dark-ink", "config.json")


def _design(draw, slug, title, description):
    return {"id": slug, "title": title, "description": description, "draw": draw}


def _artist(slug, name, style, description, designs):
    return {"id": slug, "name": name, "style": style, "description": description,
            "designs": [_design(*d) for d in designs]}


def _dark_ink():
    """Name, description and first four designs come from the site's own config."""
    with open(DARK_INK_CONFIG) as f:
        config = json.load(f)
    drawings = (
        (a.ravens_eye, "ravens-eye"),
        (a.bone_garden, "bone-garden"),
        (a.serpents_embrace, "serpents-embrace"),
        (a.shadow_forest, "shadow-forest"),
    )
    designs = [
        (draw, slug, page["title"], page["description"])
        for (draw, slug), page in zip(drawings, config["pages"][:4])
    ]
    designs += [
        (a.moth_sigil, "moth-sigil", "Moth Sigil",
         "A death's-head moth in solid black, its veins cut back to bare skin. A night visitor for the chest or throat."),
        (a.hollow_crown, "hollow-crown", "Hollow Crown",
         "A black crown set over a dark sun with a hollow eye. Heavy blackwork for those who rule nothing at all."),
    ]
    return _artist("dark-ink", config["title"], "Occult blackwork", config["description"], designs)


ARTISTS = [
    _dark_ink(),
    _artist("thimble-moonwhisker", "Thimble Moonwhisker", "Fine-line botanicals",
            "Single-needle plants drawn the way a very small botanist would, one patient hairline at a time.",
            [(a.fern_frond, "fern-frond", "Fern Frond", "A curling frond with every leaflet ruled in by hand. Delicate enough for a wrist or a collarbone."),
             (a.poppy_stem, "poppy-stem", "Poppy and Seed Head", "An open poppy beside its seed head, all thin line and no fill. Sits well along the forearm."),
             (a.foxglove_spire, "foxglove-spire", "Foxglove Spire", "A tall spire of freckled bells, narrow and vertical, made for the ribs or the back of a calf."),
             (a.moon_thistle, "moon-thistle", "Moon Thistle", "A prickly thistle in bloom against a thin crescent moon. Soft line, sharp plant."),
             (a.forest_caps, "forest-caps", "Forest Caps", "Three spotted toadstools on a tuft of grass. A small woodland scene for the ankle."),
             (a.wild_sprig_wreath, "wild-sprig-wreath", "Wild Sprig Wreath", "A round wreath of leaves and tiny blossoms around one quiet flower.")]),
    _artist("madame-zircon-dotsworth", "Madame Zircon Dotsworth", "Dotwork mandalas",
            "Sacred geometry built from a hundred thousand dots. She claims to have counted every one of them.",
            [(a.lotus_mandala, "lotus-mandala", "Lotus Mandala", "Rings of stippled petals opening from a black centre. A classic for the back of the hand or the sternum."),
             (a.sun_wheel, "sun-wheel", "Sun Wheel", "A dot-shaded disc with a wheel of triangles at its heart and rays like black blades."),
             (a.flower_of_life, "flower-of-life", "Flower of Life", "The old six-petal lattice, darkening in dots towards its rim, inside a ring of thorns."),
             (a.sri_triangles, "sri-triangles", "Nested Triangles", "Interlocked triangles descending to one black point, every band shaded with stipple."),
             (a.moon_mandala, "moon-mandala", "Moon Mandala", "A stippled moon circled by every phase and eight small stars. For night owls."),
             (a.stippled_orb, "stippled-orb", "Stippled Orb", "A dot-shaded sphere bound in three crossing orbits, with scattered stars around it.")]),
    _artist("captain-inkbeard", "Captain Barnaby Inkbeard", "Traditional bold flash",
            "Thick lines, whip shading and solid black, in the old sailor manner. Holds up from across the harbour.",
            [(a.swallow, "swallow", "Homeward Swallow", "A swooping swallow, the old mark of a sailor due back home. Bold wings and four small stars."),
             (a.lucky_anchor, "lucky-anchor", "Rope and Anchor", "A heavy anchor wrapped in rope, with whip-shaded arms. The steady classic for the upper arm."),
             (a.dagger_heart, "dagger-heart", "Dagger Through the Heart", "A dagger driven through a whip-shaded heart with three drops falling. Loyal, dramatic, a bit much."),
             (a.bold_rose, "bold-rose", "Old Harbour Rose", "A round traditional rose with half-black leaves. Fills a shoulder cap or the back of a hand."),
             (a.lucky_horseshoe, "lucky-horseshoe", "Lucky Horseshoe", "A nailed horseshoe holding a black star, for those who need the odds on their side."),
             (a.rattler_coil, "rattler-coil", "Rattler Coil", "A diamond-backed snake coiling up to a blunt black head, tail rattling behind it.")]),
    _artist("filigree-von-curlicue", "Filigree Von Curlicue", "Ornamental linework",
            "Mirrored scrollwork, lace and wrought iron. Nothing here is plain, and nothing has ever been plain.",
            [(a.damask_medallion, "damask-medallion", "Damask Medallion", "Heart-shaped scrolls stacked inside a double-lined medallion. Symmetrical work for the sternum."),
             (a.lace_collar, "lace-collar", "Lace Collar", "A necklace of lace with spoked rosettes and a single pendant, drawn to follow the collarbone."),
             (a.empty_cartouche, "empty-cartouche", "Empty Cartouche", "A baroque frame of curling scrolls, left empty on purpose. What goes inside is your problem."),
             (a.chandelier_drop, "chandelier-drop", "Chandelier Drop", "A ballroom chandelier with six candles and a beaded swag. Hangs well from the sternum down."),
             (a.wrought_gate, "wrought-gate", "Wrought Gate", "An arched iron gate full of paired scrolls under a crown of leaves. Good on the forearm."),
             (a.spade_finial, "spade-finial", "Spade Finial", "A tall spade outline filled with scrollwork, like the top of an old garden railing.")]),
    _artist("blackfang-zuzubar", "Blackfang Zuzubar", "Blade-shape tribal",
            "Solid black shapes with no outline and no mercy. Every curve ends in a point.",
            [(b.tribal_sun, "tribal-sun", "Swirling Sun", "Ten curved blades spinning around a starred ring. Solid black and readable from far away."),
             (b.hook_spiral, "hook-spiral", "Hook Spiral", "One thick spiral tapering to nothing, barbed along its outer edge. Wraps a shoulder well."),
             (b.fang_heart, "fang-heart", "Fang Heart", "A heart built from two fanged curves that nearly meet. Mirrored, sharp and heavy."),
             (b.twin_flames, "twin-flames", "Twin Flames", "Mirrored black flames rising from a single point. Made for the centre of the back."),
             (b.manta_glide, "manta-glide", "Manta Glide", "A manta ray drawn as sweeping blades with cut-out highlights and a long thin tail.")]),
    _artist("old-quillon-burinsnout", "Old Quillon Burinsnout", "Engraving lines",
            "Everything is shaded with swelling parallel lines, as on old banknotes. Says he dislikes curves, draws them anyway.",
            [(b.sperm_whale, "sperm-whale", "Sperm Whale", "A whale in banknote lines, heavy on the belly, blowing over three wavering lines of sea."),
             (b.alpine_range, "alpine-range", "Alpine Range", "Three peaks with engraved shadow faces and white caps, and a rayed sun behind them."),
             (b.lighthouse, "lighthouse", "Lighthouse", "A banded tower on a rock, its two beams ruled out across the dark. For the ones who stayed ashore."),
             (b.engraved_moon, "engraved-moon", "Engraved Moon", "A full cratered moon in curving lines that swell into its shadow, ringed by small stars."),
             (b.bronze_bell, "bronze-bell", "Bronze Bell", "A ship's bell shaded like a coin, mid-swing, with its clapper showing below the lip."),
             (b.windfall_pear, "windfall-pear", "Windfall Pear", "One heavy pear and one leaf, shaded only with line. Humble subject, a lot of patience.")]),
    _artist("professor-hatchwick-gloom", "Professor Hatchwick Gloom", "Macabre cross-hatching",
            "Pen hatching, layer on layer, until it looks like an old book of bad news.",
            [(b.hatched_skull, "hatched-skull", "Cracked Skull", "A skull built up in crossing pen strokes, with hollow black sockets and a cracked crown."),
             (b.hourglass_vigil, "hourglass-vigil", "Hourglass Vigil", "An hourglass in a beaded frame with most of its sand already down. A familiar reminder."),
             (b.guttering_candle, "guttering-candle", "Guttering Candle", "A dripping candle stub in a tin holder, almost finished, flame still going."),
             (b.nailed_coffin, "nailed-coffin", "Nailed Coffin", "A six-sided coffin with hatched side, a solid cross and eight careful nails."),
             (b.belfry_bat, "belfry-bat", "Belfry Bat", "A densely hatched bat with its wings spread above a small crescent moon."),
             (b.poison_bottle, "poison-bottle", "Poison Bottle", "A corked apothecary bottle with skull and bones on the label, bubbling slightly.")]),
    _artist("polygonzo-the-faceted", "Polygonzo the Faceted", "Low-poly geometric",
            "Refuses to acknowledge curves. Animals and gems cut into triangles of hatching, dots and solid black.",
            [(b.fox_mask, "fox-mask", "Fox Mask", "A fox's face in folded triangles, every facet with its own shading. Good on the thigh."),
             (b.wolf_mask, "wolf-mask", "Wolf Mask", "A long-jawed wolf in hard facets of black, hatch and stipple, staring straight ahead."),
             (b.owl_mask, "owl-mask", "Owl Mask", "An owl made of angles, with two eight-sided eyes that seem to follow you down the hall."),
             (b.cut_diamond, "cut-diamond", "Cut Diamond", "A brilliant-cut gem seen side on, each facet shaded differently, with a few small glints."),
             (b.icosa_cage, "icosa-cage", "Twenty Sides", "A many-sided solid with its faces in black, hatch and dots. Pure geometry, no animals harmed.")]),
    _artist("koi-whisperer-of-mu", "The Koi Whisperer of Mu", "Japanese-style bold",
            "Swept black bars, overlapping scales and curling water. Listens to fish, and reports they have opinions.",
            [(b.koi_ascending, "koi-ascending", "Koi Ascending", "A scaled koi climbing upstream between swept black bars, with little rings of water around it."),
             (b.peony_bloom, "peony-bloom", "Peony in Full Bloom", "A wide peony of many ruffled layers on dark leaves. Fills a shoulder or the outer thigh."),
             (b.great_wave, "great-wave", "Rising Wave", "A curling wave breaking over a sea of scale pattern, spray flying under a crescent moon."),
             (b.sakura_bough, "sakura-bough", "Blossom Bough", "A black branch heavy with notched blossoms and a few loose petals on their way down."),
             (b.cloud_knot, "cloud-knot", "Moon and Clouds", "Three curling cloud banks sliding across a large stippled moon. Calm work for the upper arm."),
             (b.seigaiha_fan, "seigaiha-fan", "Wave-Pattern Fan", "An open folding fan patterned with overlapping wave scales, its tassel trailing below.")]),
    _artist("wobbly-pim", "Wobbly Pim Scribblesworth", "Naive marker doodles",
            "Wonky marker drawings of unhappy things. Every shaky line is on purpose, or at least he says so.",
            [(b.sad_ghost, "sad-ghost", "Sad Ghost", "A ghost with crossed-out eyes and a single tear. Going through something. Fits behind a knee."),
             (b.grumpy_cat, "grumpy-cat", "Furious Cat", "A cat who has just been told something and does not agree with it. Very good on a shin."),
             (b.happy_cactus, "happy-cactus", "Pleased Cactus", "A small potted cactus with a small smile. Scribbled pot, flower on top, no idea why it is happy."),
             (b.toothy_flower, "toothy-flower", "Toothy Flower", "A cheerful daisy with far too many teeth. Do not water it after dark."),
             (b.little_bomb, "little-bomb", "Little Bomb", "A scribbled round bomb, fuse lit, looking delighted about it."),
             (b.speedy_snail, "speedy-snail", "Speedy Snail", "A snail at full speed, with motion lines to prove it. For someone in no hurry at all.")]),
    _artist("pokey-pixie-pinprick", "Pokey Pixie Pinprick", "Stick-and-poke dots",
            "No machine, one needle. Every line is a row of separate dots you could count, if you have the afternoon.",
            [(b.poked_heart, "poked-heart", "Poked Heart", "A double-lined heart in single dots, half filled with an even grid of more dots."),
             (b.moon_and_pins, "moon-and-pins", "Moon and Pins", "A dotted crescent moon with a handful of tiny stars caught in its curve."),
             (b.poked_dagger, "poked-dagger", "Poked Dagger", "A little dagger with a ribbon wound round its blade, all dots, no solid line anywhere."),
             (b.poked_bee, "poked-bee", "Poked Bee", "A round bee with dotted wings and dense striped bands. Friendly, and only slightly lopsided."),
             (b.poked_cherries, "poked-cherries", "Poked Cherries", "A pair of cherries on one twig, with hand-poked shadow and a small shine on each."),
             (b.poked_sheet, "poked-sheet", "Nine Small Charms", "A page of nine tiny charms to pick from: heart, star, moon, dagger, flower, sun, skull, gem and bolt.")]),
    _artist("lady-whiplash-lilyvane", "Lady Whiplash Lilyvane", "Art nouveau",
            "Haloes and long whiplash curves, swelling and thinning like an old poster for an opera nobody remembers.",
            [(b.peacock_eye, "peacock-eye", "Peacock Eye", "A single peacock feather rising through a beaded halo, inside a whiplash frame."),
             (b.calla_lilies, "calla-lilies", "Calla Lilies", "Three lilies on tall stems in front of a halo. Elegant, a little severe, very good on a calf."),
             (b.halo_dragonfly, "halo-dragonfly", "Dragonfly Halo", "A dragonfly with netted wings crossing a large beaded halo, long tail hanging straight down."),
             (b.swan_reflection, "swan-reflection", "Swan on Still Water", "A swan bending its neck in front of a halo, with thick-and-thin ripples spreading below."),
             (b.ginkgo_spray, "ginkgo-spray", "Ginkgo Spray", "A spray of fan-shaped ginkgo leaves spreading across a halo, on a thin frame of curves.")]),
    _artist("bramble-knotwright", "Bramble Knotwright the Third", "Interlaced knotwork",
            "Bands that go over, under and over again, and never end. The first two Knotwrights are still looking for the end.",
            [(c.square_knot, "square-knot", "Square Plait", "A square panel of unbroken plaitwork, every crossing over then under, with four corner studs."),
             (c.long_panel, "long-panel", "Long Panel", "A tall knotted band between two rules, sized for a forearm or the length of a spine."),
             (c.round_knot, "round-knot", "Round Knot", "Two waving bands laced into a ring around an eight-pointed star. Good on a shoulder cap."),
             (c.triquetra_ring, "triquetra-ring", "Three-Loop Knot", "A three-lobed knot with a ring laced through its loops and a star at the very middle."),
             (c.triskele_spiral, "triskele-spiral", "Triple Spiral", "Three spirals uncoiling from one point inside a dotted ring. Very old idea, still good.")]),
    _artist("starry-nebulon", "Starry Nebulon Quasarpants", "Cosmic charts",
            "Night windows, orbit lines and star charts. Has never been to space, but has strong opinions on it.",
            [(c.ringed_planet, "ringed-planet", "Ringed Planet", "A banded planet with fine rings, cut out of a round black night full of stars."),
             (c.moon_phases, "moon-phases", "Moon Phases", "Five phases of the moon across a black band, with a small row of stars above and below."),
             (c.great_comet, "great-comet", "Great Comet", "A stippled comet head trailing a long black fan of tail through a few sharp stars."),
             (c.total_eclipse, "total-eclipse", "Total Eclipse", "A black disc with a wild corona flaring around it and small stars set into the dark."),
             (c.constellation_chart, "constellation-chart", "Constellation Chart", "A round star chart with four made-up constellations on a dotted grid and a ticked rim."),
             (c.orbit_diagram, "orbit-diagram", "Orbit Diagram", "Four thin orbits around a rayed sun, each carrying a different small world.")]),
    _artist("doctor-moire-dizzywink", "Doctor Moire Dizzywink", "Op-art warps",
            "Black and white shapes that refuse to hold still. Not recommended for the seasick.",
            [(c.stripe_sphere, "stripe-sphere", "Striped Sphere", "A globe made only of curved bands that bulge towards you. Sits best on a round shoulder."),
             (c.checker_bulge, "checker-bulge", "Checker Bulge", "A checkerboard swelling out of its square frame. Works on a kneecap for obvious reasons."),
             (c.hypnotic_spiral, "hypnotic-spiral", "Hypnotic Spiral", "Two black arms winding into a point. Look at it for a while. You are getting sleepy."),
             (c.ripple_rings, "ripple-rings", "Ripple Rings", "Concentric rings that wobble as if something was dropped into them from far above."),
             (c.nested_tunnel, "nested-tunnel", "Nested Tunnel", "Black and white squares twisting down a tunnel with no floor. A good one for the palm.")]),
    _artist("hexarch-spindlethorn", "Hexarch Spindlethorn", "Sigil spikes",
            "Needle-thin mirrored sigils, all spike and hairline. They mean nothing, and he will happily explain them.",
            [(c.thorn_star, "thorn-star", "Thorn Star", "An eight-pointed star of long needles and fine curves, sharp enough to read at any size."),
             (c.spine_cross, "spine-cross", "Spine Cross", "A long spiked cross with paired barbs running its whole length. Made for the backbone."),
             (c.barbed_halo, "barbed-halo", "Barbed Halo", "A twisted wire halo with spikes pointing both ways and a small star held at its centre."),
             (c.bat_sigil, "bat-sigil", "Bat Sigil", "A bat reduced to its bones: a few long tapering strokes and a thin line of membrane."),
             (c.hexed_crown, "hexed-crown", "Hexed Crown", "A crown of needles above a heavy band, with more of them raining down beneath it.")]),
    _artist("beetlebrow-mothwick", "Beetlebrow Mothwick", "Entomology plates",
            "Insects stippled like plates from an old field guide. Knows every one by name and calls them all darling.",
            [(c.stag_beetle, "stag-beetle", "Stag Beetle", "A stag beetle pinned flat like a specimen, stipple shaded with solid black antlers."),
             (c.hawk_moth, "hawk-moth", "Hawk Moth", "A broad-winged moth with eyespots, each wing darkening in dots towards its edge."),
             (c.honey_bee, "honey-bee", "Honey Bee", "A honey bee from above, with a furred thorax, veined wings and three solid bands."),
             (c.orb_spider, "orb-spider", "Orb Spider", "A stippled spider marked with a pale star, sitting right in the middle of her web."),
             (c.plate_dragonfly, "plate-dragonfly", "Field Guide Dragonfly", "A dragonfly with every wing cell ruled in, its long body drawn segment by segment."),
             (c.swallowtail, "swallowtail", "Swallowtail", "A swallowtail butterfly with stippled veined wings and two long tails trailing below.")]),
    _artist("snipsy-the-paper-goblin", "Snipsy the Paper Goblin", "Folk paper-cut",
            "Black panels with bitten edges and little cut-out creatures, as if done with stolen nail scissors.",
            [(c.folk_bird, "folk-bird", "Folk Bird", "A plump bird cut out of a round black panel, with flowers and leaves around it."),
             (c.tree_of_life, "tree-of-life", "Tree of Life", "A branching tree full of flowers under a scalloped arch, two small birds at its roots."),
             (c.marigold_skull, "marigold-skull", "Marigold Skull", "A cut-paper skull with flowers for eyes, in a round panel with a ring of marigolds."),
             (c.twin_deer, "twin-deer", "Twin Deer", "Two spotted deer facing each other in a stamp-edged panel, antlers nearly touching."),
             (c.sun_and_moon, "sun-and-moon", "Sun and Moon", "A round panel split into day and night, with a smiling half-sun and a moon among stars."),
             (c.paper_lantern, "paper-lantern", "Paper Lantern", "A round black lantern with cut flowers and ribs, and a fringe of tassels underneath.")]),
    _artist("prismella-leadglass", "Prismella Leadglass", "Stained glass",
            "Heavy leading and patterned panes. Every shape is split into cells and filled with something different.",
            [(c.rose_window, "rose-window", "Rose Window", "A round church window of petals and patterned panes. Fills a whole shoulder blade."),
             (c.glass_butterfly, "glass-butterfly", "Glass Butterfly", "A butterfly with heavily leaded wings, panes of black, hatching and dots radiating out."),
             (c.lancet_lily, "lancet-lily", "Lancet Lily", "A lily rising in a pointed arch against a diamond lattice. Tall and thin, made for the forearm."),
             (c.glass_fish, "glass-fish", "Glass Fish", "A round fish made of honeycomb panes, with a plain head and one very surprised eye."),
             (c.glass_heart, "glass-heart", "Glass Heart", "A heart cut into a wheel of leaded panes around a small black star. Fragile on purpose."),
             (c.sun_lancet, "sun-lancet", "Sunrise Window", "A black sun coming up over two hills, with rays of patterned glass above it.")]),
]


def artist_json(artist):
    """The artist.json contents that ArtistCatalog reads."""
    return {
        "name": artist["name"],
        "description": artist["description"],
        "designs": [
            {"id": d["id"], "title": d["title"], "description": d["description"], "image": d["id"] + ".png"}
            for d in artist["designs"]
        ],
    }


def render(artist_id, design):
    """One design's PNG bytes. Its random numbers come only from its own name."""
    canvas = ink.Canvas()
    design["draw"](canvas, random.Random("%s/%s" % (artist_id, design["id"])))
    return ink.palette_png(canvas.levels(), ink.levels_palette())


def _write_one(job):
    index, design_index, directory = job
    artist = ARTISTS[index]
    design = artist["designs"][design_index]
    path = os.path.join(directory, artist["id"], design["id"] + ".png")
    data = render(artist["id"], design)
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


def generate(directory=ARTISTS_DIR):
    """Writes every artist. Returns the total size of the images in bytes."""
    if os.path.isdir(directory):
        shutil.rmtree(directory)
    jobs = []
    for index, artist in enumerate(ARTISTS):
        folder = os.path.join(directory, artist["id"])
        os.makedirs(folder)
        with open(os.path.join(folder, "artist.json"), "w") as f:
            json.dump(artist_json(artist), f, indent=2)
            f.write("\n")
        jobs.extend((index, d, directory) for d in range(len(artist["designs"])))
    with multiprocessing.Pool() as pool:
        sizes = pool.map(_write_one, jobs, chunksize=1)
    return sum(sizes)


# --- Contact sheet --------------------------------------------------------

TILE = 170
LABEL_SCALE = 2


def _read_levels(path):
    """Rows of palette indices from a PNG this script wrote."""
    with open(path, "rb") as f:
        data = f.read()
    offset = 8
    packed = b""
    width = height = 0
    while offset < len(data):
        length, kind = struct.unpack_from(">I4s", data, offset)
        body = data[offset + 8 : offset + 8 + length]
        if kind == b"IHDR":
            width, height = struct.unpack(">II", body[:8])
        elif kind == b"IDAT":
            packed += body
        offset += 12 + length
    raw = zlib.decompress(packed)
    return [raw[y * (width + 1) + 1 : (y + 1) * (width + 1)] for y in range(height)]


def _tile(rows):
    """Shrinks a 1024 image six times: nine samples of up to 9 per output pixel."""
    out = []
    for y in range(TILE):
        total = 0
        for k in (0, 2, 4):
            line = rows[y * 6 + k]
            for lane in (0, 2, 4):
                total += int.from_bytes(line[lane::6][:TILE], "little")
        out.append(total.to_bytes(TILE, "little"))
    return out


def _label(sheet, x, y, text):
    width = len(text) * 4 * LABEL_SCALE + LABEL_SCALE
    for dy in range(5 * LABEL_SCALE + 2 * LABEL_SCALE):
        sheet[y + dy][x : x + width] = bytes(width)
    for n, char in enumerate(text):
        glyph = DIGITS[char]
        for gy in range(5):
            for gx in range(3):
                if glyph[gy * 3 + gx] == "1":
                    for sy in range(LABEL_SCALE):
                        for sx in range(LABEL_SCALE):
                            sheet[y + LABEL_SCALE + gy * LABEL_SCALE + sy][
                                x + LABEL_SCALE + n * 4 * LABEL_SCALE + gx * LABEL_SCALE + sx
                            ] = 81


def write_contact_sheet(path):
    """Every design, numbered in catalog order, with one row per artist."""
    columns = max(len(artist["designs"]) for artist in ARTISTS)
    sheet = [bytearray(columns * TILE) for _ in range(len(ARTISTS) * TILE)]
    number = 0
    for row, artist in enumerate(ARTISTS):
        for column, design in enumerate(artist["designs"]):
            number += 1
            tile = _tile(_read_levels(os.path.join(ARTISTS_DIR, artist["id"], design["id"] + ".png")))
            for y, line in enumerate(tile):
                sheet[row * TILE + y][column * TILE : column * TILE + TILE] = line
            for y in range(TILE):
                sheet[row * TILE + y][column * TILE] = 40
            sheet[row * TILE][column * TILE : column * TILE + TILE] = bytes([40]) * TILE
            _label(sheet, column * TILE + 2, row * TILE + 2, str(number))
    palette = bytearray()
    for level in range(82):
        t = level / 81
        palette.extend(round(ink.PAPER[k] + (ink.INK[k] - ink.PAPER[k]) * t) for k in range(3))
    with open(path, "wb") as f:
        f.write(ink.palette_png(sheet, bytes(palette)))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contact", metavar="OUT.png")
    args = parser.parse_args(argv)
    started = time.time()
    total = generate()
    count = sum(len(artist["designs"]) for artist in ARTISTS)
    print("wrote %d designs, %d artists, %.1f MB, in %.0f s"
          % (count, len(ARTISTS), total / 1e6, time.time() - started))
    if args.contact:
        write_contact_sheet(args.contact)
        print("contact sheet: %s" % args.contact)
    return 0


if __name__ == "__main__":
    sys.exit(main())
