#include "world/Book.h"
#include "ui/UIOverlay.h"
#include "core/InputManager.h"

#include <glm/glm.hpp>
#include <algorithm>
#include <iostream>

namespace dw {

void Book::init(const glm::vec3& worldPos, float interactRadius) {
    m_worldPos = worldPos;
    m_interactRadius = interactRadius;
    m_state = BookState::Closed;
    m_currentPage = 0;
    m_openAlpha = 0.0f;
}

void Book::addPage(const std::string& texturePath) {
    BookPage page;
    page.texturePath = texturePath;
    page.texture = std::make_unique<Texture>();
    if (!texturePath.empty()) {
        if (!page.texture->load(texturePath)) {
            std::cerr << "Book: failed to load page texture: " << texturePath << "\n";
        }
    }
    m_pages.push_back(std::move(page));
}

bool Book::isPlayerNear(const glm::vec3& playerPos) const {
    float dx = playerPos.x - m_worldPos.x;
    float dz = playerPos.z - m_worldPos.z;
    return (dx * dx + dz * dz) < (m_interactRadius * m_interactRadius);
}

void Book::open() {
    if (m_state == BookState::Closed) {
        m_state = BookState::Opening;
        m_animTimer = 0.0f;
        m_currentPage = 0;
        std::cout << "Book: opening\n";
    }
}

void Book::close() {
    if (m_state == BookState::Open) {
        m_state = BookState::Closing;
        m_animTimer = 0.0f;
        std::cout << "Book: closing\n";
    }
}

void Book::update(float dt, const InputManager& input) {
    switch (m_state) {
        case BookState::Opening:
            m_animTimer += dt;
            m_openAlpha = std::min(m_animTimer / m_animDuration, 1.0f);
            if (m_animTimer >= m_animDuration) {
                m_state = BookState::Open;
                m_openAlpha = 1.0f;
            }
            break;

        case BookState::Closing:
            m_animTimer += dt;
            m_openAlpha = 1.0f - std::min(m_animTimer / m_animDuration, 1.0f);
            if (m_animTimer >= m_animDuration) {
                m_state = BookState::Closed;
                m_openAlpha = 0.0f;
            }
            break;

        case BookState::Open:
            // A/D or Left/Right to turn pages
            if (input.isKeyPressed(SDL_SCANCODE_D) || input.isKeyPressed(SDL_SCANCODE_RIGHT)) {
                if (m_currentPage < static_cast<int>(m_pages.size()) - 1) {
                    m_currentPage++;
                    m_state = BookState::TurningPage;
                    m_animTimer = 0.0f;
                }
            }
            if (input.isKeyPressed(SDL_SCANCODE_A) || input.isKeyPressed(SDL_SCANCODE_LEFT)) {
                if (m_currentPage > 0) {
                    m_currentPage--;
                    m_state = BookState::TurningPage;
                    m_animTimer = 0.0f;
                }
            }
            // Q or Escape to close
            if (input.isKeyPressed(SDL_SCANCODE_Q)) {
                close();
            }
            break;

        case BookState::TurningPage:
            m_animTimer += dt;
            if (m_animTimer >= 0.2f) {
                m_state = BookState::Open;
            }
            break;

        case BookState::Closed:
            break;
    }
}

void Book::renderUI(UIOverlay& ui, int screenWidth, int screenHeight) {
    if (m_state == BookState::Closed) return;

    float alpha = m_openAlpha;

    // Dark overlay behind the book
    ui.drawRect(0, 0, static_cast<float>(screenWidth), static_cast<float>(screenHeight),
                glm::vec4(0.0f, 0.0f, 0.0f, 0.7f * alpha));

    // Book frame area (centered, ~70% of screen)
    float bookW = screenWidth * 0.6f;
    float bookH = screenHeight * 0.75f;

    // Scale animation
    float scale = alpha;
    float scaledW = bookW * scale;
    float scaledH = bookH * scale;
    float scaledX = (screenWidth - scaledW) * 0.5f;
    float scaledY = (screenHeight - scaledH) * 0.5f;

    // Book background (dark leather)
    ui.drawRect(scaledX, scaledY, scaledW, scaledH,
                glm::vec4(0.12f, 0.08f, 0.05f, alpha));

    // Inner page area (slightly lighter)
    float margin = 12.0f * scale;
    ui.drawRect(scaledX + margin, scaledY + margin,
                scaledW - margin * 2.0f, scaledH - margin * 2.0f,
                glm::vec4(0.85f, 0.8f, 0.7f, alpha));

    // Page texture (if available)
    if (m_currentPage >= 0 && m_currentPage < static_cast<int>(m_pages.size())) {
        GLuint texId = m_pages[m_currentPage].texture ? m_pages[m_currentPage].texture->getID() : 0;
        if (texId != 0) {
            ui.drawTexturedRect(scaledX + margin, scaledY + margin,
                               scaledW - margin * 2.0f, scaledH - margin * 2.0f,
                               texId, alpha);
        }
    }

    // Page number
    if (m_state == BookState::Open && !m_pages.empty()) {
        std::string pageStr = std::to_string(m_currentPage + 1) + "/" + std::to_string(m_pages.size());
        float textScale = 2.0f;
        float textW = pageStr.length() * 8.0f * textScale;
        float textX = (screenWidth - textW) * 0.5f;
        float textY = scaledY + scaledH + 8.0f;
        ui.drawText(pageStr, textX, textY, textScale, glm::vec4(0.7f, 0.65f, 0.5f, alpha));
    }

    // Controls hint
    if (m_state == BookState::Open) {
        std::string hint = "A/D: Turn page   Q: Close";
        float hintScale = 1.5f;
        float hintW = hint.length() * 8.0f * hintScale;
        float hintX = (screenWidth - hintW) * 0.5f;
        float hintY = scaledY + scaledH + 30.0f;
        ui.drawText(hint, hintX, hintY, hintScale, glm::vec4(0.5f, 0.5f, 0.4f, alpha * 0.8f));
    }
}

} // namespace dw
