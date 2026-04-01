import * as THREE from 'three';

/**
 * Procedural Canvas 2D texture generators for Bloodborne gothic aesthetic.
 * Uses canvas drawing primitives for macro structure + smooth noise overlay.
 */

function canvasToTexture(canvas, repeat = false) {
  const tex = new THREE.CanvasTexture(canvas);
  tex.minFilter = THREE.NearestFilter;
  tex.magFilter = THREE.NearestFilter;
  tex.generateMipmaps = false;
  if (repeat) {
    tex.wrapS = THREE.RepeatWrapping;
    tex.wrapT = THREE.RepeatWrapping;
  }
  return tex;
}

// --- Smooth noise foundation ---
// Precomputed 256x256 lookup table with bilinear interpolation
const _noiseTable = new Float32Array(256 * 256);
(function initNoiseTable() {
  for (let i = 0; i < 256 * 256; i++) {
    _noiseTable[i] = Math.random();
  }
})();

function smoothNoise(x, y) {
  const ix = Math.floor(x) & 255;
  const iy = Math.floor(y) & 255;
  const fx = x - Math.floor(x);
  const fy = y - Math.floor(y);
  // Smoothstep
  const sx = fx * fx * (3 - 2 * fx);
  const sy = fy * fy * (3 - 2 * fy);

  const ix1 = (ix + 1) & 255;
  const iy1 = (iy + 1) & 255;

  const v00 = _noiseTable[iy * 256 + ix];
  const v10 = _noiseTable[iy * 256 + ix1];
  const v01 = _noiseTable[iy1 * 256 + ix];
  const v11 = _noiseTable[iy1 * 256 + ix1];

  const top = v00 + sx * (v10 - v00);
  const bot = v01 + sx * (v11 - v01);
  return top + sy * (bot - top);
}

function fbm(x, y, octaves = 4) {
  let value = 0, amp = 0.5, freq = 1;
  for (let i = 0; i < octaves; i++) {
    value += amp * smoothNoise(x * freq, y * freq);
    amp *= 0.5;
    freq *= 2;
  }
  return value;
}

export function createDirtTexture(size = 256) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext('2d');

  // Cold grey-brown base
  ctx.fillStyle = '#3e3a30';
  ctx.fillRect(0, 0, size, size);

  // 2x2 block FBM overlay (cold shifted)
  for (let y = 0; y < size; y += 2) {
    for (let x = 0; x < size; x += 2) {
      const n = fbm(x * 0.025, y * 0.025, 5);
      const r = Math.floor(45 + n * 50);
      const g = Math.floor(42 + n * 48);
      const b = Math.floor(35 + n * 42);
      ctx.fillStyle = `rgba(${r},${g},${b},0.6)`;
      ctx.fillRect(x, y, 2, 2);
    }
  }

  // Large dark root-shadow patches (cold tint)
  for (let i = 0; i < 25; i++) {
    const sx = Math.random() * size;
    const sy = Math.random() * size;
    const sr = 6 + Math.random() * 14;
    const grad = ctx.createRadialGradient(sx, sy, 0, sx, sy, sr);
    grad.addColorStop(0, `rgba(15,15,20,${0.2 + Math.random() * 0.15})`);
    grad.addColorStop(1, 'rgba(15,15,20,0)');
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(sx, sy, sr, 0, Math.PI * 2);
    ctx.fill();
  }

  // Lighter patches (muted, less warm)
  for (let i = 0; i < 10; i++) {
    const sx = Math.random() * size;
    const sy = Math.random() * size;
    const sr = 5 + Math.random() * 10;
    const grad = ctx.createRadialGradient(sx, sy, 0, sx, sy, sr);
    grad.addColorStop(0, `rgba(80,80,75,${0.15 + Math.random() * 0.1})`);
    grad.addColorStop(1, 'rgba(80,80,75,0)');
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(sx, sy, sr, 0, Math.PI * 2);
    ctx.fill();
  }

  // Pebble dots (2-3px rects)
  for (let i = 0; i < 60; i++) {
    const px = Math.random() * size;
    const py = Math.random() * size;
    const ps = 2 + Math.random();
    const shade = 65 + Math.random() * 35;
    ctx.fillStyle = `rgb(${Math.floor(shade)},${Math.floor(shade * 0.85)},${Math.floor(shade * 0.65)})`;
    ctx.fillRect(px, py, ps, ps);
  }

  return canvasToTexture(canvas, true);
}

export function createPathTexture(size = 256) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext('2d');

  // Cold packed dirt base
  ctx.fillStyle = '#504a40';
  ctx.fillRect(0, 0, size, size);

  // 2x2 block FBM
  for (let y = 0; y < size; y += 2) {
    for (let x = 0; x < size; x += 2) {
      const n = fbm(x * 0.03, y * 0.03, 4);
      const center = 1.0 - Math.abs(x / size - 0.5) * 1.2;
      const v = n * 0.7 + center * 0.3;
      const r = Math.floor(75 + v * 50);
      const g = Math.floor(62 + v * 40);
      const b = Math.floor(38 + v * 25);
      ctx.fillStyle = `rgba(${r},${g},${b},0.55)`;
      ctx.fillRect(x, y, 2, 2);
    }
  }

  // Wagon rut hints — two parallel darker lines
  ctx.globalAlpha = 0.15;
  ctx.fillStyle = '#2a2a28';
  ctx.fillRect(size * 0.3, 0, size * 0.06, size);
  ctx.fillRect(size * 0.62, 0, size * 0.06, size);
  ctx.globalAlpha = 1;

  // Edge grass fringe
  for (let i = 0; i < 30; i++) {
    const gy = Math.random() * size;
    const side = Math.random() < 0.5 ? 0 : size - 8;
    ctx.fillStyle = `rgba(50,70,35,${0.2 + Math.random() * 0.15})`;
    ctx.fillRect(side, gy, 6 + Math.random() * 6, 2 + Math.random() * 3);
  }

  // Pebbles
  for (let i = 0; i < 60; i++) {
    const px = Math.random() * size;
    const py = Math.random() * size;
    const pr = 1 + Math.random() * 3;
    const shade = 80 + Math.random() * 40;
    ctx.beginPath();
    ctx.arc(px, py, pr, 0, Math.PI * 2);
    ctx.fillStyle = `rgb(${Math.floor(shade)},${Math.floor(shade * 0.9)},${Math.floor(shade * 0.8)})`;
    ctx.fill();
  }

  // Worn center band
  ctx.globalAlpha = 0.1;
  ctx.fillStyle = '#8a7a60';
  ctx.fillRect(size * 0.35, 0, size * 0.3, size);
  ctx.globalAlpha = 1;

  return canvasToTexture(canvas, true);
}

export function createBarkTexture(w = 128, h = 256) {
  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d');

  // Dark brown base
  ctx.fillStyle = '#3a2a1a';
  ctx.fillRect(0, 0, w, h);

  // 14 vertical bark ridges (wide rectangles)
  for (let i = 0; i < 14; i++) {
    const x = (i / 14) * w + (Math.random() - 0.5) * 4;
    const rw = 4 + Math.random() * 6;
    const shade = 35 + Math.random() * 35;
    ctx.fillStyle = `rgb(${shade + 22},${shade + 12},${shade})`;
    ctx.fillRect(x, 0, rw, h);

    // Ridge highlight line on one edge
    ctx.fillStyle = `rgba(${shade + 40},${shade + 28},${shade + 15},0.3)`;
    ctx.fillRect(x, 0, 1.5, h);
  }

  // 8 deep horizontal cracks (thicker, wider)
  for (let i = 0; i < 8; i++) {
    const y = Math.random() * h;
    ctx.beginPath();
    ctx.moveTo(0, y);
    for (let x = 0; x < w; x += 3) {
      ctx.lineTo(x, y + (Math.random() - 0.5) * 4);
    }
    ctx.strokeStyle = `rgba(12,8,4,${0.4 + Math.random() * 0.3})`;
    ctx.lineWidth = 1 + Math.random() * 1.5;
    ctx.stroke();
  }

  // 2 large knot holes with radial gradients
  for (let i = 0; i < 2; i++) {
    const kx = Math.random() * w;
    const ky = Math.random() * h;
    const kr = 5 + Math.random() * 8;
    const grad = ctx.createRadialGradient(kx, ky, 0, kx, ky, kr);
    grad.addColorStop(0, 'rgba(12,8,4,0.7)');
    grad.addColorStop(0.5, 'rgba(30,20,12,0.4)');
    grad.addColorStop(1, 'rgba(45,32,20,0)');
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(kx, ky, kr, 0, Math.PI * 2);
    ctx.fill();
  }

  // 4x4 block noise overlay
  for (let y = 0; y < h; y += 4) {
    for (let x = 0; x < w; x += 4) {
      const n = smoothNoise(x * 0.2, y * 0.2);
      ctx.fillStyle = `rgba(${n > 0.5 ? 65 : 15},${n > 0.5 ? 48 : 10},${n > 0.5 ? 32 : 6},0.12)`;
      ctx.fillRect(x, y, 4, 4);
    }
  }

  return canvasToTexture(canvas, true);
}

export function createFoliageTexture(size = 128) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext('2d');

  // Deep green base
  ctx.fillStyle = '#1a3018';
  ctx.fillRect(0, 0, size, size);

  // 5 green shades for leaf clusters
  const greens = [
    [28, 55, 25], [35, 68, 30], [22, 48, 20], [40, 72, 35], [30, 60, 28],
  ];

  // 40 overlapping leaf-cluster circles
  for (let i = 0; i < 40; i++) {
    const cx = Math.random() * size;
    const cy = Math.random() * size;
    const cr = 5 + Math.random() * 12;
    const [r, g, b] = greens[i % 5];
    ctx.beginPath();
    ctx.arc(cx, cy, cr, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${r},${g},${b},${0.3 + Math.random() * 0.25})`;
    ctx.fill();
  }

  // 25 brighter highlight circles
  for (let i = 0; i < 25; i++) {
    const cx = Math.random() * size;
    const cy = Math.random() * size;
    const cr = 3 + Math.random() * 7;
    ctx.beginPath();
    ctx.arc(cx, cy, cr, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(55,95,45,${0.15 + Math.random() * 0.15})`;
    ctx.fill();
  }

  // 20 dark gap circles
  for (let i = 0; i < 20; i++) {
    const cx = Math.random() * size;
    const cy = Math.random() * size;
    const cr = 2 + Math.random() * 5;
    ctx.beginPath();
    ctx.arc(cx, cy, cr, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(10,20,8,${0.3 + Math.random() * 0.2})`;
    ctx.fill();
  }

  // 8 directional vein lines
  for (let i = 0; i < 8; i++) {
    const sx = Math.random() * size;
    const sy = Math.random() * size;
    ctx.beginPath();
    ctx.moveTo(sx, sy);
    const angle = Math.random() * Math.PI * 2;
    const len = 10 + Math.random() * 20;
    ctx.lineTo(sx + Math.cos(angle) * len, sy + Math.sin(angle) * len);
    ctx.strokeStyle = `rgba(40,80,30,${0.2 + Math.random() * 0.15})`;
    ctx.lineWidth = 0.8 + Math.random() * 0.5;
    ctx.stroke();
  }

  return canvasToTexture(canvas, true);
}

export function createRockTexture(size = 128) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext('2d');

  // Diagonal gradient base
  const grad = ctx.createLinearGradient(0, 0, size, size);
  grad.addColorStop(0, '#5a5550');
  grad.addColorStop(0.5, '#706860');
  grad.addColorStop(1, '#5e5650');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, size, size);

  // 8 warm/cool mineral patches (large arcs)
  const patchColors = [
    'rgba(100,85,65,0.25)', 'rgba(70,75,80,0.2)', 'rgba(90,80,60,0.2)',
    'rgba(65,70,75,0.2)', 'rgba(85,75,55,0.25)', 'rgba(75,80,85,0.15)',
    'rgba(95,82,62,0.2)', 'rgba(60,65,70,0.2)',
  ];
  for (let i = 0; i < 8; i++) {
    const cx = Math.random() * size;
    const cy = Math.random() * size;
    const cr = 8 + Math.random() * 16;
    ctx.beginPath();
    ctx.arc(cx, cy, cr, 0, Math.PI * 2);
    ctx.fillStyle = patchColors[i];
    ctx.fill();
  }

  // 4x4 FBM block overlay
  for (let y = 0; y < size; y += 4) {
    for (let x = 0; x < size; x += 4) {
      const n = fbm(x * 0.06, y * 0.06, 3);
      const shade = Math.floor(60 + n * 50);
      ctx.fillStyle = `rgba(${shade},${Math.floor(shade * 0.97)},${Math.floor(shade * 0.93)},0.3)`;
      ctx.fillRect(x, y, 4, 4);
    }
  }

  // 4 deep cracks with highlight edges
  for (let i = 0; i < 4; i++) {
    ctx.beginPath();
    let cx = Math.random() * size;
    let cy = Math.random() * size;
    ctx.moveTo(cx, cy);
    for (let s = 0; s < 10; s++) {
      cx += (Math.random() - 0.5) * 12;
      cy += (Math.random() - 0.5) * 12;
      ctx.lineTo(cx, cy);
    }
    // Dark crack
    ctx.strokeStyle = `rgba(25,22,18,${0.4 + Math.random() * 0.3})`;
    ctx.lineWidth = 1 + Math.random();
    ctx.stroke();
    // Highlight edge
    ctx.strokeStyle = `rgba(100,95,85,${0.15 + Math.random() * 0.1})`;
    ctx.lineWidth = 0.5;
    ctx.stroke();
  }

  // 5 lichen spots
  for (let i = 0; i < 5; i++) {
    const lx = Math.random() * size;
    const ly = Math.random() * size;
    const lr = 3 + Math.random() * 6;
    ctx.beginPath();
    ctx.arc(lx, ly, lr, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(55,72,38,${0.2 + Math.random() * 0.15})`;
    ctx.fill();
  }

  return canvasToTexture(canvas, true);
}

export function createDeadWoodTexture(size = 128) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext('2d');

  // Gradient base (weathered grey-brown)
  const grad = ctx.createLinearGradient(0, 0, size, 0);
  grad.addColorStop(0, '#4a3e30');
  grad.addColorStop(0.5, '#554838');
  grad.addColorStop(1, '#4a3e30');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, size, size);

  // Broader grain bands
  for (let i = 0; i < 25; i++) {
    const y = Math.random() * size;
    const bw = 2 + Math.random() * 4;
    const shade = 50 + Math.random() * 45;
    ctx.fillStyle = `rgb(${Math.floor(shade)},${Math.floor(shade * 0.85)},${Math.floor(shade * 0.7)})`;
    ctx.fillRect(0, y, size, bw);
  }

  // Moss patches (larger, more visible)
  for (let i = 0; i < 8; i++) {
    const mx = Math.random() * size;
    const my = Math.random() * size;
    const mr = 5 + Math.random() * 10;
    const grad2 = ctx.createRadialGradient(mx, my, 0, mx, my, mr);
    grad2.addColorStop(0, `rgba(40,62,25,${0.3 + Math.random() * 0.15})`);
    grad2.addColorStop(1, 'rgba(40,62,25,0)');
    ctx.fillStyle = grad2;
    ctx.beginPath();
    ctx.arc(mx, my, mr, 0, Math.PI * 2);
    ctx.fill();
  }

  // Horizontal cracks
  for (let i = 0; i < 5; i++) {
    const y = Math.random() * size;
    ctx.beginPath();
    ctx.moveTo(0, y);
    for (let x = 0; x < size; x += 5) {
      ctx.lineTo(x, y + (Math.random() - 0.5) * 3);
    }
    ctx.strokeStyle = `rgba(20,15,10,${0.3 + Math.random() * 0.25})`;
    ctx.lineWidth = 0.8 + Math.random();
    ctx.stroke();
  }

  return canvasToTexture(canvas, true);
}

export function createFenceTexture(w = 32, h = 128) {
  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d');

  // Dark wood base
  ctx.fillStyle = '#3a2e20';
  ctx.fillRect(0, 0, w, h);

  // Broader vertical grain strokes
  for (let i = 0; i < 8; i++) {
    const x = Math.random() * w;
    const gw = 1.5 + Math.random() * 3;
    const shade = 38 + Math.random() * 30;
    ctx.fillStyle = `rgb(${shade + 18},${shade + 10},${shade})`;
    ctx.fillRect(x, 0, gw, h);
  }

  // A few horizontal cracks
  for (let i = 0; i < 4; i++) {
    const y = Math.random() * h;
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y + (Math.random() - 0.5) * 3);
    ctx.strokeStyle = `rgba(18,12,8,${0.3 + Math.random() * 0.25})`;
    ctx.lineWidth = 0.8 + Math.random() * 0.5;
    ctx.stroke();
  }

  return canvasToTexture(canvas, true);
}

export function createGravestoneTexture(size = 128) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext('2d');

  // Grey-green gradient base
  const grad = ctx.createLinearGradient(0, 0, 0, size);
  grad.addColorStop(0, '#5a5e50');
  grad.addColorStop(0.5, '#4a4e45');
  grad.addColorStop(1, '#3a3e38');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, size, size);

  // 4x4 block FBM overlay
  for (let y = 0; y < size; y += 4) {
    for (let x = 0; x < size; x += 4) {
      const n = fbm(x * 0.05, y * 0.05, 4);
      const shade = Math.floor(55 + n * 40);
      ctx.fillStyle = `rgba(${shade},${shade + 2},${shade - 3},0.3)`;
      ctx.fillRect(x, y, 4, 4);
    }
  }

  // 6 carved grooves (horizontal lines)
  for (let i = 0; i < 6; i++) {
    const y = size * 0.15 + (i / 6) * size * 0.7;
    ctx.beginPath();
    ctx.moveTo(size * 0.1, y);
    for (let x = size * 0.1; x < size * 0.9; x += 4) {
      ctx.lineTo(x, y + (Math.random() - 0.5) * 1.5);
    }
    ctx.strokeStyle = `rgba(30,32,28,${0.3 + Math.random() * 0.2})`;
    ctx.lineWidth = 1 + Math.random() * 0.5;
    ctx.stroke();
  }

  // 3 moss patches
  for (let i = 0; i < 3; i++) {
    const mx = Math.random() * size;
    const my = size * 0.6 + Math.random() * size * 0.4;
    const mr = 8 + Math.random() * 12;
    const g2 = ctx.createRadialGradient(mx, my, 0, mx, my, mr);
    g2.addColorStop(0, `rgba(45,65,35,${0.25 + Math.random() * 0.15})`);
    g2.addColorStop(1, 'rgba(45,65,35,0)');
    ctx.fillStyle = g2;
    ctx.beginPath();
    ctx.arc(mx, my, mr, 0, Math.PI * 2);
    ctx.fill();
  }

  // 8 cracks
  for (let i = 0; i < 8; i++) {
    ctx.beginPath();
    let cx = Math.random() * size;
    let cy = Math.random() * size;
    ctx.moveTo(cx, cy);
    for (let s = 0; s < 6; s++) {
      cx += (Math.random() - 0.5) * 10;
      cy += (Math.random() - 0.5) * 10;
      ctx.lineTo(cx, cy);
    }
    ctx.strokeStyle = `rgba(25,28,22,${0.3 + Math.random() * 0.25})`;
    ctx.lineWidth = 0.5 + Math.random() * 0.8;
    ctx.stroke();
  }

  // 4 weathering stains
  for (let i = 0; i < 4; i++) {
    const sx = Math.random() * size;
    const sy = Math.random() * size;
    const sr = 6 + Math.random() * 10;
    const g3 = ctx.createRadialGradient(sx, sy, 0, sx, sy, sr);
    g3.addColorStop(0, `rgba(40,38,32,${0.15 + Math.random() * 0.1})`);
    g3.addColorStop(1, 'rgba(40,38,32,0)');
    ctx.fillStyle = g3;
    ctx.beginPath();
    ctx.arc(sx, sy, sr, 0, Math.PI * 2);
    ctx.fill();
  }

  return canvasToTexture(canvas, true);
}

export function createIronTexture(size = 64) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext('2d');

  // Dark iron base
  ctx.fillStyle = '#2a2a2e';
  ctx.fillRect(0, 0, size, size);

  // Subtle FBM noise
  for (let y = 0; y < size; y += 2) {
    for (let x = 0; x < size; x += 2) {
      const n = fbm(x * 0.08, y * 0.08, 3);
      const shade = Math.floor(35 + n * 25);
      ctx.fillStyle = `rgba(${shade},${shade},${shade + 2},0.4)`;
      ctx.fillRect(x, y, 2, 2);
    }
  }

  // 5 rust spots
  for (let i = 0; i < 5; i++) {
    const rx = Math.random() * size;
    const ry = Math.random() * size;
    const rr = 3 + Math.random() * 6;
    const g2 = ctx.createRadialGradient(rx, ry, 0, rx, ry, rr);
    g2.addColorStop(0, `rgba(80,50,30,${0.2 + Math.random() * 0.15})`);
    g2.addColorStop(1, 'rgba(80,50,30,0)');
    ctx.fillStyle = g2;
    ctx.beginPath();
    ctx.arc(rx, ry, rr, 0, Math.PI * 2);
    ctx.fill();
  }

  // 3 highlight streaks
  for (let i = 0; i < 3; i++) {
    const sy = Math.random() * size;
    ctx.beginPath();
    ctx.moveTo(0, sy);
    ctx.lineTo(size, sy + (Math.random() - 0.5) * 4);
    ctx.strokeStyle = `rgba(65,65,70,${0.2 + Math.random() * 0.15})`;
    ctx.lineWidth = 0.8 + Math.random() * 0.5;
    ctx.stroke();
  }

  return canvasToTexture(canvas, true);
}
