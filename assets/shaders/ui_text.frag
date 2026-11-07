#version 330 core

// TrueType glyphs: the atlas holds anti-aliased coverage in the red channel.
uniform sampler2D uFont;
uniform vec4 uColor;

in vec2 vUV;
out vec4 FragColor;

void main() {
    float coverage = texture(uFont, vUV).r;
    if (coverage <= 0.0) discard;
    FragColor = vec4(uColor.rgb, uColor.a * coverage);
}
