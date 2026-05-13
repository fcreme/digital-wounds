#include "world/Inventory.h"
#include "ui/UIOverlay.h"
#include "core/InputManager.h"

#include <SDL.h>
#include <algorithm>
#include <iostream>
#include <cmath>
#include <vector>

#include <stb_image.h>

namespace dw {

void Inventory::addItem(const std::string& id, const std::string& name,
                        const std::string& description, const std::string& iconPath) {
    if (hasItem(id)) return;

    InventoryItem item;
    item.id = id;
    item.name = name;
    item.description = description;
    item.iconPath = iconPath;
    m_items.push_back(std::move(item));
    std::cout << "Inventory: added '" << name << "' (" << id << ")\n";
}

bool Inventory::hasItem(const std::string& id) const {
    for (const auto& item : m_items) {
        if (item.id == id) return true;
    }
    return false;
}

void Inventory::removeItem(const std::string& id) {
    m_items.erase(
        std::remove_if(m_items.begin(), m_items.end(),
                       [&id](const InventoryItem& item) { return item.id == id; }),
        m_items.end());
}

void Inventory::toggle() {
    if (m_state == InventoryState::Closed) {
        m_state = InventoryState::Opening;
        m_animTimer = 0.0f;
    } else if (m_state == InventoryState::Open) {
        m_state = InventoryState::Closing;
        m_animTimer = 0.0f;
    }
}

void Inventory::update(float dt, const InputManager& input) {
    switch (m_state) {
        case InventoryState::Opening:
            m_animTimer += dt;
            m_openAlpha = std::min(m_animTimer / m_animDuration, 1.0f);
            if (m_animTimer >= m_animDuration) {
                m_state = InventoryState::Open;
                m_openAlpha = 1.0f;
            }
            break;

        case InventoryState::Closing:
            m_animTimer += dt;
            m_openAlpha = 1.0f - std::min(m_animTimer / m_animDuration, 1.0f);
            if (m_animTimer >= m_animDuration) {
                m_state = InventoryState::Closed;
                m_openAlpha = 0.0f;
            }
            break;

        case InventoryState::Open:
            if (!m_items.empty()) {
                // A/D or Left/Right to navigate columns
                if (input.isKeyPressed(SDL_SCANCODE_D) || input.isKeyPressed(SDL_SCANCODE_RIGHT)) {
                    m_selectedIndex = std::min(m_selectedIndex + 1, static_cast<int>(m_items.size()) - 1);
                }
                if (input.isKeyPressed(SDL_SCANCODE_A) || input.isKeyPressed(SDL_SCANCODE_LEFT)) {
                    m_selectedIndex = std::max(m_selectedIndex - 1, 0);
                }
                // W/S or Up/Down to navigate rows
                if (input.isKeyPressed(SDL_SCANCODE_S) || input.isKeyPressed(SDL_SCANCODE_DOWN)) {
                    int next = m_selectedIndex + GRID_COLS;
                    if (next < static_cast<int>(m_items.size())) m_selectedIndex = next;
                }
                if (input.isKeyPressed(SDL_SCANCODE_W) || input.isKeyPressed(SDL_SCANCODE_UP)) {
                    int next = m_selectedIndex - GRID_COLS;
                    if (next >= 0) m_selectedIndex = next;
                }
            }
            // Q or Tab to close
            if (input.isKeyPressed(SDL_SCANCODE_Q)) {
                toggle();
            }
            break;

        case InventoryState::Closed:
            break;
    }
}

void Inventory::renderUI(UIOverlay& ui, int screenWidth, int screenHeight) {
    if (m_state == InventoryState::Closed) return;

    float alpha = m_openAlpha;

    // Dark overlay
    ui.drawRect(0, 0, static_cast<float>(screenWidth), static_cast<float>(screenHeight),
                glm::vec4(0.0f, 0.0f, 0.0f, 0.75f * alpha));

    // Panel dimensions
    float panelW = screenWidth * 0.5f;
    float panelH = screenHeight * 0.6f;

    // Scale animation
    float scale = alpha;
    float scaledW = panelW * scale;
    float scaledH = panelH * scale;
    float scaledX = (screenWidth - scaledW) * 0.5f;
    float scaledY = (screenHeight - scaledH) * 0.5f;

    // Panel background
    ui.drawRect(scaledX, scaledY, scaledW, scaledH,
                glm::vec4(0.08f, 0.06f, 0.04f, 0.95f * alpha));

    // Panel border (inner lighter rect)
    float border = 4.0f * scale;
    ui.drawRect(scaledX + border, scaledY + border,
                scaledW - border * 2.0f, scaledH - border * 2.0f,
                glm::vec4(0.15f, 0.12f, 0.08f, 0.9f * alpha));

    // Title
    std::string title = "INVENTORY";
    float titleScale = 2.5f * scale;
    float titleW = title.length() * 8.0f * titleScale;
    float titleX = (screenWidth - titleW) * 0.5f;
    float titleY = scaledY + 12.0f * scale;
    ui.drawText(title, titleX, titleY, titleScale,
                glm::vec4(0.8f, 0.7f, 0.5f, alpha));

    if (m_items.empty()) {
        std::string emptyMsg = "No items";
        float emptyScale = 1.8f * scale;
        float emptyW = emptyMsg.length() * 8.0f * emptyScale;
        float emptyX = (screenWidth - emptyW) * 0.5f;
        float emptyY = scaledY + scaledH * 0.4f;
        ui.drawText(emptyMsg, emptyX, emptyY, emptyScale,
                    glm::vec4(0.5f, 0.5f, 0.4f, alpha * 0.7f));
    } else {
        // Item grid
        float gridStartY = scaledY + 40.0f * scale;
        float cellSize = 64.0f * scale;
        float cellPad = 8.0f * scale;
        float gridW = GRID_COLS * (cellSize + cellPad) - cellPad;
        float gridStartX = (screenWidth - gridW) * 0.5f;

        for (int i = 0; i < static_cast<int>(m_items.size()); i++) {
            int col = i % GRID_COLS;
            int row = i / GRID_COLS;
            float cx = gridStartX + col * (cellSize + cellPad);
            float cy = gridStartY + row * (cellSize + cellPad);

            // Cell background
            bool selected = (i == m_selectedIndex);
            glm::vec4 cellColor = selected
                ? glm::vec4(0.4f, 0.3f, 0.15f, alpha)
                : glm::vec4(0.1f, 0.08f, 0.06f, alpha * 0.8f);
            ui.drawRect(cx, cy, cellSize, cellSize, cellColor);

            // Load icon lazily
            if (!m_items[i].iconLoaded) {
                loadIconTexture(m_items[i]);
            }

            // Draw icon or fallback letter
            if (m_items[i].iconTexture != 0) {
                ui.drawTexturedRect(cx + 4.0f * scale, cy + 4.0f * scale,
                                   cellSize - 8.0f * scale, cellSize - 8.0f * scale,
                                   m_items[i].iconTexture, alpha);
            } else {
                // Fallback: draw first letter of name
                std::string letter = m_items[i].name.empty() ? "?" : m_items[i].name.substr(0, 1);
                float letterScale = 3.0f * scale;
                float letterX = cx + (cellSize - 8.0f * letterScale) * 0.5f;
                float letterY = cy + (cellSize - 8.0f * letterScale) * 0.5f;
                ui.drawText(letter, letterX, letterY, letterScale,
                            glm::vec4(0.7f, 0.6f, 0.4f, alpha));
            }

            // Selection border highlight
            if (selected) {
                float bw = 2.0f * scale;
                ui.drawRect(cx, cy, cellSize, bw, glm::vec4(0.9f, 0.7f, 0.3f, alpha));
                ui.drawRect(cx, cy + cellSize - bw, cellSize, bw, glm::vec4(0.9f, 0.7f, 0.3f, alpha));
                ui.drawRect(cx, cy, bw, cellSize, glm::vec4(0.9f, 0.7f, 0.3f, alpha));
                ui.drawRect(cx + cellSize - bw, cy, bw, cellSize, glm::vec4(0.9f, 0.7f, 0.3f, alpha));
            }
        }

        // Selected item name and description
        if (m_selectedIndex >= 0 && m_selectedIndex < static_cast<int>(m_items.size())) {
            const auto& sel = m_items[m_selectedIndex];
            int maxRows = (static_cast<int>(m_items.size()) + GRID_COLS - 1) / GRID_COLS;
            float descY = gridStartY + maxRows * (cellSize + cellPad) + 10.0f * scale;

            float nameScale = 2.0f * scale;
            float nameW = sel.name.length() * 8.0f * nameScale;
            float nameX = (screenWidth - nameW) * 0.5f;
            ui.drawText(sel.name, nameX, descY, nameScale,
                        glm::vec4(0.9f, 0.8f, 0.5f, alpha));

            if (!sel.description.empty()) {
                float descScale = 1.5f * scale;
                float descW = sel.description.length() * 8.0f * descScale;
                float descX = (screenWidth - descW) * 0.5f;
                ui.drawText(sel.description, descX, descY + 24.0f * scale, descScale,
                            glm::vec4(0.6f, 0.55f, 0.45f, alpha));
            }
        }
    }

    // Controls hint
    if (m_state == InventoryState::Open) {
        std::string hint = "A/D: Navigate   TAB/Q: Close";
        float hintScale = 1.5f * scale;
        float hintW = hint.length() * 8.0f * hintScale;
        float hintX = (screenWidth - hintW) * 0.5f;
        float hintY = scaledY + scaledH - 24.0f * scale;
        ui.drawText(hint, hintX, hintY, hintScale,
                    glm::vec4(0.5f, 0.5f, 0.4f, alpha * 0.8f));
    }
}

void Inventory::loadIconTexture(InventoryItem& item) {
    item.iconLoaded = true;

    if (!item.iconPath.empty()) {
        int w, h, channels;
        unsigned char* data = stbi_load(item.iconPath.c_str(), &w, &h, &channels, 4);
        if (data) {
            GLuint tex;
            glGenTextures(1, &tex);
            glBindTexture(GL_TEXTURE_2D, tex);
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
            stbi_image_free(data);
            item.iconTexture = tex;
            return;
        }
    }

    // Fallback: generate procedural icon
    item.iconTexture = generateProceduralIcon(item.name);
}

GLuint Inventory::generateProceduralIcon(const std::string& name) {
    constexpr int SIZE = 64;
    std::vector<unsigned char> pixels(SIZE * SIZE * 4);

    // Hash the name to pick a color
    unsigned int hash = 0;
    for (char c : name) hash = hash * 31 + static_cast<unsigned int>(c);

    float r = 0.3f + (hash % 100) / 200.0f;
    float g = 0.2f + ((hash / 100) % 100) / 200.0f;
    float b = 0.1f + ((hash / 10000) % 100) / 200.0f;

    for (int y = 0; y < SIZE; y++) {
        for (int x = 0; x < SIZE; x++) {
            int idx = (y * SIZE + x) * 4;
            // Rounded rectangle shape
            float u = static_cast<float>(x) / SIZE;
            float v = static_cast<float>(y) / SIZE;
            float border = std::min({u, v, 1.0f - u, 1.0f - v});
            float mask = std::clamp(border * SIZE * 0.3f, 0.0f, 1.0f);

            pixels[idx + 0] = static_cast<unsigned char>(r * mask * 255);
            pixels[idx + 1] = static_cast<unsigned char>(g * mask * 255);
            pixels[idx + 2] = static_cast<unsigned char>(b * mask * 255);
            pixels[idx + 3] = static_cast<unsigned char>(mask * 255);
        }
    }

    GLuint tex;
    glGenTextures(1, &tex);
    glBindTexture(GL_TEXTURE_2D, tex);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, SIZE, SIZE, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);

    return tex;
}

} // namespace dw
