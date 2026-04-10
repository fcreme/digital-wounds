# Digital Wounds

> A Resident Evil Remake-style native C++ dark atmospheric experience with interactive books and cinematic environments.

**Status: Work in Progress**

## About

Digital Wounds is an immersive desktop application built with a custom C++ engine. It uses the **RE Remake hybrid rendering architecture**: pre-rendered backgrounds created in Blender, combined with real-time 3D objects (characters, interactive books, props), dynamic lighting/shadows projected onto the static backgrounds, and FMV overlay loops for atmospheric effects like fog and swaying trees.

The visual style targets a dark, Silent Hill-inspired atmosphere with film grain, vignette, and subtle bloom post-processing.

## Tech Stack

- **C++17** — core language
- **SDL2** — window management, input, audio
- **OpenGL 3.3+** — real-time rendering (core profile)
- **GLM** — math library (vectors, matrices, transforms)
- **CMake** — build system
- **stb_image / stb_vorbis** — image and audio loading

## RE Remake Rendering Architecture

Each scene ("room") combines multiple rendering layers:

```
1. Pre-rendered background    ← static image (Blender render)
2. Depth pre-pass             ← hidden geometry sets Z-buffer
3. Real-time 3D objects       ← books, lanterns, player model
4. Shadow projection          ← dynamic shadows onto BG
5. Particle effects           ← fog, dust, fireflies
6. FMV video overlays         ← animated BG elements (fog, water)
7. Post-processing            ← vignette, grain, bloom, color grade
```

This approach gives cinematic-quality backgrounds with minimal GPU cost, while interactive elements remain fully 3D.

## Prerequisites

- **CMake** 3.20+
- **SDL2** development libraries
- **C++17 compiler** (MSVC via Visual Studio 2022, or MinGW-w64)
- **OpenGL 3.3+** capable GPU

## Build

```bash
cmake -B build
cmake --build build
```

Run:
```bash
./build/digital_wounds          # Linux/macOS
build\Debug\digital_wounds.exe  # Windows
```

## Controls

| Key | Action |
|-----|--------|
| `W A S D` | Move |
| `Mouse` | Look around |
| `E` | Interact with book |
| `A / D` | Previous / Next page (while reading) |
| `Q` | Close book |
| `ESC` | Quit |

## Project Structure

```
src/
├── main.cpp              # Entry point, SDL2 init
├── core/                 # Engine, InputManager, AssetManager
├── renderer/             # OpenGL: Renderer, BackgroundLayer, Shader, Mesh, Camera
├── scene/                # Room/scene management, transitions
├── world/                # Player, props, books, collision
├── fx/                   # Post-processing, particles, FMV overlays
├── audio/                # Spatial audio, ambient, footsteps
└── utils/                # Math helpers, logging

assets/
├── backgrounds/          # Pre-rendered room images (from Blender)
├── models/               # Real-time 3D props (.obj)
├── textures/             # PBR textures
├── collision/            # Per-room collision maps
├── shaders/              # GLSL 330 core shaders
├── audio/                # Music, SFX, ambient loops
├── video/                # FMV overlay loops
└── rooms/                # Room definitions (JSON)

legacy/                   # Original Three.js prototype (reference only)
```

## Asset Pipeline

1. **Backgrounds** — Model environments in Blender, render from fixed camera angles, export as PNG
2. **Collision maps** — Export simplified geometry from Blender for walkable areas
3. **3D props** — Model interactive objects in Blender, export as OBJ
4. **FMV overlays** — Render animation loops (fog, water, fire) as video files
5. **Room definitions** — JSON files specifying camera, background, collision, and props per room

## License

All rights reserved.
