#version 330 core

uniform sampler2D uTexture;
uniform float uAlpha;

in vec2 vUV;
out vec4 FragColor;

void main() {
    vec4 tex = texture(uTexture, vUV);
    FragColor = vec4(tex.rgb, tex.a * uAlpha);
}
