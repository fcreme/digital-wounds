#include "world/Item.h"

#include <algorithm>
#include <iostream>

namespace dw {

void WorldItem::init(const std::string& id, const std::string& name,
                     const std::string& description, const std::string& iconPath,
                     const glm::vec3& worldPos, float interactRadius) {
    m_id = id;
    m_name = name;
    m_description = description;
    m_iconPath = iconPath;
    m_worldPos = worldPos;
    m_interactRadius = interactRadius;
    m_state = ItemState::Idle;
    m_pickupTimer = 0.0f;
}

bool WorldItem::isPlayerNear(const glm::vec3& playerPos) const {
    float dx = playerPos.x - m_worldPos.x;
    float dz = playerPos.z - m_worldPos.z;
    return (dx * dx + dz * dz) < (m_interactRadius * m_interactRadius);
}

void WorldItem::pickUp() {
    if (m_state == ItemState::Idle) {
        m_state = ItemState::PickingUp;
        m_pickupTimer = 0.0f;
        std::cout << "Item: picking up '" << m_name << "'\n";
    }
}

void WorldItem::update(float dt) {
    if (m_state == ItemState::PickingUp) {
        m_pickupTimer += dt;
        if (m_pickupTimer >= PICKUP_DURATION) {
            m_state = ItemState::Gone;
        }
    }
}

float WorldItem::getPickupProgress() const {
    if (m_state != ItemState::PickingUp) return 0.0f;
    return std::min(m_pickupTimer / PICKUP_DURATION, 1.0f);
}

} // namespace dw
