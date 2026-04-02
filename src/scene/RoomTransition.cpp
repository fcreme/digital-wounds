#include "scene/RoomTransition.h"

#include <glad/gl.h>
#include <iostream>
#include <algorithm>

namespace dw {

bool RoomTransition::init() {
    if (!m_shader.loadFromFile("assets/shaders/fade.vert", "assets/shaders/fade.frag")) {
        std::cerr << "RoomTransition: failed to load shaders\n";
        return false;
    }

    float quad[] = {
        -1.0f,  1.0f,
        -1.0f, -1.0f,
         1.0f, -1.0f,
        -1.0f,  1.0f,
         1.0f, -1.0f,
         1.0f,  1.0f,
    };

    glGenVertexArrays(1, &m_vao);
    glGenBuffers(1, &m_vbo);
    glBindVertexArray(m_vao);
    glBindBuffer(GL_ARRAY_BUFFER, m_vbo);
    glBufferData(GL_ARRAY_BUFFER, sizeof(quad), quad, GL_STATIC_DRAW);
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * sizeof(float), (void*)0);
    glBindVertexArray(0);

    std::cout << "RoomTransition initialized\n";
    return true;
}

void RoomTransition::startTransition(float duration, std::function<void()> onMidpoint) {
    m_active = true;
    m_timer = 0.0f;
    m_duration = duration;
    m_alpha = 0.0f;
    m_midpointFired = false;
    m_onMidpoint = std::move(onMidpoint);
}

void RoomTransition::update(float dt) {
    if (!m_active) return;

    m_timer += dt;
    float halfDuration = m_duration * 0.5f;

    if (m_timer < halfDuration) {
        // Fade to black
        m_alpha = m_timer / halfDuration;
    } else {
        // Fire midpoint callback (load new room)
        if (!m_midpointFired) {
            m_midpointFired = true;
            if (m_onMidpoint) m_onMidpoint();
        }
        // Fade from black
        m_alpha = 1.0f - (m_timer - halfDuration) / halfDuration;
    }

    m_alpha = std::clamp(m_alpha, 0.0f, 1.0f);

    if (m_timer >= m_duration) {
        m_active = false;
        m_alpha = 0.0f;
    }
}

void RoomTransition::render() {
    if (!m_active || m_alpha <= 0.001f) return;

    glDisable(GL_DEPTH_TEST);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

    m_shader.use();
    m_shader.setFloat("uAlpha", m_alpha);

    glBindVertexArray(m_vao);
    glDrawArrays(GL_TRIANGLES, 0, 6);
    glBindVertexArray(0);

    glEnable(GL_DEPTH_TEST);
}

void RoomTransition::shutdown() {
    if (m_vbo) { glDeleteBuffers(1, &m_vbo); m_vbo = 0; }
    if (m_vao) { glDeleteVertexArrays(1, &m_vao); m_vao = 0; }
}

} // namespace dw
