import FencePosts from './FencePosts.js';
import StoneMarkers from './StoneMarkers.js';
import FallenLogs from './FallenLogs.js';
import GateArch from './GateArch.js';
import Gravestones from './Gravestones.js';
import WoodenCrosses from './WoodenCrosses.js';
import RuinedWalls from './RuinedWalls.js';
import StonePillars from './StonePillars.js';
import IronLanterns from './IronLanterns.js';

export default class PropsManager {
  constructor(scene) {
    this.scene = scene;
    this.props = [
      new FencePosts(scene),
      new StoneMarkers(scene),
      new FallenLogs(scene),
      new GateArch(scene),
      new Gravestones(scene),
      new WoodenCrosses(scene),
      new RuinedWalls(scene),
      new StonePillars(scene),
      new IronLanterns(scene),
    ];
  }

  build(pathCurve, treeColliders) {
    for (const prop of this.props) {
      prop.build(pathCurve, treeColliders);
    }
  }

  dispose() {
    for (const prop of this.props) {
      prop.dispose();
    }
  }
}
