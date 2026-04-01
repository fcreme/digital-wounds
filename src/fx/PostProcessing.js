import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { PSXColorShader, ScanlineShader, DesaturationShader } from './PSXEffect.js';

const VignetteShader = {
  uniforms: {
    tDiffuse: { value: null },
    offset: { value: 1.2 },
    darkness: { value: 1.5 },
  },
  vertexShader: /* glsl */ `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: /* glsl */ `
    uniform sampler2D tDiffuse;
    uniform float offset;
    uniform float darkness;
    varying vec2 vUv;
    void main() {
      vec4 texel = texture2D(tDiffuse, vUv);
      vec2 uv = (vUv - vec2(0.5)) * vec2(offset);
      texel.rgb *= clamp(1.0 - dot(uv, uv), 0.0, 1.0) * darkness + (1.0 - darkness);
      gl_FragColor = texel;
    }
  `,
};

const FilmShader = {
  uniforms: {
    tDiffuse: { value: null },
    time: { value: 0.0 },
    intensity: { value: 0.12 },
    grayscale: { value: false },
  },
  vertexShader: /* glsl */ `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: /* glsl */ `
    uniform sampler2D tDiffuse;
    uniform float time;
    uniform float intensity;
    uniform bool grayscale;
    varying vec2 vUv;
    float rand(vec2 co) {
      return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
    }
    void main() {
      vec4 texel = texture2D(tDiffuse, vUv);
      float noise = rand(vUv + vec2(time)) * intensity;
      texel.rgb += vec3(noise) - vec3(intensity * 0.5);
      gl_FragColor = texel;
    }
  `,
};

// Bloodborne cold color grade — cold blue shadows, muted highlights
const ColdGradeShader = {
  uniforms: {
    tDiffuse: { value: null },
  },
  vertexShader: /* glsl */ `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: /* glsl */ `
    uniform sampler2D tDiffuse;
    varying vec2 vUv;
    void main() {
      vec4 color = texture2D(tDiffuse, vUv);
      float lum = dot(color.rgb, vec3(0.299, 0.587, 0.114));

      // Cold shadows (push darks toward blue)
      vec3 coldShadow = color.rgb + vec3(-0.06, -0.02, 0.10) * (1.0 - lum);
      // Muted highlights (slightly warm to preserve lantern contrast)
      vec3 mutedHighlight = coldShadow + vec3(0.03, 0.02, -0.02) * lum;

      gl_FragColor = vec4(mutedHighlight, color.a);
    }
  `,
};

export default class PostProcessing {
  constructor(renderer, scene, camera) {
    this._renderer = renderer;
    const size = renderer.getSize(new THREE.Vector2());

    this._composer = new EffectComposer(renderer);

    // 1. Render
    this._composer.addPass(new RenderPass(scene, camera));

    // 2. PSX Color (posterize + dither)
    this._psxColor = new ShaderPass(PSXColorShader);
    this._psxColor.uniforms.resolution.value.set(size.x, size.y);
    this._composer.addPass(this._psxColor);

    // 3. Bloom — stronger, wider glow for moonlit atmosphere
    this._bloom = new UnrealBloomPass(
      new THREE.Vector2(size.x, size.y),
      0.70,  // strength
      1.0,   // radius
      0.30   // threshold
    );
    this._composer.addPass(this._bloom);

    // 4. Cold color grade — Bloodborne cold shadow / muted highlight split
    this._coldGrade = new ShaderPass(ColdGradeShader);
    this._composer.addPass(this._coldGrade);

    // 5. Desaturation — more muted for gothic atmosphere
    this._desat = new ShaderPass(DesaturationShader);
    this._desat.uniforms.amount.value = 0.18;
    this._composer.addPass(this._desat);

    // 6. Scanlines
    this._scanlines = new ShaderPass(ScanlineShader);
    this._scanlines.uniforms.scanlineCount.value = size.y;
    this._composer.addPass(this._scanlines);

    // 7. Vignette — darker edges for gothic framing
    this._vignette = new ShaderPass(VignetteShader);
    this._vignette.uniforms.offset.value = 0.9;
    this._vignette.uniforms.darkness.value = 0.72;
    this._composer.addPass(this._vignette);

    // 8. Film grain — stronger for gritty atmosphere
    this._film = new ShaderPass(FilmShader);
    this._film.uniforms.intensity.value = 0.025;
    this._composer.addPass(this._film);

    // 9. Output
    this._composer.addPass(new OutputPass());
  }

  update(elapsed) {
    this._film.uniforms.time.value = elapsed;
  }

  render() {
    this._composer.render();
  }

  resize(w, h) {
    this._composer.setSize(w, h);
    this._psxColor.uniforms.resolution.value.set(w, h);
    this._scanlines.uniforms.scanlineCount.value = h;
  }

  dispose() {
    this._composer.passes.forEach(pass => {
      if (pass.dispose) pass.dispose();
    });
  }
}
