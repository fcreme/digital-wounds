import * as THREE from 'three';
import { randomRange, displaceGeometryVertices } from '../utils/math.js';
import { createRockTexture } from '../utils/ProceduralTextures.js';
import PropBase from './PropBase.js';

export default class StoneMarkers extends PropBase {
  build(pathCurve, treeColliders) {
    const geo = new THREE.IcosahedronGeometry(0.22, 1);
    displaceGeometryVertices(geo, 0.03);
    geo.scale(0.7, 1, 0.6);
    geo.translate(0, 0.2, 0);
    const { map: rockMap, normalMap: rockNormal } = createRockTexture();
    const mat = new THREE.MeshStandardMaterial({
      map: rockMap,
      normalMap: rockNormal,
      normalScale: new THREE.Vector2(1.5, 1.5),
      color: 0x7a7860,
      roughness: 0.92,
      metalness: 0,
    });

    this.placeInstanced(geo, mat, 15, pathCurve, treeColliders, {
      name: 'pathProps-stoneMarkers',
      tRange: [0.08, 0.92],
      distRange: [1.8, 3.5],
      maxAttemptsMul: 5,
      rotationFn: (d) => d.rotation.set(
        randomRange(-0.08, 0.08),
        Math.random() * Math.PI * 2,
        randomRange(-0.08, 0.08)
      ),
      scaleFn: (d) => {
        d.scale.set(
          randomRange(0.6, 1.4),
          randomRange(0.5, 1.5),
          randomRange(0.6, 1.4)
        );
      },
    });
  }
}
