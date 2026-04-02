#version 330 core

uniform sampler2D uFont;
uniform vec4 uColor;

in vec2 vUV;
out vec4 FragColor;

void main() {
    float alpha = texture(uFont, vUV).a;
    if (alpha < 0.5) discard;
    FragColor = vec4(uColor.rgb, uColor.a * alpha);
}
