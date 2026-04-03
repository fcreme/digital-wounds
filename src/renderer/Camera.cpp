#include "renderer/Camera.h"

#include <cmath>

namespace dw {

void Camera::setup(const glm::vec3& position, const glm::vec3& target, const glm::vec3& up) {
    m_position = position;
    m_target = target;
    m_view = glm::lookAt(position, target, up);
}

void Camera::setPerspective(float fovDegrees, float aspect, float nearPlane, float farPlane) {
    m_projection = glm::perspective(glm::radians(fovDegrees), aspect, nearPlane, farPlane);
}

void Camera::updateFromPlayer(const glm::vec3& playerPos, float eyeHeight, float yaw, float pitch) {
    m_position = playerPos + glm::vec3(0.0f, eyeHeight, 0.0f);

    glm::vec3 front;
    front.x = std::cos(pitch) * std::sin(yaw);
    front.y = std::sin(pitch);
    front.z = std::cos(pitch) * std::cos(yaw);
    front = glm::normalize(front);

    m_target = m_position + front;
    m_view = glm::lookAt(m_position, m_target, glm::vec3(0.0f, 1.0f, 0.0f));
}

} // namespace dw
