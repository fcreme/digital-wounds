#pragma once

#include <glm/glm.hpp>
#include <string>

namespace dw {

enum class ItemState {
    Idle,
    PickingUp,
    Gone
};

class WorldItem {
public:
    WorldItem() = default;
    ~WorldItem() = default;

    void init(const std::string& id, const std::string& name,
              const std::string& description, const std::string& iconPath,
              const glm::vec3& worldPos, float interactRadius = 2.5f);

    bool isPlayerNear(const glm::vec3& playerPos) const;

    void pickUp();
    void update(float dt);

    void setGone() { m_state = ItemState::Gone; }
    bool isGone() const { return m_state == ItemState::Gone; }
    bool isIdle() const { return m_state == ItemState::Idle; }

    const std::string& getId() const { return m_id; }
    const std::string& getName() const { return m_name; }
    const std::string& getDescription() const { return m_description; }
    const std::string& getIconPath() const { return m_iconPath; }
    const glm::vec3& getPosition() const { return m_worldPos; }
    float getPickupProgress() const;

private:
    std::string m_id;
    std::string m_name;
    std::string m_description;
    std::string m_iconPath;
    glm::vec3 m_worldPos{0.0f};
    float m_interactRadius = 2.5f;

    ItemState m_state = ItemState::Idle;
    float m_pickupTimer = 0.0f;
    static constexpr float PICKUP_DURATION = 0.6f;
};

} // namespace dw
