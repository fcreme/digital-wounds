#version 330 core

in vec3 vWorldPos;
in vec3 vNormal;
in vec2 vTexCoord;
in vec4 vFragPosLightSpace;

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

// Interaction highlight (0 = none, 1 = full glow)
uniform float uHighlight;

// Shadows
uniform sampler2D uShadowMap;
uniform int uUseShadows;

float calculateShadow(vec4 fragPosLightSpace) {
    // Perspective divide
    vec3 projCoords = fragPosLightSpace.xyz / fragPosLightSpace.w;
    projCoords = projCoords * 0.5 + 0.5;

    // Fragment outside shadow map — no shadow
    if (projCoords.z > 1.0)
        return 0.0;

    float currentDepth = projCoords.z;

    // Bias based on surface angle to light
    vec3 normal = normalize(vNormal);
    vec3 lightDir = normalize(-uLightDir);
    float bias = max(0.005 * (1.0 - dot(normal, lightDir)), 0.001);

    // PCF 3x3
    float shadow = 0.0;
    vec2 texelSize = 1.0 / textureSize(uShadowMap, 0);
    for (int x = -1; x <= 1; x++) {
        for (int y = -1; y <= 1; y++) {
            float pcfDepth = texture(uShadowMap, projCoords.xy + vec2(x, y) * texelSize).r;
            shadow += currentDepth - bias > pcfDepth ? 1.0 : 0.0;
        }
    }
    shadow /= 9.0;

    // 70% shadow intensity (not full black)
    return shadow * 0.7;
}

void main() {
    vec3 normal = normalize(vNormal);
    if (!gl_FrontFacing) normal = -normal; // flip normal for back-faces (interior walls)
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

    // Shadow attenuation on directional light
    float shadow = 0.0;
    if (uUseShadows != 0) {
        shadow = calculateShadow(vFragPosLightSpace);
    }

    vec3 result = uAmbient * baseColor + (1.0 - shadow) * diff * uLightColor * baseColor;

    // Point light contributions (not affected by directional shadow map)
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

    // Interaction highlight: emissive rim glow
    if (uHighlight > 0.0) {
        // Fresnel-based rim light
        vec3 viewDir = normalize(-vWorldPos); // approximate view dir
        float rim = 1.0 - max(dot(normal, viewDir), 0.0);
        rim = pow(rim, 2.0);
        vec3 glowColor = vec3(0.9, 0.7, 0.3); // warm gold glow
        result += glowColor * rim * uHighlight * 1.5;
        // Subtle overall emissive boost
        result += baseColor * uHighlight * 0.15;
    }

    FragColor = vec4(result, 1.0);
}
