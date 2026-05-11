#pragma once

#include "renderer/Shader.h"
#include <glad/gl.h>
#include <functional>

namespace dw {

class RoomTransition {
public:
    RoomTransition() = default;

    bool init();
    void onResize(int w, int h);
    void startTransition(float duration, std::function<void()> onMidpoint);
    void update(float dt);
    void render();
    bool isActive() const { return m_active; }
    void shutdown();

private:
    Shader m_shader;
    GLuint m_vao = 0;
    GLuint m_vbo = 0;

    bool m_active = false;
    float m_timer = 0.0f;
    float m_duration = 1.0f;
    float m_alpha = 0.0f;
    bool m_midpointFired = false;
    std::function<void()> m_onMidpoint;
    int m_viewportW = 1280;
    int m_viewportH = 720;
};

} // namespace dw
