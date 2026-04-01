import * as THREE from 'three';
import TerrainBuilder from './TerrainBuilder.js';
import PathBuilder from './PathBuilder.js';
import ForestGenerator from './ForestGenerator.js';
import SkyDome from './SkyDome.js';
import GroundScatter from './GroundScatter.js';
import HotelHallway from './HotelHallway.js';
import PathProps from './PathProps.js';
import FlickerLight from '../fx/FlickerLight.js';
import EventBus from '../core/EventBus.js';

export default class WorldManager {
  constructor(scene) {
    this.scene = scene;
    this.worldGroup = new THREE.Group();
    this.worldGroup.name = 'world';
    this.scene.add(this.worldGroup);

    this.terrain = new TerrainBuilder(this.worldGroup);
    this.path = new PathBuilder(this.worldGroup);
    this.forest = new ForestGenerator(this.worldGroup);
    this.skyDome = new SkyDome();
    this.groundScatter = new GroundScatter(this.worldGroup);
    this.hotelHallway = new HotelHallway(this.worldGroup);
    this.pathProps = new PathProps(this.worldGroup);
    this._flickerLights = [];

    // Lighting
    this._setupLighting();
  }

  _setupLighting() {
    // Ambient — cold dark grey
    this.ambient = new THREE.AmbientLight(0x1a1e28, 0.35);
    this.scene.add(this.ambient);

    // Hemisphere — cold sky, deep dark ground
    this.hemiLight = new THREE.HemisphereLight(0x4a5570, 0x0a0c14, 0.6);
    this.scene.add(this.hemiLight);

    // Moonlight — silver-white, stronger
    this.moonlight = new THREE.DirectionalLight(0x8899bb, 1.8);
    this.moonlight.position.set(-30, 40, -20);
    this.moonlight.castShadow = true;
    this.moonlight.shadow.mapSize.width = 2048;
    this.moonlight.shadow.mapSize.height = 2048;
    this.moonlight.shadow.camera.near = 0.5;
    this.moonlight.shadow.camera.far = 100;
    this.moonlight.shadow.camera.left = -50;
    this.moonlight.shadow.camera.right = 50;
    this.moonlight.shadow.camera.top = 50;
    this.moonlight.shadow.camera.bottom = -50;
    this.moonlight.shadow.bias = -0.001;
    this.scene.add(this.moonlight);
    this.scene.add(this.moonlight.target);

    // Fill light — nearly eliminated
    this.fillLight = new THREE.DirectionalLight(0x3a3a50, 0.1);
    this.fillLight.position.set(20, 5, 30);
    this.scene.add(this.fillLight);
  }

  _setupPathLights(pathCurve) {
    // 6 muted FlickerLights — fewer, more isolated warm pools
    const lightCount = 6;
    for (let i = 0; i < lightCount; i++) {
      const t = (i + 1) / (lightCount + 1);
      const point = pathCurve.getPointAt(t);
      const tangent = pathCurve.getTangentAt(t);
      const normal = new THREE.Vector3().crossVectors(tangent, new THREE.Vector3(0, 1, 0)).normalize();

      // Offset slightly to one side and elevate
      const side = i % 2 === 0 ? 1 : -1;
      const pos = new THREE.Vector3(
        point.x + normal.x * side * 2.0,
        1.8,
        point.z + normal.z * side * 2.0
      );

      const fl = new FlickerLight(this.scene, pos, 0xcc8844, 2.0, 18);
      this._flickerLights.push(fl);
    }
  }

  async build() {
    const skyGroup = this.skyDome.build();
    this.scene.add(skyGroup);

    this.terrain.build();
    const { curve } = this.path.build();
    const colliders = this.forest.build(curve);
    this.groundScatter.build(curve, colliders);
    this.pathProps.build(curve, colliders);
    this._setupPathLights(curve);

    // Load hotel hallway tiles along the path
    await this.hotelHallway.build(curve);

    return { pathCurve: curve, colliders };
  }

  update(delta, elapsed) {
    for (const fl of this._flickerLights) {
      fl.update(elapsed);
    }
  }

  get pathCurve() {
    return this.path.curve;
  }

  dispose() {
    this.skyDome.dispose();
    this.scene.remove(this.skyDome.group);
    this.terrain.dispose();
    this.path.dispose();
    this.forest.dispose();
    this.groundScatter.dispose();
    this.pathProps.dispose();
    this.hotelHallway.dispose();
    for (const fl of this._flickerLights) {
      fl.dispose(this.scene);
    }
    this._flickerLights = [];
    this.scene.remove(this.ambient);
    this.scene.remove(this.hemiLight);
    this.scene.remove(this.moonlight);
    this.scene.remove(this.fillLight);
    this.scene.remove(this.worldGroup);
  }
}
