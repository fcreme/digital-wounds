#include "renderer/Camera.h"

#include <cmath>

namespace dw {

void Camera::setup(const glm::vec3& position, const glm::vec3& target, const glm::vec3& up) {
    (void)up;  // up vector always (0,1,0) — stored implicitly in rebuildView
    m_position = position;
    m_target = target;
    rebuildView();
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
    rebuildView();
}

void Camera::shake(float intensity, float duration) {
    m_shakeIntensity = intensity;
    m_shakeDuration = duration;
    m_shakeTimer = duration;
}

void Camera::updateShake(float dt) {
    if (m_shakeTimer <= 0.0f) {
        m_shakeOffset = glm::vec3(0.0f);
        return;
    }

    m_shakeTimer -= dt;
    if (m_shakeTimer < 0.0f) m_shakeTimer = 0.0f;

    float remaining = m_shakeTimer / m_shakeDuration;
    float elapsed = m_shakeDuration - m_shakeTimer;
    float offsetX = m_shakeIntensity * std::sin(elapsed * 30.0f) * remaining;
    float offsetY = m_shakeIntensity * std::sin(elapsed * 37.0f) * remaining;
    m_shakeOffset = glm::vec3(offsetX, offsetY, 0.0f);

    rebuildView();
}

void Camera::rebuildView() {
    glm::vec3 pos = m_position + m_shakeOffset;
    m_view = glm::lookAt(pos, m_target + m_shakeOffset, glm::vec3(0.0f, 1.0f, 0.0f));
}

} // namespace dw
