#pragma once

#include "renderer/Texture.h"

#include <glad/gl.h>
#include <glm/glm.hpp>
#include <string>
#include <vector>

namespace dw {

class UIOverlay;
class InputManager;

struct InventoryItem {
    std::string id;
    std::string name;
    std::string description;
    std::string iconPath;
    GLuint iconTexture = 0;
    bool iconLoaded = false;
};

enum class InventoryState {
    Closed,
    Opening,
    Open,
    Closing
};

class Inventory {
public:
    Inventory() = default;
    ~Inventory() = default;

    void addItem(const std::string& id, const std::string& name,
                 const std::string& description, const std::string& iconPath);
    bool hasItem(const std::string& id) const;
    void removeItem(const std::string& id);

    void toggle();
    bool isOpen() const { return m_state != InventoryState::Closed; }

    void update(float dt, const InputManager& input);
    void renderUI(UIOverlay& ui, int screenWidth, int screenHeight);

private:
    void loadIconTexture(InventoryItem& item);
    static GLuint generateProceduralIcon(const std::string& name);

    std::vector<InventoryItem> m_items;
    int m_selectedIndex = 0;

    InventoryState m_state = InventoryState::Closed;
    float m_animTimer = 0.0f;
    float m_animDuration = 0.3f;
    float m_openAlpha = 0.0f;

    static constexpr int GRID_COLS = 4;
};

} // namespace dw
