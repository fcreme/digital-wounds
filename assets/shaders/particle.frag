#version 330 core

in vec4 vColor;
out vec4 FragColor;

void main() {
    // Soft circular particle
    vec2 center = gl_PointCoord - vec2(0.5);
    float dist = length(center);
    float alpha = smoothstep(0.5, 0.2, dist) * vColor.a;

    if (alpha < 0.01) discard;

    FragColor = vec4(vColor.rgb, alpha);
}
