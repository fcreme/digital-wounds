import * as THREE from 'three';
import { randomRange } from '../utils/math.js';
import { createFenceTexture } from '../utils/ProceduralTextures.js';
import PropBase from './PropBase.js';

export default class FencePosts extends PropBase {
  build(pathCurve, treeColliders) {
    const geo = new THREE.CylinderGeometry(0.04, 0.07, 1.2, 7);
    geo.translate(0, 0.6, 0);
    const { map: fenceMap, normalMap: fenceNormal } = createFenceTexture();
    const mat = new THREE.MeshStandardMaterial({
      map: fenceMap,
      normalMap: fenceNormal,
      normalScale: new THREE.Vector2(0.8, 0.8),
      color: 0x6a5530,
      roughness: 0.9,
      metalness: 0,
    });

    this.placeInstanced(geo, mat, 30, pathCurve, treeColliders, {
      name: 'pathProps-fencePosts',
      tRange: [0.05, 0.95],
      distRange: [2, 4],
      maxAttemptsMul: 3,
      rotationFn: (d) => d.rotation.set(
        randomRange(-0.12, 0.12),
        Math.random() * Math.PI * 2,
        randomRange(-0.12, 0.12)
      ),
      scaleFn: (d) => {
        const s = randomRange(0.8, 1.3);
        d.scale.set(s, s * randomRange(0.7, 1.2), s);
      },
    });
  }
}
