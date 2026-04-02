export function lerp(a, b, t) {
  return a + (b - a) * t;
}

export function easeInOutCubic(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

export function randomRange(min, max) {
  return min + Math.random() * (max - min);
}

export function gaussian(x, mean, sigma) {
  return Math.exp(-0.5 * Math.pow((x - mean) / sigma, 2));
}

export function displaceGeometryVertices(geometry, amount) {
  const pos = geometry.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i);
    const y = pos.getY(i);
    const z = pos.getZ(i);
    // Position-based hash for deterministic displacement
    const hash1 = Math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453;
    const hash2 = Math.sin(x * 269.5 + y * 183.3 + z * 246.1) * 43758.5453;
    const hash3 = Math.sin(x * 420.2 + y * 631.2 + z * 164.7) * 43758.5453;
    const dx = (hash1 - Math.floor(hash1) - 0.5) * 2 * amount;
    const dy = (hash2 - Math.floor(hash2) - 0.5) * 2 * amount;
    const dz = (hash3 - Math.floor(hash3) - 0.5) * 2 * amount;
    pos.setXYZ(i, x + dx, y + dy, z + dz);
  }
  geometry.computeVertexNormals();
}
