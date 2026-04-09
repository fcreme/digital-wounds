"""Generate atmospheric pre-rendered backgrounds for Digital Wounds."""

from PIL import Image, ImageDraw, ImageFilter
import random
import math
import os

WIDTH, HEIGHT = 1280, 720

def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

def noise_layer(w, h, scale=4, intensity=30):
    """Create a small noise image and upscale for organic feel."""
    small = Image.new('L', (w // scale, h // scale))
    pixels = small.load()
    for y in range(small.height):
        for x in range(small.width):
            pixels[x, y] = random.randint(0, intensity)
    return small.resize((w, h), Image.BILINEAR)


def gen_forest_clearing():
    img = Image.new('RGB', (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    # Sky gradient: deep dark blue-green
    top_color = (12, 18, 30)
    mid_color = (20, 35, 25)
    horizon_color = (35, 55, 40)
    ground_color = (18, 25, 14)
    bottom_color = (10, 14, 8)

    horizon_y = int(HEIGHT * 0.45)

    # Sky
    for y in range(horizon_y):
        t = y / horizon_y
        if t < 0.5:
            c = lerp_color(top_color, mid_color, t * 2)
        else:
            c = lerp_color(mid_color, horizon_color, (t - 0.5) * 2)
        draw.line([(0, y), (WIDTH, y)], fill=c)

    # Ground
    for y in range(horizon_y, HEIGHT):
        t = (y - horizon_y) / (HEIGHT - horizon_y)
        c = lerp_color(ground_color, bottom_color, t)
        draw.line([(0, y), (WIDTH, y)], fill=c)

    # Fog glow near horizon
    fog = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    fog_draw = ImageDraw.Draw(fog)
    for i in range(60):
        alpha = int(3 * (1 - i / 60))
        y_off = horizon_y - 30 + i
        fog_draw.line([(0, y_off), (WIDTH, y_off)], fill=(40, 65, 45, alpha))
    img.paste(Image.alpha_composite(img.convert('RGBA'), fog).convert('RGB'))

    # Dark tree silhouettes
    tree_layer = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    tree_draw = ImageDraw.Draw(tree_layer)

    random.seed(42)
    for _ in range(18):
        tx = random.randint(-50, WIDTH + 50)
        trunk_w = random.randint(8, 20)
        trunk_h = random.randint(150, 350)
        trunk_bottom = horizon_y + random.randint(-10, 40)
        dark = random.randint(2, 10)
        col = (dark, dark + 2, dark)

        # Trunk
        tree_draw.rectangle([tx - trunk_w//2, trunk_bottom - trunk_h,
                             tx + trunk_w//2, trunk_bottom], fill=col)

        # Branches
        for _ in range(random.randint(3, 8)):
            by = trunk_bottom - random.randint(trunk_h // 3, trunk_h)
            blen = random.randint(30, 90) * random.choice([-1, 1])
            tree_draw.line([(tx, by), (tx + blen, by - random.randint(10, 40))],
                          fill=col, width=random.randint(2, 5))

    # Canopy blobs
    for _ in range(25):
        cx = random.randint(0, WIDTH)
        cy = random.randint(horizon_y - 300, horizon_y - 80)
        r = random.randint(40, 120)
        dark = random.randint(3, 12)
        tree_draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                         fill=(dark, dark + 3, dark, 200))

    tree_layer = tree_layer.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img.convert('RGBA'), tree_layer).convert('RGB')

    # Stone pillars (subtle dark rectangles)
    pillar_layer = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    pillar_draw = ImageDraw.Draw(pillar_layer)
    for px in [WIDTH // 2 - 180, WIDTH // 2 + 150]:
        pw, ph = 35, 140
        py = horizon_y - ph + 20
        pillar_draw.rectangle([px, py, px + pw, py + ph], fill=(22, 20, 18, 180))
        # Slight highlight on left edge
        pillar_draw.line([(px, py), (px, py + ph)], fill=(30, 28, 25, 100), width=2)
    pillar_layer = pillar_layer.filter(ImageFilter.GaussianBlur(1))
    img = Image.alpha_composite(img.convert('RGBA'), pillar_layer).convert('RGB')

    # Subtle stars
    for _ in range(80):
        sx = random.randint(0, WIDTH)
        sy = random.randint(0, horizon_y - 50)
        brightness = random.randint(40, 90)
        r = random.choice([1, 1, 1, 2])
        draw = ImageDraw.Draw(img)
        draw.ellipse([sx - r, sy - r, sx + r, sy + r],
                    fill=(brightness, brightness, brightness + 5))

    # Film grain
    noise = noise_layer(WIDTH, HEIGHT, scale=2, intensity=12)
    noise_rgb = Image.merge('RGB', [noise, noise, noise])
    from PIL import ImageChops
    img = ImageChops.add(img, noise_rgb)

    # Vignette
    vignette = Image.new('L', (WIDTH, HEIGHT), 255)
    vig_draw = ImageDraw.Draw(vignette)
    cx, cy = WIDTH // 2, HEIGHT // 2
    max_dist = math.sqrt(cx**2 + cy**2)
    for y in range(HEIGHT):
        for x in range(0, WIDTH, 4):
            dist = math.sqrt((x - cx)**2 + (y - cy)**2) / max_dist
            v = max(0, int(255 * (1 - dist * dist * 1.2)))
            vig_draw.rectangle([x, y, x + 4, y], fill=v)

    from PIL import ImageChops
    img = ImageChops.multiply(img, Image.merge('RGB', [vignette, vignette, vignette]))

    return img


def gen_dark_hallway():
    img = Image.new('RGB', (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    # Interior gradient (warm tones, well-lit)
    top_color = (110, 85, 120)
    mid_color = (160, 120, 135)
    bottom_color = (140, 105, 85)

    for y in range(HEIGHT):
        t = y / HEIGHT
        if t < 0.5:
            c = lerp_color(top_color, mid_color, t * 2)
        else:
            c = lerp_color(mid_color, bottom_color, (t - 0.5) * 2)
        draw.line([(0, y), (WIDTH, y)], fill=c)

    # Walls - perspective lines converging to center
    wall_layer = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    wall_draw = ImageDraw.Draw(wall_layer)

    vanish_x, vanish_y = WIDTH // 2, int(HEIGHT * 0.42)

    # Left wall
    wall_draw.polygon([(0, 0), (vanish_x - 80, vanish_y - 60),
                       (vanish_x - 80, vanish_y + 120), (0, HEIGHT)],
                     fill=(200, 160, 140, 255))

    # Right wall
    wall_draw.polygon([(WIDTH, 0), (vanish_x + 80, vanish_y - 60),
                       (vanish_x + 80, vanish_y + 120), (WIDTH, HEIGHT)],
                     fill=(200, 160, 140, 255))

    # Floor
    wall_draw.polygon([(0, HEIGHT), (vanish_x - 80, vanish_y + 120),
                       (vanish_x + 80, vanish_y + 120), (WIDTH, HEIGHT)],
                     fill=(180, 140, 110, 255))

    # Ceiling
    wall_draw.polygon([(0, 0), (vanish_x - 80, vanish_y - 60),
                       (vanish_x + 80, vanish_y - 60), (WIDTH, 0)],
                     fill=(160, 130, 155, 255))

    img = Image.alpha_composite(img.convert('RGBA'), wall_layer).convert('RGB')

    # Warm lantern glow spots
    glow_layer = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_positions = [
        (WIDTH // 2 - 200, int(HEIGHT * 0.35)),
        (WIDTH // 2 + 200, int(HEIGHT * 0.35)),
        (WIDTH // 2 - 120, int(HEIGHT * 0.40)),
        (WIDTH // 2 + 120, int(HEIGHT * 0.40)),
    ]
    for gx, gy in glow_positions:
        for r in range(120, 0, -1):
            alpha = int(25 * (1 - r / 120))
            glow_draw = ImageDraw.Draw(glow_layer)
            glow_draw.ellipse([gx - r, gy - r, gx + r, gy + r],
                            fill=(120, 70, 20, alpha))
    img = Image.alpha_composite(img.convert('RGBA'), glow_layer).convert('RGB')

    # Picture frames on walls (dark rectangles with slight border)
    frame_layer = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    frame_draw = ImageDraw.Draw(frame_layer)

    frames = [
        (WIDTH // 2 - 280, int(HEIGHT * 0.25), 70, 55),
        (WIDTH // 2 - 170, int(HEIGHT * 0.28), 55, 45),
        (WIDTH // 2 + 130, int(HEIGHT * 0.28), 55, 45),
        (WIDTH // 2 + 220, int(HEIGHT * 0.25), 70, 55),
    ]
    for fx, fy, fw, fh in frames:
        # Frame border (golden)
        frame_draw.rectangle([fx - 3, fy - 3, fx + fw + 3, fy + fh + 3],
                           fill=(55, 40, 22, 200))
        # Dark interior
        frame_draw.rectangle([fx, fy, fx + fw, fy + fh],
                           fill=(15, 10, 10, 220))

    img = Image.alpha_composite(img.convert('RGBA'), frame_layer).convert('RGB')

    # Film grain
    noise = noise_layer(WIDTH, HEIGHT, scale=2, intensity=10)
    noise_rgb = Image.merge('RGB', [noise, noise, noise])
    from PIL import ImageChops
    img = ImageChops.add(img, noise_rgb)

    # Vignette handled by post-processing shader — skip baked vignette

    return img


if __name__ == '__main__':
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'backgrounds')
    os.makedirs(out_dir, exist_ok=True)

    print("Generating Forest Clearing...")
    forest = gen_forest_clearing()
    forest.save(os.path.join(out_dir, 'forest_clearing.png'))
    print("  -> saved forest_clearing.png")

    print("Generating Dark Hallway...")
    hallway = gen_dark_hallway()
    hallway.save(os.path.join(out_dir, 'dark_hallway.png'))
    print("  -> saved dark_hallway.png")

    print("Done!")
