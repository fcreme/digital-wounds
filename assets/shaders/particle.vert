#version 330 core

layout (location = 0) in vec3 aPos;
layout (location = 1) in float aSize;
layout (location = 2) in vec4 aColor;
layout (location = 3) in float aType;

uniform mat4 uView;
uniform mat4 uProjection;

out vec4 vColor;
flat out int vType;
out float vViewDepth;

void main() {
    vColor = aColor;
    vType = int(aType + 0.5);
    vec4 viewPos = uView * vec4(aPos, 1.0);
    vViewDepth = -viewPos.z; // positive linear depth in view space
    gl_Position = uProjection * viewPos;

    // Scale point size by distance (closer = bigger)
    float dist = length(viewPos.xyz);
    gl_PointSize = aSize * (300.0 / dist);
    gl_PointSize = clamp(gl_PointSize, 1.0, 64.0);
}
