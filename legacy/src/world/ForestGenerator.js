import * as THREE from 'three';
import { randomRange, displaceGeometryVertices } from '../utils/math.js';
import { patchMaterial } from '../fx/PSXEffect.js';
import { createBarkTexture, createFoliageTexture, createDeadWoodTexture } from '../utils/ProceduralTextures.js';

export default class ForestGenerator {
  constructor(scene) {
    this.scene = scene;
    this.instancedMeshes = [];
    this._colliders = [];
  }

  build(pathCurve) {
    const treeCount = 350;
    const variants = this._createTreeVariants();

    // Distribute counts across 4 variants
    const counts = [
      Math.floor(treeCount * 0.35),  // tall thin pines
      Math.floor(treeCount * 0.28),  // dead trees
      Math.floor(treeCount * 0.27),  // gnarled
      treeCount - Math.floor(treeCount * 0.35) - Math.floor(treeCount * 0.28) - Math.floor(treeCount * 0.27), // birch/forked (~35)
    ];

    // Generate positions avoiding the path
    const pathSamplePoints = [];
    for (let t = 0; t <= 1; t += 0.005) {
      pathSamplePoints.push(pathCurve.getPointAt(t));
    }

    for (let v = 0; v < variants.length; v++) {
      const variant = variants[v];
      const count = counts[v];

      const matrices = [];
      const dummy = new THREE.Object3D();
      let placed = 0;

      while (placed < count) {
        const x = randomRange(-90, 90);
        const z = randomRange(-90, 90);

        let tooClose = false;
        for (const pp of pathSamplePoints) {
          const dx = x - pp.x;
          const dz = z - pp.z;
          if (dx * dx + dz * dz < 12) {
            tooClose = true;
            break;
          }
        }
        if (tooClose) continue;

        dummy.position.set(x, 0, z);
        dummy.rotation.y = Math.random() * Math.PI * 2;
        const scale = randomRange(0.7, 1.3);
        dummy.scale.set(scale, scale * randomRange(0.8, 1.2), scale);
        dummy.updateMatrix();
        matrices.push(dummy.matrix.clone());
        placed++;
      }

      for (const part of variant) {
        const instanced = new THREE.InstancedMesh(part.geometry, part.material, count);
        instanced.castShadow = true;
        instanced.receiveShadow = true;
        instanced.name = part.name;

        for (let i = 0; i < matrices.length; i++) {
          instanced.setMatrixAt(i, matrices[i]);
        }

        instanced.instanceMatrix.needsUpdate = true;
        this.scene.add(instanced);
        this.instancedMeshes.push(instanced);
      }
    }

    this._createColliders(pathCurve);
    return this._colliders;
  }

  _createTreeVariants() {
    const { map: barkMap, normalMap: barkNormal } = createBarkTexture();
    const { map: foliageMap, normalMap: foliageNormal } = createFoliageTexture();
    const { map: deadWoodMap, normalMap: deadWoodNormal } = createDeadWoodTexture();

    // Variant 0: Tall pine — warm brown trunk + cool green canopy
    const pineTrunk = this._createPineTrunkGeometry();
    const pineTrunkMat = new THREE.MeshStandardMaterial({
      map: barkMap,
      normalMap: barkNormal,
      normalScale: new THREE.Vector2(1.0, 1.0),
      color: 0x7a5540,
      roughness: 0.9,
      metalness: 0,
    });
    patchMaterial(pineTrunkMat);

    const pineCanopy = this._createPineCanopyGeometry();
    const pineCanopyMat = new THREE.MeshStandardMaterial({
      map: foliageMap,
      normalMap: foliageNormal,
      normalScale: new THREE.Vector2(0.4, 0.4),
      color: 0x2a5538,
      roughness: 0.85,
      metalness: 0,
    });
    patchMaterial(pineCanopyMat);

    // Variant 1: Dead tree — pale grey
    const dead = this._createDeadTreeGeometry();
    this._computeCylindricalUVs(dead);
    const deadMat = new THREE.MeshStandardMaterial({
      map: deadWoodMap,
      normalMap: deadWoodNormal,
      normalScale: new THREE.Vector2(1.2, 1.2),
      color: 0x807060,
      roughness: 0.9,
      metalness: 0,
    });
    patchMaterial(deadMat);

    // Variant 2: Gnarled thick tree — dark trunk + warm green canopy
    const gnarledTrunk = this._createGnarledTrunkGeometry();
    const gnarledTrunkMat = new THREE.MeshStandardMaterial({
      map: barkMap,
      normalMap: barkNormal,
      normalScale: new THREE.Vector2(1.0, 1.0),
      color: 0x4a3520,
      roughness: 0.9,
      metalness: 0,
    });
    patchMaterial(gnarledTrunkMat);

    const gnarledCanopy = this._createGnarledCanopyGeometry();
    const gnarledCanopyMat = new THREE.MeshStandardMaterial({
      map: foliageMap,
      normalMap: foliageNormal,
      normalScale: new THREE.Vector2(0.4, 0.4),
      color: 0x3a5830,
      roughness: 0.85,
      metalness: 0,
    });
    patchMaterial(gnarledCanopyMat);

    // Variant 3: Birch/forked tree — lighter silver trunk, no canopy
    const birch = this._createBirchGeometry();
    this._computeCylindricalUVs(birch);
    const birchMat = new THREE.MeshStandardMaterial({
      map: barkMap,
      normalMap: barkNormal,
      normalScale: new THREE.Vector2(1.0, 1.0),
      color: 0x8a8070,
      roughness: 0.85,
      metalness: 0,
    });
    patchMaterial(birchMat);

    return [
      [
        { geometry: pineTrunk, material: pineTrunkMat, name: 'trees-pine-trunk' },
        { geometry: pineCanopy, material: pineCanopyMat, name: 'trees-pine-canopy' },
      ],
      [
        { geometry: dead, material: deadMat, name: 'trees-dead' },
      ],
      [
        { geometry: gnarledTrunk, material: gnarledTrunkMat, name: 'trees-gnarled-trunk' },
        { geometry: gnarledCanopy, material: gnarledCanopyMat, name: 'trees-gnarled-canopy' },
      ],
      [
        { geometry: birch, material: birchMat, name: 'trees-birch' },
      ],
    ];
  }

  _createPineTrunkGeometry() {
    const trunk = new THREE.CylinderGeometry(0.12, 0.18, 6, 8, 4);
    trunk.translate(0, 3, 0);
    displaceGeometryVertices(trunk, 0.02);
    this._computeCylindricalUVs(trunk);
    return trunk;
  }

  _createPineCanopyGeometry() {
    const foliage1 = new THREE.ConeGeometry(1.8, 3, 8);
    foliage1.translate(0, 5.5, 0);
    displaceGeometryVertices(foliage1, 0.15);

    const foliage2 = new THREE.ConeGeometry(1.4, 2.5, 8);
    foliage2.translate(0, 7, 0);
    displaceGeometryVertices(foliage2, 0.12);

    const foliage3 = new THREE.ConeGeometry(0.9, 2, 8);
    foliage3.translate(0, 8.2, 0);
    displaceGeometryVertices(foliage3, 0.08);

    const merged = this._mergeGeometries([foliage1, foliage2, foliage3]);
    this._computeSphericalUVs(merged);
    return merged;
  }

  _createDeadTreeGeometry() {
    const trunk = new THREE.CylinderGeometry(0.08, 0.22, 5, 8, 3);
    trunk.translate(0, 2.5, 0);
    displaceGeometryVertices(trunk, 0.02);

    const branch1 = new THREE.CylinderGeometry(0.03, 0.06, 2, 6);
    branch1.rotateZ(Math.PI / 4);
    branch1.translate(0.8, 3.5, 0);

    const branch2 = new THREE.CylinderGeometry(0.03, 0.05, 1.5, 6);
    branch2.rotateZ(-Math.PI / 3);
    branch2.translate(-0.6, 4, 0.2);

    // 3rd branch + sub-fork
    const branch3 = new THREE.CylinderGeometry(0.025, 0.05, 1.2, 6);
    branch3.rotateZ(Math.PI / 5);
    branch3.translate(0.4, 4.3, -0.3);

    const subFork = new THREE.CylinderGeometry(0.02, 0.03, 0.8, 5);
    subFork.rotateZ(Math.PI / 3);
    subFork.translate(1.3, 4.0, 0.1);

    return this._mergeGeometries([trunk, branch1, branch2, branch3, subFork]);
  }

  _createGnarledTrunkGeometry() {
    const trunk = new THREE.CylinderGeometry(0.15, 0.35, 4, 8, 3);
    trunk.translate(0, 2, 0);
    displaceGeometryVertices(trunk, 0.04);
    this._computeCylindricalUVs(trunk);
    return trunk;
  }

  _createGnarledCanopyGeometry() {
    const canopy = new THREE.SphereGeometry(2.2, 8, 6);
    canopy.translate(0, 4.5, 0);
    canopy.scale(1, 0.7, 1);
    displaceGeometryVertices(canopy, 0.25);
    this._computeSphericalUVs(canopy);
    return canopy;
  }

  _createBirchGeometry() {
    // Tall trunk with 2 diverging forks
    const trunk = new THREE.CylinderGeometry(0.1, 0.2, 5.5, 8, 4);
    trunk.translate(0, 2.75, 0);
    displaceGeometryVertices(trunk, 0.02);

    const fork1 = new THREE.CylinderGeometry(0.05, 0.1, 3, 6, 2);
    fork1.rotateZ(Math.PI / 7);
    fork1.translate(0.5, 6, 0);
    displaceGeometryVertices(fork1, 0.02);

    const fork2 = new THREE.CylinderGeometry(0.05, 0.1, 2.8, 6, 2);
    fork2.rotateZ(-Math.PI / 6);
    fork2.translate(-0.4, 5.8, 0.2);
    displaceGeometryVertices(fork2, 0.02);

    return this._mergeGeometries([trunk, fork1, fork2]);
  }

  _computeCylindricalUVs(geometry) {
    const pos = geometry.attributes.position;
    const uvs = new Float32Array(pos.count * 2);

    let minY = Infinity, maxY = -Infinity;
    for (let i = 0; i < pos.count; i++) {
      const y = pos.getY(i);
      if (y < minY) minY = y;
      if (y > maxY) maxY = y;
    }
    const rangeY = maxY - minY || 1;

    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const z = pos.getZ(i);
      const y = pos.getY(i);

      uvs[i * 2] = (Math.atan2(z, x) / Math.PI + 1) * 0.5;
      uvs[i * 2 + 1] = (y - minY) / rangeY;
    }

    geometry.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
  }

  _computeSphericalUVs(geometry) {
    const pos = geometry.attributes.position;
    const uvs = new Float32Array(pos.count * 2);

    let cx = 0, cy = 0, cz = 0;
    for (let i = 0; i < pos.count; i++) {
      cx += pos.getX(i);
      cy += pos.getY(i);
      cz += pos.getZ(i);
    }
    cx /= pos.count;
    cy /= pos.count;
    cz /= pos.count;

    for (let i = 0; i < pos.count; i++) {
      const dx = pos.getX(i) - cx;
      const dy = pos.getY(i) - cy;
      const dz = pos.getZ(i) - cz;

      const r = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1;
      uvs[i * 2] = (Math.atan2(dz, dx) / Math.PI + 1) * 0.5;
      uvs[i * 2 + 1] = Math.acos(Math.max(-1, Math.min(1, dy / r))) / Math.PI;
    }

    geometry.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
  }

  _mergeGeometries(geometries) {
    let totalVerts = 0;
    let totalIdx = 0;
    for (const g of geometries) {
      totalVerts += g.attributes.position.count;
      totalIdx += g.index ? g.index.count : 0;
    }

    const positions = new Float32Array(totalVerts * 3);
    const normals = new Float32Array(totalVerts * 3);
    const indices = [];

    let vertOffset = 0;

    for (const g of geometries) {
      const pos = g.attributes.position;
      const norm = g.attributes.normal;

      for (let i = 0; i < pos.count; i++) {
        positions[(vertOffset + i) * 3] = pos.getX(i);
        positions[(vertOffset + i) * 3 + 1] = pos.getY(i);
        positions[(vertOffset + i) * 3 + 2] = pos.getZ(i);

        if (norm) {
          normals[(vertOffset + i) * 3] = norm.getX(i);
          normals[(vertOffset + i) * 3 + 1] = norm.getY(i);
          normals[(vertOffset + i) * 3 + 2] = norm.getZ(i);
        }
      }

      if (g.index) {
        for (let i = 0; i < g.index.count; i++) {
          indices.push(g.index.getX(i) + vertOffset);
        }
      }

      vertOffset += pos.count;
      g.dispose();
    }

    const merged = new THREE.BufferGeometry();
    merged.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    merged.setAttribute('normal', new THREE.BufferAttribute(normals, 3));
    if (indices.length > 0) {
      merged.setIndex(indices);
    }

    return merged;
  }

  _createColliders(pathCurve) {
    const pathSamples = [];
    for (let t = 0; t <= 1; t += 0.02) {
      pathSamples.push(pathCurve.getPointAt(t));
    }

    const matrix = new THREE.Matrix4();
    const position = new THREE.Vector3();

    for (const instanced of this.instancedMeshes) {
      for (let i = 0; i < instanced.count; i++) {
        instanced.getMatrixAt(i, matrix);
        position.setFromMatrixPosition(matrix);

        let nearPath = false;
        for (const pp of pathSamples) {
          const dx = position.x - pp.x;
          const dz = position.z - pp.z;
          if (dx * dx + dz * dz < 100) {
            nearPath = true;
            break;
          }
        }

        if (nearPath) {
          this._colliders.push({ x: position.x, z: position.z, radius: 0.6 });
        }
      }
    }
  }

  get colliders() {
    return this._colliders;
  }

  dispose() {
    for (const m of this.instancedMeshes) {
      m.geometry.dispose();
      if (m.material.map) m.material.map.dispose();
      if (m.material.normalMap) m.material.normalMap.dispose();
      m.material.dispose();
      this.scene.remove(m);
    }
    this.instancedMeshes = [];
    this._colliders = [];
  }
}
