import * as THREE from 'three';
import { randomRange } from '../utils/math.js';

export default class FallingLeaves {
  constructor(scene) {
    this.scene = scene;
    this.points = null;
    this._particles = [];
  }

  build(playerPosition) {
    const count = 100;
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    this._particles = [];

    const palette = [
      new THREE.Color(0x6b4226), // brown
      new THREE.Color(0x9b6b30), // amber
      new THREE.Color(0x4a3018), // dark brown
      new THREE.Color(0x7a7a70), // ash grey
      new THREE.Color(0xb87333), // copper
      new THREE.Color(0x6b8e23), // olive
    ];

    for (let i = 0; i < count; i++) {
      const px = playerPosition.x + randomRange(-25, 25);
      const py = randomRange(0.5, 8);
      const pz = playerPosition.z + randomRange(-25, 25);

      positions[i * 3] = px;
      positions[i * 3 + 1] = py;
      positions[i * 3 + 2] = pz;

      const c = palette[Math.floor(Math.random() * palette.length)];
      colors[i * 3] = c.r;
      colors[i * 3 + 1] = c.g;
      colors[i * 3 + 2] = c.b;

      this._particles.push({
        fallSpeed: randomRange(0.4, 1.0),
        swayAmplitude: randomRange(0.3, 0.8),
        swayFreqX: randomRange(0.5, 1.5),
        swayFreqZ: randomRange(0.5, 1.5),
        phase: Math.random() * Math.PI * 2,
      });
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 0.10,
      vertexColors: true,
      transparent: true,
      opacity: 0.75,
      blending: THREE.NormalBlending,
      depthWrite: false,
      sizeAttenuation: true,
    });

    this.points = new THREE.Points(geometry, material);
    this.points.name = 'fallingLeaves';
    this.scene.add(this.points);
  }

  update(delta, elapsed, playerPosition) {
    if (!this.points) return;

    const posAttr = this.points.geometry.attributes.position;
    const arr = posAttr.array;

    for (let i = 0; i < this._particles.length; i++) {
      const p = this._particles[i];
      const i3 = i * 3;

      // Fall downward
      arr[i3 + 1] -= p.fallSpeed * delta;

      // Sinusoidal lateral sway
      arr[i3] += Math.sin(elapsed * p.swayFreqX + p.phase) * p.swayAmplitude * delta;
      arr[i3 + 2] += Math.cos(elapsed * p.swayFreqZ + p.phase * 1.3) * p.swayAmplitude * delta;

      // Respawn at top when hitting ground
      if (arr[i3 + 1] < 0.1) {
        arr[i3 + 1] = randomRange(6, 9);
        arr[i3] = playerPosition.x + randomRange(-25, 25);
        arr[i3 + 2] = playerPosition.z + randomRange(-25, 25);
      }

      // Wrap around player position
      const dx = arr[i3] - playerPosition.x;
      const dz = arr[i3 + 2] - playerPosition.z;
      if (Math.abs(dx) > 25) arr[i3] = playerPosition.x + randomRange(-20, 20);
      if (Math.abs(dz) > 25) arr[i3 + 2] = playerPosition.z + randomRange(-20, 20);
    }

    posAttr.needsUpdate = true;
  }

  dispose() {
    if (this.points) {
      this.points.geometry.dispose();
      this.points.material.dispose();
      this.scene.remove(this.points);
    }
  }
}
