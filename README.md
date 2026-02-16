# Digital Wounds

> A PS1/Silent Hill-inspired 3D web experience showcasing tattoo artist portfolios through interactive books in a dark atmospheric forest.

**Status: Work in Progress**

## About

Digital Wounds is an immersive first-person 3D experience built with Three.js. Players explore a fog-drenched forest rendered with PlayStation 1-era visual effects — vertex jitter, affine texture warping, ordered dithering, and scanline overlays. Along the path, interactive books display tattoo artist portfolios with realistic page-curl animations.

## Tech Stack

- **Three.js** r170 — 3D rendering
- **Vite** 6 — build tool & dev server
- **Vanilla JavaScript** — no frameworks

## Getting Started

### Prerequisites

- Node.js 18+

### Installation

```bash
git clone <repo-url>
cd digital-wounds
npm install
npm run dev
```

The dev server will start at `http://localhost:5173`.

### Build

```bash
npm run build
npm run preview
```

## Controls

| Key | Action |
|-----|--------|
| `W A S D` | Move |
| `Mouse` | Look around |
| `E` | Interact with book |
| `A / D` | Previous / Next page (while reading) |
| `Q` | Close book |

## Architecture

```
src/
├── core/           # Engine, EventBus, InputManager, AssetPipeline
├── player/         # PlayerController, InteractionRaycaster
├── world/          # WorldManager, ForestGenerator, TerrainBuilder,
│                   # PathBuilder, ArtistStation, SkyDome, GroundScatter
├── book/           # Book, BookFactory, PageGeometryBuilder,
│                   # PageCurlAnimator, PageMaterial, PageTextureCompositor
├── fx/             # PSXEffect, PostProcessing, ParticleSystem,
│                   # FlickerLight, Fireflies, AudioSystem
├── ui/             # UIOverlay, LoadingScreen
└── utils/          # Math helpers
```

All systems communicate through a central **EventBus** (pub/sub pattern).

## PSX Visual Pipeline

The retro aesthetic is achieved through multiple layers:

1. **Low-res rendering** — 240p internal resolution upscaled with nearest-neighbor filtering
2. **Vertex jitter** — positions snapped to a coarse grid via `onBeforeCompile` patching
3. **Affine texture mapping** — UVs divided by perspective-corrected W for authentic PS1 warping
4. **Post-processing chain** — posterization, Bayer dithering, bloom, scanlines, vignette, film grain
5. **Dense fog** — exponential squared fog for ~20 unit visibility (Silent Hill style)

## Adding an Artist

No code changes required:

1. Create a config at `public/data/artists/<slug>/config.json`
2. Add the slug to `public/data/artists/manifest.json`
3. Place portfolio images in the artist directory

## License

All rights reserved.
