#version 330 core

layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aUV;  // (0,0) top-left of the painting

uniform mat4 uView;
uniform mat4 uProjection;

out vec2 vUV;
out vec3 vWorldPos;  // the quads are built in world space

void main() {
    vUV = aUV;
    vWorldPos = aPos;
    gl_Position = uProjection * uView * vec4(aPos, 1.0);
}
