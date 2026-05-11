#version 330 core

in vec2 vTexCoord;
out float FragColor;

uniform sampler2D uSSAO;

void main() {
    vec2 texelSize = 1.0 / textureSize(uSSAO, 0);
    float result = 0.0;

    // 5x5 box blur (centered)
    for (int x = -2; x <= 2; x++) {
        for (int y = -2; y <= 2; y++) {
            vec2 offset = vec2(float(x), float(y)) * texelSize;
            result += texture(uSSAO, vTexCoord + offset).r;
        }
    }

    FragColor = result / 25.0;
}
