#include "ui/TitleScreen.h"
#include "ui/UIOverlay.h"
#include "core/InputManager.h"

#include <glad/gl.h>
#include <glm/glm.hpp>
#include <cmath>
#include <iostream>
#include <algorithm>

namespace dw {

bool TitleScreen::init(int screenWidth, int screenHeight) {
    m_screenWidth = screenWidth;
    m_screenHeight = screenHeight;

    // Set up a static camera looking into a dark volume
    m_camera.setup(glm::vec3(0.0f, 1.5f, 5.0f), glm::vec3(0.0f, 1.0f, 0.0f));
    m_camera.setPerspective(45.0f, static_cast<float>(screenWidth) / static_cast<float>(screenHeight), 0.1f, 100.0f);

    if (!m_particles.init()) {
        std::cerr << "TitleScreen: failed to init particles\n";
        return false;
    }

    // Atmospheric dust — warm amber, slow float
    ParticleEmitter dust;
    dust.type = ParticleType::Dust;
    dust.origin = glm::vec3(0.0f, 1.0f, 0.0f);
    dust.area = glm::vec3(6.0f, 3.0f, 4.0f);
    dust.count = 60;
    dust.color = glm::vec4(0.9f, 0.75f, 0.5f, 0.15f);
    dust.speed = 0.2f;
    m_particles.addEmitter(dust);

    // Fireflies — warm glow, erratic pulse
    ParticleEmitter fireflies;
    fireflies.type = ParticleType::Fireflies;
    fireflies.origin = glm::vec3(0.0f, 1.5f, 1.0f);
    fireflies.area = glm::vec3(5.0f, 2.5f, 3.0f);
    fireflies.count = 8;
    fireflies.color = glm::vec4(1.0f, 0.85f, 0.4f, 0.4f);
    m_particles.addEmitter(fireflies);

    std::cout << "TitleScreen initialized\n";
    return true;
}

void TitleScreen::update(float dt, const InputManager& input) {
    if (m_finished) return;

    m_time += dt;
    m_particles.update(dt);

    // Start fade-out on Enter or Space (only after prompt is visible)
    if (!m_fadeOut && m_time > 3.5f) {
        if (input.isKeyPressed(SDL_SCANCODE_RETURN) || input.isKeyPressed(SDL_SCANCODE_SPACE)) {
            m_fadeOut = true;
            m_fadeAlpha = 0.0f;
        }
    }

    // Advance fade-out
    if (m_fadeOut) {
        m_fadeAlpha += dt / 1.5f; // 1.5 second fade
        if (m_fadeAlpha >= 1.0f) {
            m_fadeAlpha = 1.0f;
            m_finished = true;
        }
    }
}

void TitleScreen::render(UIOverlay& ui, int screenWidth, int screenHeight) {
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    // Render particles in 3D
    m_particles.render(m_camera.getView(), m_camera.getProjection());

    // --- UI text on top ---

    // "DIGITAL WOUNDS" — fade in from 0.5s to 2.5s
    {
        float titleAlpha = std::clamp((m_time - 0.5f) / 2.0f, 0.0f, 1.0f);
        if (titleAlpha > 0.0f) {
            const std::string title = "DIGITAL WOUNDS";
            float scale = 5.0f;
            float textW = title.length() * 8.0f * scale;
            float x = (screenWidth - textW) * 0.5f;
            float y = screenHeight * 0.30f;
            ui.drawText(title, x, y, scale, glm::vec4(0.9f, 0.8f, 0.6f, titleAlpha));
        }
    }

    // "Press Enter" — pulses after 3.5s
    if (m_time > 3.5f && !m_fadeOut) {
        float pulse = 0.4f + 0.3f * std::sin(m_time * 2.5f);
        const std::string prompt = "Press Enter";
        float scale = 3.0f;
        float textW = prompt.length() * 8.0f * scale;
        float x = (screenWidth - textW) * 0.5f;
        float y = screenHeight * 0.75f;
        ui.drawText(prompt, x, y, scale, glm::vec4(0.9f, 0.8f, 0.6f, pulse));
    }

    // Fade-out overlay
    if (m_fadeOut) {
        ui.drawRect(0, 0, static_cast<float>(screenWidth), static_cast<float>(screenHeight),
                    glm::vec4(0.0f, 0.0f, 0.0f, m_fadeAlpha));
    }
}

void TitleScreen::onResize(int width, int height) {
    m_screenWidth = width;
    m_screenHeight = height;
    m_camera.setPerspective(45.0f, static_cast<float>(width) / static_cast<float>(height), 0.1f, 100.0f);
}

void TitleScreen::shutdown() {
    m_particles.shutdown();
    std::cout << "TitleScreen shutdown\n";
}

} // namespace dw
