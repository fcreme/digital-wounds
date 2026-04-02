import * as THREE from 'three';
import { randomRange } from '../utils/math.js';
import { patchMaterial } from '../fx/PSXEffect.js';

export default class PropBase {
  constructor(scene) {
    this.scene = scene;
    this.instancedMeshes = [];
    this.staticMeshes = [];
  }

  isBlockedByTree(x, z, treeColliders, minDist = 1.2) {
    for (const tree of treeColliders) {
      const dx = x - tree.x;
      const dz = z - tree.z;
      if (dx * dx + dz * dz < minDist * minDist) return true;
    }
    return false;
  }

  placeInstanced(geo, mat, count, pathCurve, treeColliders, opts = {}) {
    const {
      name = 'pathProps',
      tRange = [0.05, 0.95],
      distRange = [2, 4],
      maxAttemptsMul = 3,
      minTreeDist = 1.2,
      rotationFn = null,
      scaleFn = null,
    } = opts;

    patchMaterial(mat);

    const instanced = new THREE.InstancedMesh(geo, mat, count);
    instanced.castShadow = true;
    instanced.receiveShadow = true;
    instanced.name = name;

    const dummy = new THREE.Object3D();
    let placed = 0;

    for (let i = 0; i < count * maxAttemptsMul && placed < count; i++) {
      const t = randomRange(tRange[0], tRange[1]);
      const point = pathCurve.getPointAt(t);
      const tangent = pathCurve.getTangentAt(t);
      const normal = new THREE.Vector3().crossVectors(tangent, new THREE.Vector3(0, 1, 0)).normalize();

      const side = Math.random() < 0.5 ? 1 : -1;
      const dist = randomRange(distRange[0], distRange[1]);
      const x = point.x + normal.x * side * dist;
      const z = point.z + normal.z * side * dist;

      if (this.isBlockedByTree(x, z, treeColliders, minTreeDist)) continue;

      dummy.position.set(x, 0, z);

      if (rotationFn) {
        rotationFn(dummy);
      } else {
        dummy.rotation.set(
          randomRange(-0.1, 0.1),
          Math.random() * Math.PI * 2,
          randomRange(-0.1, 0.1)
        );
      }

      if (scaleFn) {
        scaleFn(dummy);
      } else {
        const s = randomRange(0.8, 1.2);
        dummy.scale.set(s, s, s);
      }

      dummy.updateMatrix();
      instanced.setMatrixAt(placed, dummy.matrix);
      placed++;
    }

    instanced.count = placed;
    instanced.instanceMatrix.needsUpdate = true;
    this.scene.add(instanced);
    this.instancedMeshes.push(instanced);
    return instanced;
  }

  mergeGeometries(geometries) {
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

  build(pathCurve, treeColliders) {
    throw new Error('Subclass must implement build()');
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

    for (const g of this.staticMeshes) {
      g.traverse((child) => {
        if (child.isMesh) {
          child.geometry.dispose();
          if (child.material.map) child.material.map.dispose();
          if (child.material.normalMap) child.material.normalMap.dispose();
          child.material.dispose();
        }
      });
      this.scene.remove(g);
    }
    this.staticMeshes = [];
  }
}
