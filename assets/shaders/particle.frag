#version 330 core

in vec4 vColor;
flat in int vType;
in float vViewDepth;

uniform sampler2D uDepthTex;
uniform float uNearPlane;
uniform float uFarPlane;
uniform vec2 uResolution;
uniform int uHasDepth;

out vec4 FragColor;

float linearizeDepth(float d) {
    float z = d * 2.0 - 1.0; // NDC
    return (2.0 * uNearPlane * uFarPlane) / (uFarPlane + uNearPlane - z * (uFarPlane - uNearPlane));
}

void main() {
    vec2 center = gl_PointCoord - vec2(0.5);
    float dist = length(center);
    float alpha = 0.0;

    // Per-type procedural shapes
    if (vType == 0) {
        // Dust: soft circle
        alpha = smoothstep(0.5, 0.2, dist) * vColor.a;
    }
    else if (vType == 1) {
        // Fog: very diffuse falloff
        alpha = smoothstep(0.5, 0.0, dist) * vColor.a;
        alpha *= 0.7 + 0.3 * smoothstep(0.5, 0.1, dist);
    }
    else if (vType == 2) {
        // Fireflies: bright core + outer glow halo
        float core = smoothstep(0.15, 0.0, dist);
        float halo = smoothstep(0.5, 0.1, dist) * 0.4;
        alpha = (core + halo) * vColor.a;
    }
    else if (vType == 3) {
        // Fire: vertically stretched, brighter at bottom
        vec2 uv = gl_PointCoord;
        float yFade = smoothstep(0.0, 0.7, uv.y); // brighter at bottom (y=0)
        float xDist = abs(uv.x - 0.5);
        float shape = smoothstep(0.5, 0.1, xDist) * smoothstep(1.0, 0.2, uv.y);
        alpha = shape * yFade * vColor.a;
    }

    if (alpha < 0.005) discard;

    // Soft particles: fade when near scene geometry
    if (uHasDepth == 1) {
        vec2 screenUV = gl_FragCoord.xy / uResolution;
        float sceneDepth = linearizeDepth(texture(uDepthTex, screenUV).r);
        float particleDepth = vViewDepth;
        float depthDiff = sceneDepth - particleDepth;
        float softFade = smoothstep(0.0, 0.5, depthDiff);
        alpha *= softFade;
    }

    if (alpha < 0.005) discard;

    FragColor = vec4(vColor.rgb, alpha);
}
