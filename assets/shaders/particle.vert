#version 330 core

layout (location = 0) in vec3 aPos;
layout (location = 1) in float aSize;
layout (location = 2) in vec4 aColor;

uniform mat4 uView;
uniform mat4 uProjection;

out vec4 vColor;

void main() {
    vColor = aColor;
    vec4 viewPos = uView * vec4(aPos, 1.0);
    gl_Position = uProjection * viewPos;

    // Scale point size by distance (closer = bigger)
    float dist = length(viewPos.xyz);
    gl_PointSize = aSize * (300.0 / dist);
    gl_PointSize = clamp(gl_PointSize, 1.0, 64.0);
}
