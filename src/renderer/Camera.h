#pragma once

#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

namespace dw {

// Fixed camera (RE Remake style) — one camera per room, no free-look
class Camera {
public:
    Camera() = default;

    void setup(const glm::vec3& position, const glm::vec3& target, const glm::vec3& up = glm::vec3(0.0f, 1.0f, 0.0f));
    void setPerspective(float fovDegrees, float aspect, float nearPlane, float farPlane);

    const glm::mat4& getView() const { return m_view; }
    const glm::mat4& getProjection() const { return m_projection; }
    const glm::vec3& getPosition() const { return m_position; }

private:
    glm::vec3 m_position{0.0f, 1.5f, 5.0f};
    glm::vec3 m_target{0.0f, 0.0f, 0.0f};

    glm::mat4 m_view{1.0f};
    glm::mat4 m_projection{1.0f};
};

} // namespace dw
