import * as THREE from 'three';
import { randomRange } from '../utils/math.js';
import { patchMaterial } from '../fx/PSXEffect.js';
import { createIronTexture } from '../utils/ProceduralTextures.js';
import PropBase from './PropBase.js';

export default class IronLanterns extends PropBase {
  build(pathCurve) {
    const { map: ironMap, normalMap: ironNormal } = createIronTexture();

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
        map: ironMap,
        normalMap: ironNormal,
        normalScale: new THREE.Vector2(0.8, 0.8),
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
      this.staticMeshes.push(group);
    }
  }
}
