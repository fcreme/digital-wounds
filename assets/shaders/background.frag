#version 330 core

in vec2 vTexCoord;
out vec4 FragColor;

uniform sampler2D uBackground;

void main() {
    vec4 texColor = texture(uBackground, vTexCoord);
    texColor.rgb = pow(texColor.rgb, vec3(2.2));
    FragColor = texColor;
}
