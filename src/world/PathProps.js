import * as THREE from 'three';
import { randomRange, displaceGeometryVertices } from '../utils/math.js';
import { patchMaterial } from '../fx/PSXEffect.js';
import { createFenceTexture, createRockTexture, createDeadWoodTexture, createGravestoneTexture, createIronTexture } from '../utils/ProceduralTextures.js';

export default class PathProps {
  constructor(scene) {
    this.scene = scene;
    this.instancedMeshes = [];
    this._staticMeshes = [];
  }

  build(pathCurve, treeColliders) {
    const pathSamples = [];
    for (let t = 0; t <= 1; t += 0.005) {
      pathSamples.push({
        point: pathCurve.getPointAt(t),
        tangent: pathCurve.getTangentAt(t),
        t,
      });
    }

    this._buildFencePosts(pathCurve, pathSamples, treeColliders);
    this._buildStoneMarkers(pathCurve, pathSamples, treeColliders);
    this._buildFallenLogs(pathCurve, pathSamples, treeColliders);
    this._buildGateArch(pathCurve);
    this._buildGravestones(pathCurve, pathSamples, treeColliders);
    this._buildWoodenCrosses(pathCurve, pathSamples, treeColliders);
    this._buildRuinedWalls(pathCurve, pathSamples, treeColliders);
    this._buildStonePillars(pathCurve, pathSamples, treeColliders);
    this._buildIronLanterns(pathCurve);
  }

  _isBlockedByTree(x, z, treeColliders, minDist = 1.2) {
    for (const tree of treeColliders) {
      const dx = x - tree.x;
      const dz = z - tree.z;
      if (dx * dx + dz * dz < minDist * minDist) return true;
    }
    return false;
  }

  _buildFencePosts(pathCurve, pathSamples, treeColliders) {
    const geo = new THREE.CylinderGeometry(0.04, 0.07, 1.2, 7);
    geo.translate(0, 0.6, 0);
    const fenceTex = createFenceTexture(32, 128);
    const mat = new THREE.MeshStandardMaterial({
      map: fenceTex,
      color: 0x6a5530,
      roughness: 0.9,
      metalness: 0,
    });
    patchMaterial(mat);

    const count = 30;
    const instanced = new THREE.InstancedMesh(geo, mat, count);
    instanced.castShadow = true;
    instanced.receiveShadow = true;
    instanced.name = 'pathProps-fencePosts';

    const dummy = new THREE.Object3D();
    let placed = 0;

    for (let i = 0; i < count * 3 && placed < count; i++) {
      const t = randomRange(0.05, 0.95);
      const point = pathCurve.getPointAt(t);
      const tangent = pathCurve.getTangentAt(t);
      const normal = new THREE.Vector3().crossVectors(tangent, new THREE.Vector3(0, 1, 0)).normalize();

      const side = Math.random() < 0.5 ? 1 : -1;
      const dist = randomRange(2, 4);
      const x = point.x + normal.x * side * dist;
      const z = point.z + normal.z * side * dist;

      if (this._isBlockedByTree(x, z, treeColliders)) continue;

      dummy.position.set(x, 0, z);
      dummy.rotation.set(
        randomRange(-0.12, 0.12),
        Math.random() * Math.PI * 2,
        randomRange(-0.12, 0.12)
      );
      const s = randomRange(0.8, 1.3);
      dummy.scale.set(s, s * randomRange(0.7, 1.2), s);
      dummy.updateMatrix();
      instanced.setMatrixAt(placed, dummy.matrix);
      placed++;
    }

    instanced.count = placed;
    instanced.instanceMatrix.needsUpdate = true;
    this.scene.add(instanced);
    this.instancedMeshes.push(instanced);
  }

  _buildStoneMarkers(pathCurve, pathSamples, treeColliders) {
    const geo = new THREE.IcosahedronGeometry(0.22, 1);
    displaceGeometryVertices(geo, 0.03);
    geo.scale(0.7, 1, 0.6);
    geo.translate(0, 0.2, 0);
    const rockTex = createRockTexture(128);
    const mat = new THREE.MeshStandardMaterial({
      map: rockTex,
      color: 0x7a7860,
      roughness: 0.92,
      metalness: 0,
    });
    patchMaterial(mat);

    const count = 15;
    const instanced = new THREE.InstancedMesh(geo, mat, count);
    instanced.castShadow = true;
    instanced.receiveShadow = true;
    instanced.name = 'pathProps-stoneMarkers';

    const dummy = new THREE.Object3D();
    let placed = 0;

    for (let i = 0; i < count * 5 && placed < count; i++) {
      const t = randomRange(0.08, 0.92);
      const point = pathCurve.getPointAt(t);
      const tangent = pathCurve.getTangentAt(t);
      const normal = new THREE.Vector3().crossVectors(tangent, new THREE.Vector3(0, 1, 0)).normalize();

      const side = Math.random() < 0.5 ? 1 : -1;
      const dist = randomRange(1.8, 3.5);
      const x = point.x + normal.x * side * dist;
      const z = point.z + normal.z * side * dist;

      if (this._isBlockedByTree(x, z, treeColliders)) continue;

      dummy.position.set(x, 0, z);
      dummy.rotation.set(
        randomRange(-0.08, 0.08),
        Math.random() * Math.PI * 2,
        randomRange(-0.08, 0.08)
      );
      const sx = randomRange(0.6, 1.4);
      const sy = randomRange(0.5, 1.5);
      const sz = randomRange(0.6, 1.4);
      dummy.scale.set(sx, sy, sz);
      dummy.updateMatrix();
      instanced.setMatrixAt(placed, dummy.matrix);
      placed++;
    }

    instanced.count = placed;
    instanced.instanceMatrix.needsUpdate = true;
    this.scene.add(instanced);
    this.instancedMeshes.push(instanced);
  }

  _buildFallenLogs(pathCurve, pathSamples, treeColliders) {
    const geo = new THREE.CylinderGeometry(0.12, 0.15, 2.5, 8, 3);
    displaceGeometryVertices(geo, 0.02);
    geo.rotateZ(Math.PI / 2);
    geo.translate(0, 0.12, 0);
    const deadWoodTex = createDeadWoodTexture(128);
    const mat = new THREE.MeshStandardMaterial({
      map: deadWoodTex,
      color: 0x5a4a28,
      roughness: 0.9,
      metalness: 0,
    });
    patchMaterial(mat);

    const count = 12;
    const instanced = new THREE.InstancedMesh(geo, mat, count);
    instanced.castShadow = true;
    instanced.receiveShadow = true;
    instanced.name = 'pathProps-fallenLogs';

    const dummy = new THREE.Object3D();
    let placed = 0;

    for (let i = 0; i < count * 6 && placed < count; i++) {
      const t = randomRange(0.1, 0.9);
      const point = pathCurve.getPointAt(t);
      const tangent = pathCurve.getTangentAt(t);
      const normal = new THREE.Vector3().crossVectors(tangent, new THREE.Vector3(0, 1, 0)).normalize();

      const side = Math.random() < 0.5 ? 1 : -1;
      const dist = randomRange(2.5, 5);
      const x = point.x + normal.x * side * dist;
      const z = point.z + normal.z * side * dist;

      if (this._isBlockedByTree(x, z, treeColliders)) continue;

      dummy.position.set(x, 0, z);
      dummy.rotation.set(
        randomRange(-0.1, 0.1),
        Math.random() * Math.PI * 2,
        randomRange(-0.05, 0.05)
      );
      const s = randomRange(0.7, 1.3);
      dummy.scale.set(s, s * randomRange(0.8, 1.2), s);
      dummy.updateMatrix();
      instanced.setMatrixAt(placed, dummy.matrix);
      placed++;
    }

    instanced.count = placed;
    instanced.instanceMatrix.needsUpdate = true;
    this.scene.add(instanced);
    this.instancedMeshes.push(instanced);
  }

  _buildGateArch(pathCurve) {
    const group = new THREE.Group();
    group.name = 'pathProps-gateArch';

    const fenceTex = createFenceTexture(32, 128);
    const postMat = new THREE.MeshStandardMaterial({
      map: fenceTex,
      color: 0x6a5530,
      roughness: 0.9,
      metalness: 0,
    });
    const deadWoodTex = createDeadWoodTexture(128);
    const beamMat = new THREE.MeshStandardMaterial({
      map: deadWoodTex,
      color: 0x5a4a28,
      roughness: 0.9,
      metalness: 0,
    });
    patchMaterial(postMat);
    patchMaterial(beamMat);

    const t = 0.15;
    const pos = pathCurve.getPointAt(t);
    const tangent = pathCurve.getTangentAt(t);
    const normal = new THREE.Vector3().crossVectors(tangent, new THREE.Vector3(0, 1, 0)).normalize();

    const postHeight = 3.0;
    const gateWidth = 2.2;

    // Left post
    const leftPostGeo = new THREE.CylinderGeometry(0.08, 0.12, postHeight, 6);
    const leftPost = new THREE.Mesh(leftPostGeo, postMat);
    leftPost.position.set(
      pos.x + normal.x * gateWidth / 2,
      postHeight / 2,
      pos.z + normal.z * gateWidth / 2
    );
    leftPost.castShadow = true;
    group.add(leftPost);

    // Right post
    const rightPostGeo = new THREE.CylinderGeometry(0.08, 0.12, postHeight, 6);
    const rightPost = new THREE.Mesh(rightPostGeo, postMat);
    rightPost.position.set(
      pos.x - normal.x * gateWidth / 2,
      postHeight / 2,
      pos.z - normal.z * gateWidth / 2
    );
    rightPost.castShadow = true;
    group.add(rightPost);

    // Crossbeam
    const beamLength = gateWidth + 0.3;
    const beamGeo = new THREE.CylinderGeometry(0.06, 0.06, beamLength, 5);
    beamGeo.rotateZ(Math.PI / 2);
    const beam = new THREE.Mesh(beamGeo, beamMat);

    beam.position.set(pos.x, postHeight - 0.06, pos.z);
    const angle = Math.atan2(normal.z, normal.x);
    beam.rotation.y = -angle;
    beam.castShadow = true;
    group.add(beam);

    this.scene.add(group);
    this._staticMeshes.push(group);
  }

  _mergeGeometries(geometries) {
    let totalVerts = 0;
    for (const g of geometries) totalVerts += g.attributes.position.count;

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

  _buildGravestones(pathCurve, pathSamples, treeColliders) {
    const geo = new THREE.BoxGeometry(0.35, 0.8, 0.08, 4, 4, 1);
    displaceGeometryVertices(geo, 0.015);
    geo.translate(0, 0.4, 0);

    const gravestoneTex = createGravestoneTexture(128);
    const mat = new THREE.MeshStandardMaterial({
      map: gravestoneTex,
      color: 0x606858,
      roughness: 0.92,
      metalness: 0,
    });
    patchMaterial(mat);

    const count = 20;
    const instanced = new THREE.InstancedMesh(geo, mat, count);
    instanced.castShadow = true;
    instanced.receiveShadow = true;
    instanced.name = 'pathProps-gravestones';

    const dummy = new THREE.Object3D();
    let placed = 0;

    for (let i = 0; i < count * 5 && placed < count; i++) {
      const t = randomRange(0.1, 0.9);
      const point = pathCurve.getPointAt(t);
      const tangent = pathCurve.getTangentAt(t);
      const normal = new THREE.Vector3().crossVectors(tangent, new THREE.Vector3(0, 1, 0)).normalize();

      const side = Math.random() < 0.5 ? 1 : -1;
      const dist = randomRange(3, 6);
      const x = point.x + normal.x * side * dist;
      const z = point.z + normal.z * side * dist;

      if (this._isBlockedByTree(x, z, treeColliders)) continue;

      dummy.position.set(x, 0, z);
      dummy.rotation.set(
        randomRange(-0.06, 0.06),
        Math.random() * Math.PI * 2,
        randomRange(-0.1, 0.1)
      );
      const s = randomRange(0.8, 1.3);
      dummy.scale.set(s, s * randomRange(0.8, 1.4), s);
      dummy.updateMatrix();
      instanced.setMatrixAt(placed, dummy.matrix);
      placed++;
    }

    instanced.count = placed;
    instanced.instanceMatrix.needsUpdate = true;
    this.scene.add(instanced);
    this.instancedMeshes.push(instanced);
  }

  _buildWoodenCrosses(pathCurve, pathSamples, treeColliders) {
    const vertical = new THREE.BoxGeometry(0.06, 0.9, 0.06);
    vertical.translate(0, 0.45, 0);
    const horizontal = new THREE.BoxGeometry(0.5, 0.06, 0.06);
    horizontal.translate(0, 0.65, 0);
    const crossGeo = this._mergeGeometries([vertical, horizontal]);

    const fenceTex = createFenceTexture(32, 128);
    const mat = new THREE.MeshStandardMaterial({
      map: fenceTex,
      color: 0x4a3a25,
      roughness: 0.9,
      metalness: 0,
    });
    patchMaterial(mat);

    const count = 10;
    const instanced = new THREE.InstancedMesh(crossGeo, mat, count);
    instanced.castShadow = true;
    instanced.receiveShadow = true;
    instanced.name = 'pathProps-woodenCrosses';

    const dummy = new THREE.Object3D();
    let placed = 0;

    for (let i = 0; i < count * 5 && placed < count; i++) {
      const t = randomRange(0.1, 0.9);
      const point = pathCurve.getPointAt(t);
      const tangent = pathCurve.getTangentAt(t);
      const normal = new THREE.Vector3().crossVectors(tangent, new THREE.Vector3(0, 1, 0)).normalize();

      const side = Math.random() < 0.5 ? 1 : -1;
      const dist = randomRange(3, 7);
      const x = point.x + normal.x * side * dist;
      const z = point.z + normal.z * side * dist;

      if (this._isBlockedByTree(x, z, treeColliders)) continue;

      dummy.position.set(x, 0, z);
      dummy.rotation.set(0, Math.random() * Math.PI * 2, randomRange(-0.15, 0.15));
      const s = randomRange(0.8, 1.2);
      dummy.scale.set(s, s, s);
      dummy.updateMatrix();
      instanced.setMatrixAt(placed, dummy.matrix);
      placed++;
    }

    instanced.count = placed;
    instanced.instanceMatrix.needsUpdate = true;
    this.scene.add(instanced);
    this.instancedMeshes.push(instanced);
  }

  _buildRuinedWalls(pathCurve, pathSamples, treeColliders) {
    const geo = new THREE.BoxGeometry(2.5, 1.8, 0.25, 4, 4, 1);
    displaceGeometryVertices(geo, 0.06);
    geo.translate(0, 0.9, 0);

    const rockTex = createRockTexture(128);
    const mat = new THREE.MeshStandardMaterial({
      map: rockTex,
      color: 0x585850,
      roughness: 0.95,
      metalness: 0,
    });
    patchMaterial(mat);

    const count = 8;
    const instanced = new THREE.InstancedMesh(geo, mat, count);
    instanced.castShadow = true;
    instanced.receiveShadow = true;
    instanced.name = 'pathProps-ruinedWalls';

    const dummy = new THREE.Object3D();
    let placed = 0;

    for (let i = 0; i < count * 6 && placed < count; i++) {
      const t = randomRange(0.1, 0.9);
      const point = pathCurve.getPointAt(t);
      const tangent = pathCurve.getTangentAt(t);
      const normal = new THREE.Vector3().crossVectors(tangent, new THREE.Vector3(0, 1, 0)).normalize();

      const side = Math.random() < 0.5 ? 1 : -1;
      const dist = randomRange(5, 9);
      const x = point.x + normal.x * side * dist;
      const z = point.z + normal.z * side * dist;

      if (this._isBlockedByTree(x, z, treeColliders, 2.0)) continue;

      dummy.position.set(x, 0, z);
      dummy.rotation.set(
        randomRange(-0.05, 0.05),
        Math.random() * Math.PI * 2,
        randomRange(-0.05, 0.05)
      );
      const s = randomRange(0.7, 1.2);
      dummy.scale.set(s, s * randomRange(0.6, 1.0), s);
      dummy.updateMatrix();
      instanced.setMatrixAt(placed, dummy.matrix);
      placed++;
    }

    instanced.count = placed;
    instanced.instanceMatrix.needsUpdate = true;
    this.scene.add(instanced);
    this.instancedMeshes.push(instanced);
  }

  _buildStonePillars(pathCurve, pathSamples, treeColliders) {
    const cylinder = new THREE.CylinderGeometry(0.18, 0.22, 2.2, 8);
    cylinder.translate(0, 1.1, 0);
    const cap = new THREE.BoxGeometry(0.55, 0.15, 0.55);
    cap.translate(0, 2.28, 0);
    const pillarGeo = this._mergeGeometries([cylinder, cap]);
    displaceGeometryVertices(pillarGeo, 0.02);

    const gravestoneTex = createGravestoneTexture(128);
    const mat = new THREE.MeshStandardMaterial({
      map: gravestoneTex,
      color: 0x5a5a55,
      roughness: 0.9,
      metalness: 0,
    });
    patchMaterial(mat);

    const count = 6;
    const instanced = new THREE.InstancedMesh(pillarGeo, mat, count);
    instanced.castShadow = true;
    instanced.receiveShadow = true;
    instanced.name = 'pathProps-stonePillars';

    const dummy = new THREE.Object3D();
    let placed = 0;

    for (let i = 0; i < count * 6 && placed < count; i++) {
      const t = randomRange(0.1, 0.9);
      const point = pathCurve.getPointAt(t);
      const tangent = pathCurve.getTangentAt(t);
      const normal = new THREE.Vector3().crossVectors(tangent, new THREE.Vector3(0, 1, 0)).normalize();

      const side = Math.random() < 0.5 ? 1 : -1;
      const dist = randomRange(3, 7);
      const x = point.x + normal.x * side * dist;
      const z = point.z + normal.z * side * dist;

      if (this._isBlockedByTree(x, z, treeColliders)) continue;

      dummy.position.set(x, 0, z);
      dummy.rotation.set(
        randomRange(-0.03, 0.03),
        Math.random() * Math.PI * 2,
        randomRange(-0.03, 0.03)
      );
      const s = randomRange(0.8, 1.1);
      dummy.scale.set(s, s, s);
      dummy.updateMatrix();
      instanced.setMatrixAt(placed, dummy.matrix);
      placed++;
    }

    instanced.count = placed;
    instanced.instanceMatrix.needsUpdate = true;
    this.scene.add(instanced);
    this.instancedMeshes.push(instanced);
  }

  _buildIronLanterns(pathCurve) {
    const ironTex = createIronTexture(64);

    for (let i = 0; i < 6; i++) {
      const group = new THREE.Group();
      group.name = `pathProps-ironLantern-${i}`;

      const t = (i + 0.5) / 7;
      const point = pathCurve.getPointAt(t);
      const tangent = pathCurve.getTangentAt(t);
      const normal = new THREE.Vector3().crossVectors(tangent, new THREE.Vector3(0, 1, 0)).normalize();

      const side = i % 2 === 0 ? 1 : -1;
      const dist = randomRange(2, 3.5);
      const x = point.x + normal.x * side * dist;
      const z = point.z + normal.z * side * dist;

      // Post
      const postGeo = new THREE.CylinderGeometry(0.03, 0.04, 2.8, 6);
      const postMat = new THREE.MeshStandardMaterial({
        map: ironTex,
        color: 0x2a2a30,
        roughness: 0.85,
        metalness: 0.3,
      });
      patchMaterial(postMat);
      const post = new THREE.Mesh(postGeo, postMat);
      post.position.set(x, 1.4, z);
      post.castShadow = true;
      group.add(post);

      // Lantern head
      const headGeo = new THREE.IcosahedronGeometry(0.12, 0);
      const headMat = new THREE.MeshStandardMaterial({
        color: 0x3a3530,
        roughness: 0.7,
        metalness: 0.4,
        transparent: true,
        opacity: 0.8,
      });
      patchMaterial(headMat);
      const head = new THREE.Mesh(headGeo, headMat);
      head.position.set(x, 2.8, z);
      group.add(head);

      // Point light
      const light = new THREE.PointLight(0xcc8844, 1.2, 10);
      light.position.set(x, 2.7, z);
      group.add(light);

      this.scene.add(group);
      this._staticMeshes.push(group);
    }
  }

  dispose() {
    for (const m of this.instancedMeshes) {
      m.geometry.dispose();
      if (m.material.map) m.material.map.dispose();
      m.material.dispose();
      this.scene.remove(m);
    }
    this.instancedMeshes = [];

    for (const g of this._staticMeshes) {
      g.traverse((child) => {
        if (child.isMesh) {
          child.geometry.dispose();
          if (child.material.map) child.material.map.dispose();
          child.material.dispose();
        }
      });
      this.scene.remove(g);
    }
    this._staticMeshes = [];
  }
}
