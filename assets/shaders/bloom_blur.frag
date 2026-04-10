#version 330 core

in vec2 vTexCoord;
out vec4 FragColor;

uniform sampler2D uImage;
uniform bool uHorizontal;

// 13-tap Gaussian weights (7 taps each side + center)
const float weight[7] = float[](0.1981, 0.1753, 0.1210, 0.0650, 0.0272, 0.0089, 0.0022);

void main() {
    vec2 texelSize = 1.0 / textureSize(uImage, 0);
    vec3 result = texture(uImage, vTexCoord).rgb * weight[0];

    if (uHorizontal) {
        for (int i = 1; i < 7; ++i) {
            result += texture(uImage, vTexCoord + vec2(texelSize.x * i, 0.0)).rgb * weight[i];
            result += texture(uImage, vTexCoord - vec2(texelSize.x * i, 0.0)).rgb * weight[i];
        }
    } else {
        for (int i = 1; i < 7; ++i) {
            result += texture(uImage, vTexCoord + vec2(0.0, texelSize.y * i)).rgb * weight[i];
            result += texture(uImage, vTexCoord - vec2(0.0, texelSize.y * i)).rgb * weight[i];
        }
    }

    FragColor = vec4(result, 1.0);
}
