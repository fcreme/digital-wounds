"""Reads the gallery model's wall triangles and emissive texture from its GLB.

The node transforms cancel out, so a vertex in world units is POSITION * 10
with Y up. The emissive texture is image 1 and is addressed by TEXCOORD_1, in
the top-left texture space that the painting rectangles use, with no flip.
"""

import json
import struct

POSITION_SCALE = 10.0
WALL_MAX_NORMAL_Y = 0.3
EMISSIVE_IMAGE = 1

# The hall floor, from the model's floor corners, as (x, z). The east side steps
# in around the notch at z -7.49 to 2.08.
FLOOR_OUTLINE = (
    (-10.0, -33.24),
    (13.06, -33.24),
    (13.06, -7.49),
    (10.72, -7.49),
    (10.72, 2.08),
    (12.65, 2.08),
    (12.65, 30.66),
    (-10.0, 30.66),
)


def _read_glb(path):
    with open(path, "rb") as f:
        data = f.read()
    json_length = struct.unpack_from("<I", data, 12)[0]
    gltf = json.loads(data[20 : 20 + json_length])
    return gltf, data[20 + json_length + 8 :]


def _read_accessor(gltf, binary, index, count_per_item, code):
    accessor = gltf["accessors"][index]
    view = gltf["bufferViews"][accessor["bufferView"]]
    start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    item = "<%d%s" % (count_per_item, code)
    stride = view.get("byteStride", struct.calcsize(item))
    return [
        struct.unpack_from(item, binary, start + stride * i)
        for i in range(accessor["count"])
    ]


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def load_triangles(path):
    """Every triangle as a dict of world `positions`, texture `uvs` and unit `normal`."""
    gltf, binary = _read_glb(path)
    primitive = gltf["meshes"][0]["primitives"][0]
    positions = _read_accessor(gltf, binary, primitive["attributes"]["POSITION"], 3, "f")
    uvs = _read_accessor(gltf, binary, primitive["attributes"]["TEXCOORD_1"], 2, "f")
    indices = [i[0] for i in _read_accessor(gltf, binary, primitive["indices"], 1, "I")]

    triangles = []
    for t in range(0, len(indices), 3):
        corners = indices[t : t + 3]
        world = [tuple(c * POSITION_SCALE for c in positions[i]) for i in corners]
        edge_a = [world[1][k] - world[0][k] for k in range(3)]
        edge_b = [world[2][k] - world[0][k] for k in range(3)]
        normal = _cross(edge_a, edge_b)
        length = sum(c * c for c in normal) ** 0.5
        triangles.append(
            {
                "positions": world,
                "uvs": [uvs[i] for i in corners],
                "normal": tuple(c / length for c in normal),
            }
        )
    return triangles


def load_wall_triangles(path):
    """The vertical triangles only: walls, without floor or ceiling."""
    return [
        t for t in load_triangles(path) if abs(t["normal"][1]) < WALL_MAX_NORMAL_Y
    ]


def load_emissive_png(path):
    """The emissive texture's PNG bytes, sliced out of the GLB."""
    gltf, binary = _read_glb(path)
    view = gltf["bufferViews"][gltf["images"][EMISSIVE_IMAGE]["bufferView"]]
    start = view.get("byteOffset", 0)
    return binary[start : start + view["byteLength"]]


def inside_floor(x, z):
    """True when world point (x, z) is on the hall floor."""
    inside = False
    for i, (x0, z0) in enumerate(FLOOR_OUTLINE):
        x1, z1 = FLOOR_OUTLINE[(i + 1) % len(FLOOR_OUTLINE)]
        if (z0 > z) != (z1 > z) and x < x0 + (z - z0) * (x1 - x0) / (z1 - z0):
            inside = not inside
    return inside
