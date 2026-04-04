#version 330 core

out vec4 FragColor;

uniform float uAlpha;
uniform vec2 uResolution;

void main() {
    vec2 uv = gl_FragCoord.xy / uResolution;

    // Panel edges: left slides from 0 toward 0.5, right slides from 1 toward 0.5
    float leftEdge  = uAlpha * 0.5;
    float rightEdge = 1.0 - uAlpha * 0.5;

    // Outside both panels — transparent
    if (uv.x > leftEdge && uv.x < rightEdge) {
        discard;
    }

    // Shadow gradient: darker at screen edge, lighter toward center seam
    float gradient;
    if (uv.x <= leftEdge) {
        gradient = uv.x / max(leftEdge, 0.001);
    } else {
        gradient = (1.0 - uv.x) / max(1.0 - rightEdge, 0.001);
    }
    gradient = clamp(gradient, 0.0, 1.0);

    // Base panel color: near-black with subtle gradient toward seam
    float brightness = gradient * 0.04;

    // Light seam: thin warm-tinted glow at the door crack edge
    float distToSeam;
    if (uv.x <= leftEdge) {
        distToSeam = leftEdge - uv.x;
    } else {
        distToSeam = uv.x - rightEdge;
    }

    // Seam visible only when panels are partially closed (not at extremes)
    float seamVisibility = smoothstep(0.0, 0.1, uAlpha) * smoothstep(1.0, 0.85, uAlpha);
    float seamWidth = 0.008;
    float seam = exp(-distToSeam / seamWidth) * seamVisibility;

    // Warm light seam color (amber/orange tint)
    vec3 seamColor = vec3(1.0, 0.75, 0.4) * seam * 0.6;

    vec3 color = vec3(brightness) + seamColor;

    FragColor = vec4(color, 1.0);
}
