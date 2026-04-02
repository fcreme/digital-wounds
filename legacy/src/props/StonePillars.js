import * as THREE from 'three';
import { randomRange, displaceGeometryVertices } from '../utils/math.js';
import { createGravestoneTexture } from '../utils/ProceduralTextures.js';
import PropBase from './PropBase.js';

export default class StonePillars extends PropBase {
  build(pathCurve, treeColliders) {
    const cylinder = new THREE.CylinderGeometry(0.18, 0.22, 2.2, 8);
    cylinder.translate(0, 1.1, 0);
    const cap = new THREE.BoxGeometry(0.55, 0.15, 0.55);
    cap.translate(0, 2.28, 0);
    const pillarGeo = this.mergeGeometries([cylinder, cap]);
    displaceGeometryVertices(pillarGeo, 0.02);

    const { map: stoneMap, normalMap: stoneNormal } = createGravestoneTexture();
    const mat = new THREE.MeshStandardMaterial({
      map: stoneMap,
      normalMap: stoneNormal,
      normalScale: new THREE.Vector2(1.2, 1.2),
      color: 0x5a5a55,
      roughness: 0.9,
      metalness: 0,
    });

    this.placeInstanced(pillarGeo, mat, 6, pathCurve, treeColliders, {
      name: 'pathProps-stonePillars',
      tRange: [0.1, 0.9],
      distRange: [3, 7],
      maxAttemptsMul: 6,
      rotationFn: (d) => d.rotation.set(
        randomRange(-0.03, 0.03),
        Math.random() * Math.PI * 2,
        randomRange(-0.03, 0.03)
      ),
      scaleFn: (d) => {
        const s = randomRange(0.8, 1.1);
        d.scale.set(s, s, s);
      },
    });
  }
}
