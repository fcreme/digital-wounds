#pragma once

#include "renderer/Texture.h"

#include <glm/glm.hpp>
#include <string>
#include <vector>
#include <memory>

namespace dw {

class UIOverlay;
class InputManager;

struct BookPage {
    std::string texturePath;
    std::unique_ptr<Texture> texture;
};

enum class BookState {
    Closed,
    Opening,
    Open,
    Closing,
    TurningPage
};

class Book {
public:
    Book() = default;
    ~Book() = default;

    // Setup the book at a world position with page images
    void init(const glm::vec3& worldPos, float interactRadius = 2.0f);
    void addPage(const std::string& texturePath);

    // Check if player is close enough to interact
    bool isPlayerNear(const glm::vec3& playerPos) const;

    // Called each frame — handles state transitions and input
    void update(float dt, const InputManager& input);

    // Render the book viewer UI (call when book is open/opening/closing)
    void renderUI(UIOverlay& ui, int screenWidth, int screenHeight);

    // Is the book currently open (blocking player movement)?
    bool isOpen() const { return m_state != BookState::Closed; }

    const glm::vec3& getPosition() const { return m_worldPos; }

    // Open/close
    void open();
    void close();

private:
    glm::vec3 m_worldPos{0.0f};
    float m_interactRadius = 2.0f;

    std::vector<BookPage> m_pages;
    int m_currentPage = 0;

    BookState m_state = BookState::Closed;
    float m_animTimer = 0.0f;
    float m_animDuration = 0.4f;
    float m_openAlpha = 0.0f; // 0 = fully closed, 1 = fully open
};

} // namespace dw
