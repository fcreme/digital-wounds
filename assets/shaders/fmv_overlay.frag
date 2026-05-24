#version 330 core

in vec2 vTexCoord;
out vec4 FragColor;

uniform sampler2D uTexture;
uniform float uTime;
uniform int uFrameCount;
uniform float uAlpha;
uniform vec2 uScrollSpeed;
uniform vec3 uTint;

void main() {
    vec2 uv = vTexCoord;

    // Sprite sheet frame selection (horizontal strip) with interpolation
    if (uFrameCount > 1) {
        float fw = 1.0 / float(uFrameCount);
        float frameF = mod(uTime, float(uFrameCount));
        int frame0 = int(floor(frameF));
        int frame1 = int(mod(float(frame0 + 1), float(uFrameCount)));
        float frac = frameF - floor(frameF);

        vec2 uv0 = vec2(uv.x * fw + float(frame0) * fw, uv.y);
        vec2 uv1 = vec2(uv.x * fw + float(frame1) * fw, uv.y);

        // UV scrolling for continuous drift effects
        uv0 += uScrollSpeed * uTime;
        uv1 += uScrollSpeed * uTime;

        vec4 color0 = texture(uTexture, uv0);
        vec4 color1 = texture(uTexture, uv1);
        vec4 color = mix(color0, color1, frac);
        FragColor = vec4(color.rgb * uTint, color.a * uAlpha);
    } else {
        // UV scrolling for continuous drift effects
        uv += uScrollSpeed * uTime;

        vec4 color = texture(uTexture, uv);
        FragColor = vec4(color.rgb * uTint, color.a * uAlpha);
    }
}
