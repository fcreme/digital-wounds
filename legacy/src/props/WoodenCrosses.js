import * as THREE from 'three';
import { randomRange } from '../utils/math.js';
import { createFenceTexture } from '../utils/ProceduralTextures.js';
import PropBase from './PropBase.js';

export default class WoodenCrosses extends PropBase {
  build(pathCurve, treeColliders) {
    const vertical = new THREE.BoxGeometry(0.06, 0.9, 0.06);
    vertical.translate(0, 0.45, 0);
    const horizontal = new THREE.BoxGeometry(0.5, 0.06, 0.06);
    horizontal.translate(0, 0.65, 0);
    const crossGeo = this.mergeGeometries([vertical, horizontal]);

    const { map: fenceMap, normalMap: fenceNormal } = createFenceTexture();
    const mat = new THREE.MeshStandardMaterial({
      map: fenceMap,
      normalMap: fenceNormal,
      normalScale: new THREE.Vector2(0.8, 0.8),
      color: 0x4a3a25,
      roughness: 0.9,
      metalness: 0,
    });

    this.placeInstanced(crossGeo, mat, 10, pathCurve, treeColliders, {
      name: 'pathProps-woodenCrosses',
      tRange: [0.1, 0.9],
      distRange: [3, 7],
      maxAttemptsMul: 5,
      rotationFn: (d) => d.rotation.set(0, Math.random() * Math.PI * 2, randomRange(-0.15, 0.15)),
      scaleFn: (d) => {
        const s = randomRange(0.8, 1.2);
        d.scale.set(s, s, s);
      },
    });
  }
}
