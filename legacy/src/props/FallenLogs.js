import * as THREE from 'three';
import { randomRange, displaceGeometryVertices } from '../utils/math.js';
import { createDeadWoodTexture } from '../utils/ProceduralTextures.js';
import PropBase from './PropBase.js';

export default class FallenLogs extends PropBase {
  build(pathCurve, treeColliders) {
    const geo = new THREE.CylinderGeometry(0.12, 0.15, 2.5, 8, 3);
    displaceGeometryVertices(geo, 0.02);
    geo.rotateZ(Math.PI / 2);
    geo.translate(0, 0.12, 0);
    const { map: woodMap, normalMap: woodNormal } = createDeadWoodTexture();
    const mat = new THREE.MeshStandardMaterial({
      map: woodMap,
      normalMap: woodNormal,
      normalScale: new THREE.Vector2(1.0, 1.0),
      color: 0x5a4a28,
      roughness: 0.9,
      metalness: 0,
    });

    this.placeInstanced(geo, mat, 12, pathCurve, treeColliders, {
      name: 'pathProps-fallenLogs',
      tRange: [0.1, 0.9],
      distRange: [2.5, 5],
      maxAttemptsMul: 6,
      rotationFn: (d) => d.rotation.set(
        randomRange(-0.1, 0.1),
        Math.random() * Math.PI * 2,
        randomRange(-0.05, 0.05)
      ),
      scaleFn: (d) => {
        const s = randomRange(0.7, 1.3);
        d.scale.set(s, s * randomRange(0.8, 1.2), s);
      },
    });
  }
}
