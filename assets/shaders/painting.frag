#version 330 core

in vec2 vUV;
in vec3 vWorldPos;
out vec4 FragColor;

uniform sampler2D uArt;       // sRGB-flagged, so sampling returns linear
uniform vec2 uSize;           // painting width/height in world units
uniform float uImageAspect;   // artwork width / height
uniform float uBrightness;
uniform float uHighlight;
uniform vec3 uNormal;            // this painting's facing

// Mood light: a multiplier on baked light. Keep identical in mesh.frag and painting.frag;
// MAX_SPOTS must match MAX_MOOD_SPOTS in src/world/MoodLighting.h.
#define MAX_SPOTS 32
uniform int uMoodEnabled;
uniform float uMoodAmbient;
uniform vec3 uMoodCeiling;       // start height, end height, level at the ceiling
uniform int uNumSpots;
uniform vec3 uSpotPos[MAX_SPOTS];
uniform vec3 uSpotDir[MAX_SPOTS];
uniform vec3 uSpotColor;         // colour times intensity
uniform vec3 uSpotShape;         // cos(outer), cos(inner), range

vec3 moodLight(vec3 p, vec3 n) {
    float base = uMoodAmbient * mix(1.0, uMoodCeiling.z, smoothstep(uMoodCeiling.x, uMoodCeiling.y, p.y));
    vec3 light = vec3(base);
    for (int i = 0; i < uNumSpots && i < MAX_SPOTS; i++) {
        vec3 d = p - uSpotPos[i];
        float dist = length(d);
        vec3 dir = d / max(dist, 1e-4);
        float cone = smoothstep(uSpotShape.x, uSpotShape.y, dot(dir, uSpotDir[i]));
        float r = dist / uSpotShape.z;
        float atten = 1.0 / (1.0 + r * r);
        // Two-sided surfaces: soften the facing term rather than trusting the normal's sign.
        float facing = 0.35 + 0.65 * abs(dot(n, dir));
        light += uSpotColor * cone * atten * facing;
    }
    return light;
}

// Paper mat #E6DCC8 in linear space, matching how the sRGB art is sampled.
const vec3 MAT = pow(vec3(230.0, 220.0, 200.0) / 255.0, vec3(2.2));
const vec3 FRAME = vec3(0.012, 0.009, 0.008);
const vec3 GLOW = vec3(1.0, 0.62, 0.25);

void main() {
    vec2 p = vUV * uSize;                        // world units from the top-left
    float frame = 0.06 * min(uSize.x, uSize.y);
    vec2 inner = uSize - 2.0 * frame;            // mat area
    vec2 q = p - vec2(frame);                    // position inside the mat area

    vec3 color;
    if (q.x < 0.0 || q.y < 0.0 || q.x > inner.x || q.y > inner.y) {
        color = FRAME + GLOW * uHighlight * 0.9;
    } else {
        // Fit the artwork inside the mat without stretching, centred.
        vec2 art = inner;
        if (inner.x / inner.y > uImageAspect) art.x = inner.y * uImageAspect;
        else art.y = inner.x / uImageAspect;
        vec2 a = (q - 0.5 * (inner - art)) / art;
        if (a.x < 0.0 || a.y < 0.0 || a.x > 1.0 || a.y > 1.0) color = MAT;
        else color = texture(uArt, a).rgb;
        color *= uBrightness;
        if (uMoodEnabled != 0) color *= moodLight(vWorldPos, uNormal);
    }
    FragColor = vec4(color, 1.0);
}
