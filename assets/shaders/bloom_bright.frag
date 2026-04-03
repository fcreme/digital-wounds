#version 330 core

in vec2 vTexCoord;
out vec4 FragColor;

uniform sampler2D uScreen;
uniform float uThreshold;

void main() {
    vec3 color = texture(uScreen, vTexCoord).rgb;
    float brightness = dot(color, vec3(0.2126, 0.7152, 0.0722));

    if (brightness > uThreshold) {
        FragColor = vec4(color, 1.0);
    } else {
        FragColor = vec4(0.0, 0.0, 0.0, 1.0);
    }
}
