#version 330 core

in vec2 vTexCoord;
out vec4 FragColor;

uniform sampler2D uScreen;
uniform float uThreshold;

void main() {
    vec3 color = texture(uScreen, vTexCoord).rgb;
    float brightness = dot(color, vec3(0.2126, 0.7152, 0.0722));

    // Smooth threshold: gradual ramp instead of hard cutoff
    float contribution = smoothstep(uThreshold - 0.1, uThreshold + 0.1, brightness);
    FragColor = vec4(color * contribution, 1.0);
}
