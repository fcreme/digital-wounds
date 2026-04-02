import * as THREE from 'three';
import { patchMaterial } from '../fx/PSXEffect.js';
import { createFenceTexture, createDeadWoodTexture } from '../utils/ProceduralTextures.js';
import PropBase from './PropBase.js';

export default class GateArch extends PropBase {
  build(pathCurve) {
    const group = new THREE.Group();
    group.name = 'pathProps-gateArch';

    const { map: fenceMap, normalMap: fenceNormal } = createFenceTexture();
    const postMat = new THREE.MeshStandardMaterial({
      map: fenceMap,
      normalMap: fenceNormal,
      normalScale: new THREE.Vector2(0.8, 0.8),
      color: 0x6a5530,
      roughness: 0.9,
      metalness: 0,
    });
    const { map: woodMap, normalMap: woodNormal } = createDeadWoodTexture();
    const beamMat = new THREE.MeshStandardMaterial({
      map: woodMap,
      normalMap: woodNormal,
      normalScale: new THREE.Vector2(1.0, 1.0),
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
    this.staticMeshes.push(group);
  }
}
