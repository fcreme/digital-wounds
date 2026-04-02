#include "world/Player.h"
#include "core/InputManager.h"
#include "renderer/Camera.h"

#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <algorithm>
#include <cmath>
#include <iostream>

namespace dw {

bool Player::init() {
    // Simple capsule-like shape: a tall cube as placeholder
    m_mesh = Mesh::createCube(1.0f);
    std::cout << "Player initialized\n";
    return true;
}

void Player::update(float dt, const InputManager& input, const Camera& camera) {
    (void)camera;

    // Tank controls (RE style): left/right rotates, up/down moves forward/back
    if (input.isKeyDown(SDL_SCANCODE_A)) {
        m_rotation += m_rotSpeed * dt;
    }
    if (input.isKeyDown(SDL_SCANCODE_D)) {
        m_rotation -= m_rotSpeed * dt;
    }

    float forwardX = -std::sin(m_rotation);
    float forwardZ = -std::cos(m_rotation);

    glm::vec3 movement(0.0f);
    if (input.isKeyDown(SDL_SCANCODE_W)) {
        movement.x += forwardX * m_moveSpeed * dt;
        movement.z += forwardZ * m_moveSpeed * dt;
    }
    if (input.isKeyDown(SDL_SCANCODE_S)) {
        movement.x -= forwardX * m_moveSpeed * dt * 0.6f; // slower backwards
        movement.z -= forwardZ * m_moveSpeed * dt * 0.6f;
    }

    m_position += movement;

    // Clamp to world bounds
    m_position.x = std::clamp(m_position.x, m_boundsMinX, m_boundsMaxX);
    m_position.z = std::clamp(m_position.z, m_boundsMinZ, m_boundsMaxZ);
}

void Player::render(Shader& shader) {
    glm::mat4 model(1.0f);
    model = glm::translate(model, m_position + glm::vec3(0.0f, 0.5f, 0.0f)); // raise to stand on ground
    model = glm::rotate(model, m_rotation, glm::vec3(0.0f, 1.0f, 0.0f));
    model = glm::scale(model, glm::vec3(0.4f, 0.9f, 0.3f)); // tall thin box

    shader.setMat4("uModel", glm::value_ptr(model));
    m_mesh.draw();
}

void Player::setWorldBounds(float minX, float maxX, float minZ, float maxZ) {
    m_boundsMinX = minX;
    m_boundsMaxX = maxX;
    m_boundsMinZ = minZ;
    m_boundsMaxZ = maxZ;
}

} // namespace dw
