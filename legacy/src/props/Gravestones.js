import * as THREE from 'three';
import { randomRange, displaceGeometryVertices } from '../utils/math.js';
import { createGravestoneTexture } from '../utils/ProceduralTextures.js';
import PropBase from './PropBase.js';

export default class Gravestones extends PropBase {
  build(pathCurve, treeColliders) {
    const geo = new THREE.BoxGeometry(0.35, 0.8, 0.08, 4, 4, 1);
    displaceGeometryVertices(geo, 0.015);
    geo.translate(0, 0.4, 0);

    const { map: stoneMap, normalMap: stoneNormal } = createGravestoneTexture();
    const mat = new THREE.MeshStandardMaterial({
      map: stoneMap,
      normalMap: stoneNormal,
      normalScale: new THREE.Vector2(1.2, 1.2),
      color: 0x606858,
      roughness: 0.92,
      metalness: 0,
    });

    this.placeInstanced(geo, mat, 20, pathCurve, treeColliders, {
      name: 'pathProps-gravestones',
      tRange: [0.1, 0.9],
      distRange: [3, 6],
      maxAttemptsMul: 5,
      rotationFn: (d) => d.rotation.set(
        randomRange(-0.06, 0.06),
        Math.random() * Math.PI * 2,
        randomRange(-0.1, 0.1)
      ),
      scaleFn: (d) => {
        const s = randomRange(0.8, 1.3);
        d.scale.set(s, s * randomRange(0.8, 1.4), s);
      },
    });
  }
}
