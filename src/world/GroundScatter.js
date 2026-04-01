import * as THREE from 'three';
import { randomRange, displaceGeometryVertices } from '../utils/math.js';
import { patchMaterial } from '../fx/PSXEffect.js';
import { createRockTexture } from '../utils/ProceduralTextures.js';

export default class GroundScatter {
  constructor(scene) {
    this.scene = scene;
    this.instancedMeshes = [];
  }

  build(pathCurve, treeColliders) {
    const pathSamples = [];
    for (let t = 0; t <= 1; t += 0.01) {
      pathSamples.push(pathCurve.getPointAt(t));
    }

    this._buildGrass(pathSamples, treeColliders);
    this._buildLeaves(pathSamples, treeColliders);
    this._buildRocks(pathSamples, treeColliders);
    this._buildMushrooms(pathSamples, treeColliders);
    this._buildTwigs(pathSamples, treeColliders);
    this._buildPuddles(pathSamples, treeColliders);
  }

  _placeInstances(instanced, count, pathSamples, treeColliders, maxDist, callback) {
    const dummy = new THREE.Object3D();
    let placed = 0;
    let attempts = 0;
    const maxAttempts = count * 10;

    while (placed < count && attempts < maxAttempts) {
      attempts++;
      const sample = pathSamples[Math.floor(Math.random() * pathSamples.length)];

      const angle = Math.random() * Math.PI * 2;
      const dist = randomRange(1.5, maxDist);
      const x = sample.x + Math.cos(angle) * dist;
      const z = sample.z + Math.sin(angle) * dist;

      let blocked = false;
      for (const tree of treeColliders) {
        const dx = x - tree.x;
        const dz = z - tree.z;
        if (dx * dx + dz * dz < 1.0) {
          blocked = true;
          break;
        }
      }
      if (blocked) continue;

      callback(dummy, x, z, placed);
      dummy.updateMatrix();
      instanced.setMatrixAt(placed, dummy.matrix);
      placed++;
    }

    instanced.count = placed;
    instanced.instanceMatrix.needsUpdate = true;
  }

  _buildGrass(pathSamples, treeColliders) {
    const plane1 = new THREE.PlaneGeometry(0.2, 0.35);
    const plane2 = new THREE.PlaneGeometry(0.2, 0.35);
    plane2.rotateY(Math.PI / 2);
    const grassGeo = this._mergeGeometries([plane1, plane2]);
    grassGeo.translate(0, 0.18, 0);

    const grassMat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      side: THREE.DoubleSide,
      roughness: 0.9,
      metalness: 0,
      vertexColors: false,
    });
    patchMaterial(grassMat);

    const count = 700;
    const instanced = new THREE.InstancedMesh(grassGeo, grassMat, count);
    instanced.name = 'groundScatter-grass';

    // 5 cold/dead grass shades
    const grassColors = [
      new THREE.Color(0x2e3828),
      new THREE.Color(0x263020),
      new THREE.Color(0x343830),
      new THREE.Color(0x2a3428),
      new THREE.Color(0x303828),
    ];

    this._placeInstances(instanced, count, pathSamples, treeColliders, 8, (dummy, x, z, i) => {
      dummy.position.set(x, 0, z);
      dummy.rotation.set(0, Math.random() * Math.PI, 0);
      const s = randomRange(0.5, 1.2);
      dummy.scale.set(s, s * randomRange(0.8, 1.5), s);

      instanced.setColorAt(i, grassColors[Math.floor(Math.random() * grassColors.length)]);
    });

    if (instanced.instanceColor) instanced.instanceColor.needsUpdate = true;
    this.scene.add(instanced);
    this.instancedMeshes.push(instanced);
  }

  _buildLeaves(pathSamples, treeColliders) {
    const leafGeo = new THREE.PlaneGeometry(0.12, 0.08);
    leafGeo.rotateX(-Math.PI / 2);
    leafGeo.translate(0, 0.015, 0);

    const leafMat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      side: THREE.DoubleSide,
      roughness: 0.85,
      metalness: 0,
    });
    patchMaterial(leafMat);

    const count = 250;
    const instanced = new THREE.InstancedMesh(leafGeo, leafMat, count);
    instanced.name = 'groundScatter-leaves';

    // Dark decay leaf colors
    const autumnColors = [
      new THREE.Color(0x5a4030),
      new THREE.Color(0x4a3828),
      new THREE.Color(0x3a3028),
      new THREE.Color(0x504035),
      new THREE.Color(0x453528),
      new THREE.Color(0x3a2a20),
    ];

    this._placeInstances(instanced, count, pathSamples, treeColliders, 6, (dummy, x, z, i) => {
      dummy.position.set(x, 0.01, z);
      dummy.rotation.set(randomRange(-0.1, 0.1), Math.random() * Math.PI * 2, randomRange(-0.1, 0.1));
      const s = randomRange(0.8, 1.5);
      dummy.scale.set(s, 1, s);

      const c = autumnColors[Math.floor(Math.random() * autumnColors.length)];
      instanced.setColorAt(i, c);
    });

    if (instanced.instanceColor) instanced.instanceColor.needsUpdate = true;
    this.scene.add(instanced);
    this.instancedMeshes.push(instanced);
  }

  _buildRocks(pathSamples, treeColliders) {
    // IcosahedronGeometry(0.15, 1) = 80 faces for organic look
    const rockGeo = new THREE.IcosahedronGeometry(0.15, 1);
    displaceGeometryVertices(rockGeo, 0.03);

    const rockTex = createRockTexture(128);
    const rockMat = new THREE.MeshStandardMaterial({
      map: rockTex,
      color: 0xffffff,
      roughness: 0.92,
      metalness: 0,
    });
    patchMaterial(rockMat);

    const count = 150;
    const instanced = new THREE.InstancedMesh(rockGeo, rockMat, count);
    instanced.name = 'groundScatter-rocks';
    instanced.castShadow = true;
    instanced.receiveShadow = true;

    // 5 grey shades: neutral, warm, cool, brown, light
    const rockColors = [
      new THREE.Color(0x7a7a7a),
      new THREE.Color(0x8a7868),
      new THREE.Color(0x6a7280),
      new THREE.Color(0x7a6a58),
      new THREE.Color(0x8a8a88),
    ];

    this._placeInstances(instanced, count, pathSamples, treeColliders, 10, (dummy, x, z, i) => {
      dummy.position.set(x, randomRange(-0.02, 0.05), z);
      dummy.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
      const s = randomRange(0.4, 1.8);
      dummy.scale.set(s * randomRange(0.7, 1.3), s * randomRange(0.5, 1.0), s * randomRange(0.7, 1.3));

      instanced.setColorAt(i, rockColors[Math.floor(Math.random() * rockColors.length)]);
    });

    if (instanced.instanceColor) instanced.instanceColor.needsUpdate = true;
    this.scene.add(instanced);
    this.instancedMeshes.push(instanced);
  }

  _buildMushrooms(pathSamples, treeColliders) {
    const stem = new THREE.CylinderGeometry(0.02, 0.025, 0.08, 6);
    stem.translate(0, 0.04, 0);
    const cap = new THREE.SphereGeometry(0.04, 6, 4, 0, Math.PI * 2, 0, Math.PI / 2);
    cap.translate(0, 0.08, 0);
    const mushroomGeo = this._mergeGeometries([stem, cap]);

    const mushroomMat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      roughness: 0.8,
      metalness: 0,
    });
    patchMaterial(mushroomMat);

    const count = 40;
    const instanced = new THREE.InstancedMesh(mushroomGeo, mushroomMat, count);
    instanced.name = 'groundScatter-mushrooms';

    const mushroomColors = [
      new THREE.Color(0xc8a882),
      new THREE.Color(0xb89870),
      new THREE.Color(0xd0b090),
      new THREE.Color(0xc0a078),
    ];

    this._placeInstances(instanced, count, pathSamples, treeColliders, 5, (dummy, x, z, i) => {
      dummy.position.set(x, 0, z);
      dummy.rotation.set(0, Math.random() * Math.PI * 2, 0);
      const s = randomRange(0.6, 1.4);
      dummy.scale.set(s, s * randomRange(0.8, 1.3), s);

      instanced.setColorAt(i, mushroomColors[Math.floor(Math.random() * mushroomColors.length)]);
    });

    if (instanced.instanceColor) instanced.instanceColor.needsUpdate = true;
    this.scene.add(instanced);
    this.instancedMeshes.push(instanced);
  }

  _buildTwigs(pathSamples, treeColliders) {
    const twigGeo = new THREE.CylinderGeometry(0.008, 0.012, 0.4, 5);
    twigGeo.rotateZ(Math.PI / 2);
    twigGeo.translate(0, 0.01, 0);

    const twigMat = new THREE.MeshStandardMaterial({
      color: 0x5a4530,
      roughness: 0.9,
      metalness: 0,
    });
    patchMaterial(twigMat);

    const count = 150;
    const instanced = new THREE.InstancedMesh(twigGeo, twigMat, count);
    instanced.name = 'groundScatter-twigs';

    this._placeInstances(instanced, count, pathSamples, treeColliders, 7, (dummy, x, z) => {
      dummy.position.set(x, 0.005, z);
      dummy.rotation.set(
        randomRange(-0.05, 0.05),
        Math.random() * Math.PI * 2,
        randomRange(-0.05, 0.05)
      );
      const s = randomRange(0.6, 1.5);
      dummy.scale.set(s, 1, 1);
    });

    this.scene.add(instanced);
    this.instancedMeshes.push(instanced);
  }

  _buildPuddles(pathSamples, treeColliders) {
    const puddleGeo = new THREE.CircleGeometry(0.4, 8);
    puddleGeo.rotateX(-Math.PI / 2);
    puddleGeo.translate(0, 0.02, 0);

    const puddleMat = new THREE.MeshStandardMaterial({
      color: 0x1a1e28,
      roughness: 0.15,
      metalness: 0.6,
      transparent: true,
      opacity: 0.65,
    });
    // NOT PSX-patched — smooth/reflective

    const count = 30;
    const instanced = new THREE.InstancedMesh(puddleGeo, puddleMat, count);
    instanced.name = 'groundScatter-puddles';
    instanced.receiveShadow = true;

    this._placeInstances(instanced, count, pathSamples, treeColliders, 8, (dummy, x, z) => {
      dummy.position.set(x, 0.02, z);
      dummy.rotation.set(0, Math.random() * Math.PI * 2, 0);
      const s = randomRange(0.5, 2.0);
      dummy.scale.set(s * randomRange(0.6, 1.4), 1, s);
    });

    this.scene.add(instanced);
    this.instancedMeshes.push(instanced);
  }

  _mergeGeometries(geometries) {
    let totalVerts = 0;
    for (const g of geometries) {
      totalVerts += g.attributes.position.count;
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
    if (indices.length > 0) merged.setIndex(indices);
    return merged;
  }

  dispose() {
    for (const m of this.instancedMeshes) {
      m.geometry.dispose();
      if (m.material.map) m.material.map.dispose();
      m.material.dispose();
      this.scene.remove(m);
    }
    this.instancedMeshes = [];
  }
}
