import * as THREE from 'three';
import { patchMaterial } from '../fx/PSXEffect.js';
import { createDirtTexture } from '../utils/ProceduralTextures.js';

export default class TerrainBuilder {
  constructor(scene) {
    this.scene = scene;
    this.mesh = null;
  }

  build() {
    const geometry = new THREE.PlaneGeometry(500, 500, 100, 100);
    geometry.rotateX(-Math.PI / 2);

    // Add subtle height variation
    const positions = geometry.attributes.position;
    for (let i = 0; i < positions.count; i++) {
      const x = positions.getX(i);
      const z = positions.getZ(i);
      const y = Math.sin(x * 0.05) * Math.cos(z * 0.05) * 0.7
              + Math.sin(x * 0.15 + z * 0.1) * 0.3
              + Math.sin(x * 0.8 + z * 0.6) * 0.03;
      positions.setY(i, y);
    }
    geometry.computeVertexNormals();

    // Vertex color variation — cold grey-brown gothic palette
    const colors = new Float32Array(positions.count * 3);
    const baseColor = new THREE.Color(0x3a3830);
    for (let i = 0; i < positions.count; i++) {
      const x = positions.getX(i);
      const z = positions.getZ(i);
      const noise = Math.sin(x * 0.3 + z * 0.2) * 0.15
                  + Math.sin(x * 0.7 - z * 0.5) * 0.08
                  + Math.sin(x * 1.5 + z * 1.2) * 0.05;
      // Green bias patches — less lively
      const greenBias = Math.max(0, Math.sin(x * 0.12 + z * 0.08) * 0.03);
      // Cold blue bias patches
      const coldBias = Math.max(0, Math.sin(x * 0.09 - z * 0.11) * 0.02);
      const r = Math.max(0, Math.min(1, baseColor.r + noise * 0.8));
      const g = Math.max(0, Math.min(1, baseColor.g + noise * 0.7 + greenBias));
      const b = Math.max(0, Math.min(1, baseColor.b + noise * 0.6 + coldBias));
      colors[i * 3] = r;
      colors[i * 3 + 1] = g;
      colors[i * 3 + 2] = b;
    }
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    // Tile UVs 40x40 across 200x200 terrain
    const uvs = geometry.attributes.uv;
    for (let i = 0; i < uvs.count; i++) {
      uvs.setXY(i, uvs.getX(i) * 100, uvs.getY(i) * 100);
    }

    const { map: dirtMap, normalMap: dirtNormal } = createDirtTexture();
    const material = new THREE.MeshStandardMaterial({
      map: dirtMap,
      normalMap: dirtNormal,
      normalScale: new THREE.Vector2(1.5, 1.5),
      vertexColors: true,
      roughness: 0.95,
      metalness: 0,
    });
    patchMaterial(material);

    this.mesh = new THREE.Mesh(geometry, material);
    this.mesh.receiveShadow = true;
    this.mesh.name = 'terrain';
    this.scene.add(this.mesh);

    return this.mesh;
  }

  dispose() {
    if (this.mesh) {
      this.mesh.geometry.dispose();
      if (this.mesh.material.map) this.mesh.material.map.dispose();
      if (this.mesh.material.normalMap) this.mesh.material.normalMap.dispose();
      this.mesh.material.dispose();
      this.scene.remove(this.mesh);
    }
  }
}
