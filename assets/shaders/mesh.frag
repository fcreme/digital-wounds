#version 330 core

in vec3 vWorldPos;
in vec3 vNormal;
in vec2 vTexCoord;

out vec4 FragColor;

uniform sampler2D uDiffuse;
uniform bool uHasTexture;

// Directional light
uniform vec3 uLightDir;
uniform vec3 uLightColor;
uniform vec3 uAmbient;

// Point lights (up to 4)
#define MAX_POINT_LIGHTS 4
uniform int uNumPointLights;
uniform vec3 uPointLightPos[MAX_POINT_LIGHTS];
uniform vec3 uPointLightColor[MAX_POINT_LIGHTS];
uniform float uPointLightRadius[MAX_POINT_LIGHTS];

// Material color (used when no texture)
uniform vec3 uMaterialColor;

void main() {
    vec3 normal = normalize(vNormal);
    vec3 lightDir = normalize(-uLightDir);

    // Base color
    vec3 baseColor;
    if (uHasTexture) {
        baseColor = texture(uDiffuse, vTexCoord).rgb;
    } else {
        baseColor = uMaterialColor;
    }

    // Directional light contribution
    float diff = max(dot(normal, lightDir), 0.0);
    vec3 result = uAmbient * baseColor + diff * uLightColor * baseColor;

    // Point light contributions
    for (int i = 0; i < uNumPointLights && i < MAX_POINT_LIGHTS; i++) {
        vec3 toLight = uPointLightPos[i] - vWorldPos;
        float dist = length(toLight);
        vec3 lightVec = toLight / dist;

        // Attenuation (smooth falloff)
        float atten = clamp(1.0 - dist / uPointLightRadius[i], 0.0, 1.0);
        atten *= atten; // quadratic falloff

        float ndotl = max(dot(normal, lightVec), 0.0);
        result += ndotl * atten * uPointLightColor[i] * baseColor;
    }

    FragColor = vec4(result, 1.0);
}
