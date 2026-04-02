#pragma once

#include "renderer/Mesh.h"
#include "renderer/Shader.h"
#include <glm/glm.hpp>

namespace dw {

class InputManager;
class Camera;

class Player {
public:
    Player() = default;
    ~Player() = default;

    bool init();
    void update(float dt, const InputManager& input, const Camera& camera);
    void render(Shader& shader);

    const glm::vec3& getPosition() const { return m_position; }
    void setPosition(const glm::vec3& pos) { m_position = pos; }

    // Collision bounds (AABB half-extents)
    void setWorldBounds(float minX, float maxX, float minZ, float maxZ);

private:
    glm::vec3 m_position{0.0f, 0.0f, 0.0f};
    float m_rotation = 0.0f; // Y-axis rotation in radians
    float m_moveSpeed = 3.0f;
    float m_rotSpeed = 3.0f;

    // World bounds
    float m_boundsMinX = -10.0f;
    float m_boundsMaxX = 10.0f;
    float m_boundsMinZ = -10.0f;
    float m_boundsMaxZ = 10.0f;

    Mesh m_mesh; // simple placeholder mesh
};

} // namespace dw
