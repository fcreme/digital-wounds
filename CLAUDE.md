# Digital Wounds — Project Instructions

## Project Overview
Digital Wounds is a native C++ desktop application — a dark atmospheric experience showcasing tattoo artist portfolios. Built with a custom engine following the **Resident Evil Remake (2002) hybrid rendering architecture**: pre-rendered backgrounds + real-time 3D objects + dynamic lighting projected onto static backgrounds + FMV overlays for atmospheric effects.

## Tech Stack
- **Language:** C++17
- **Build System:** CMake 3.20+
- **Window/Input/Audio:** SDL2
- **Rendering:** OpenGL 3.3+ (core profile)
- **Math:** GLM (header-only)
- **Image Loading:** stb_image (in `lib/`)
- **Audio Decoding:** stb_vorbis (in `lib/`)

## Build Instructions (MSYS2 MinGW-w64 on Windows)
```bash
# Must run from MSYS2 shell or with MinGW in PATH:
export PATH=/mingw64/bin:$PATH
cmake -B build -G "MinGW Makefiles"
cmake --build build
./build/digital_wounds.exe
```

Or from Git Bash / cmd:
```bash
/c/msys64/usr/bin/bash.exe -lc 'export PATH=/mingw64/bin:$PATH && cd /path/to/project && cmake -B build -G "MinGW Makefiles" && cmake --build build'
```

## Coding Conventions
- C++17 standard
- **Files:** snake_case (`background_layer.cpp`)
- **Classes:** PascalCase (`BackgroundLayer`)
- **Methods:** camelCase (`loadTexture()`)
- **Member variables:** `m_` prefix (`m_window`, `m_renderer`)
- **Constants/Enums:** UPPER_SNAKE_CASE
- Header guards: `#pragma once`
- Prefer RAII and smart pointers over raw new/delete
- Keep headers minimal — forward-declare where possible

## Architecture

### Rendering Pipeline (per frame)
```
1. Clear screen
2. Draw pre-rendered background (fullscreen textured quad)
3. Set depth buffer from room's hidden geometry (depth pre-pass)
4. Render real-time 3D objects (books, lanterns, player) with depth testing
5. Project dynamic shadows onto background using hidden geometry
6. Render particle effects (fog, dust, fireflies)
7. Render video overlays (FMV loops for animated BG elements)
8. Post-processing (vignette, film grain, bloom, color grading)
9. Swap buffers
```

### Key Systems
- **Engine** (`src/core/`): SDL2 window, OpenGL context, game loop, input, asset loading
- **Renderer** (`src/renderer/`): OpenGL orchestrator, background quad, shader management, mesh rendering, fixed cameras, shadow projection
- **Scene** (`src/scene/`): Room management, transitions (fade/door)
- **World** (`src/world/`): Player, interactive props (books), collision maps
- **FX** (`src/fx/`): Post-processing, particles, FMV video overlays
- **Audio** (`src/audio/`): Spatial audio, ambient, footsteps via SDL2_mixer or raw SDL

### Room System
Each room is defined by:
- A pre-rendered background image (from Blender)
- A fixed camera position + projection matrix
- A collision map (2D walkable area)
- A list of real-time 3D props
- Optional FMV overlay loops

Room definitions live in `assets/rooms/` as JSON files.

## Folder Structure
```
src/              — C++ source (the actual engine)
legacy/src/       — old Three.js code (reference only, do NOT modify)
assets/           — all runtime assets (backgrounds, models, shaders, audio, etc.)
lib/              — third-party header-only libraries (stb_image, stb_vorbis)
build/            — CMake build output (gitignored)
```

## Asset Pipeline
- **Backgrounds:** Rendered in Blender → exported as PNG/JPG to `assets/backgrounds/`
- **Collision:** Exported from Blender as simplified geometry or painted maps → `assets/collision/`
- **3D Props:** Modeled in Blender → exported as OBJ → `assets/models/`
- **Shaders:** GLSL 330 core → `assets/shaders/`
- **FMV Overlays:** Rendered animation loops → `assets/video/`

## Important Notes
- The `legacy/` folder contains the original Three.js prototype. Use it as reference for gameplay logic, book system, and visual targets — but never modify it.
- All shaders target GLSL 330 core (OpenGL 3.3).
- The engine uses a fixed-camera system (not free-look) — cameras are defined per room.
- Player is rendered as a real-time 3D model on top of pre-rendered backgrounds.
