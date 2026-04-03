#version 330 core

in vec2 vTexCoord;
out vec4 FragColor;

uniform sampler2D uImage;
uniform bool uHorizontal;

// 9-tap Gaussian weights
const float weight[5] = float[](0.2270270270, 0.1945945946, 0.1216216216, 0.0540540541, 0.0162162162);

void main() {
    vec2 texelSize = 1.0 / textureSize(uImage, 0);
    vec3 result = texture(uImage, vTexCoord).rgb * weight[0];

    if (uHorizontal) {
        for (int i = 1; i < 5; ++i) {
            result += texture(uImage, vTexCoord + vec2(texelSize.x * i, 0.0)).rgb * weight[i];
            result += texture(uImage, vTexCoord - vec2(texelSize.x * i, 0.0)).rgb * weight[i];
        }
    } else {
        for (int i = 1; i < 5; ++i) {
            result += texture(uImage, vTexCoord + vec2(0.0, texelSize.y * i)).rgb * weight[i];
            result += texture(uImage, vTexCoord - vec2(0.0, texelSize.y * i)).rgb * weight[i];
        }
    }

    FragColor = vec4(result, 1.0);
}
