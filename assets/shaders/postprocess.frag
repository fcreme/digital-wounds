#version 330 core

in vec2 vTexCoord;
out vec4 FragColor;

uniform sampler2D uScreen;
uniform float uTime;
uniform vec2 uResolution;

// Film grain noise
float rand(vec2 co) {
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {
    vec3 color = texture(uScreen, vTexCoord).rgb;

    // --- Vignette ---
    vec2 uv = vTexCoord;
    float dist = distance(uv, vec2(0.5));
    float vignette = smoothstep(0.7, 0.4, dist);
    color *= mix(0.3, 1.0, vignette);

    // --- Film grain ---
    float grain = rand(vTexCoord * uResolution + vec2(uTime * 100.0)) * 0.08;
    color += grain - 0.04;

    // --- Subtle color grading (push toward cold tones) ---
    color.r *= 0.95;
    color.b *= 1.05;

    // --- Slight contrast boost ---
    color = (color - 0.5) * 1.1 + 0.5;

    FragColor = vec4(clamp(color, 0.0, 1.0), 1.0);
}
