#include "renderer/Camera.h"

namespace dw {

void Camera::setup(const glm::vec3& position, const glm::vec3& target, const glm::vec3& up) {
    m_position = position;
    m_target = target;
    m_view = glm::lookAt(position, target, up);
}

void Camera::setPerspective(float fovDegrees, float aspect, float nearPlane, float farPlane) {
    m_projection = glm::perspective(glm::radians(fovDegrees), aspect, nearPlane, farPlane);
}

} // namespace dw
