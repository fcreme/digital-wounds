import * as THREE from 'three';
import { randomRange, displaceGeometryVertices } from '../utils/math.js';
import { createRockTexture } from '../utils/ProceduralTextures.js';
import PropBase from './PropBase.js';

export default class RuinedWalls extends PropBase {
  build(pathCurve, treeColliders) {
    const geo = new THREE.BoxGeometry(2.5, 1.8, 0.25, 4, 4, 1);
    displaceGeometryVertices(geo, 0.06);
    geo.translate(0, 0.9, 0);

    const { map: rockMap, normalMap: rockNormal } = createRockTexture();
    const mat = new THREE.MeshStandardMaterial({
      map: rockMap,
      normalMap: rockNormal,
      normalScale: new THREE.Vector2(1.5, 1.5),
      color: 0x585850,
      roughness: 0.95,
      metalness: 0,
    });

    this.placeInstanced(geo, mat, 8, pathCurve, treeColliders, {
      name: 'pathProps-ruinedWalls',
      tRange: [0.1, 0.9],
      distRange: [5, 9],
      maxAttemptsMul: 6,
      minTreeDist: 2.0,
      rotationFn: (d) => d.rotation.set(
        randomRange(-0.05, 0.05),
        Math.random() * Math.PI * 2,
        randomRange(-0.05, 0.05)
      ),
      scaleFn: (d) => {
        const s = randomRange(0.7, 1.2);
        d.scale.set(s, s * randomRange(0.6, 1.0), s);
      },
    });
  }
}
