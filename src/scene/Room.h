#pragma once

#include "renderer/Camera.h"
#include <glm/glm.hpp>
#include <string>
#include <vector>

namespace dw {

struct RoomPropDef {
    std::string modelPath;
    std::string texturePath;
    glm::vec3 position{0.0f};
    glm::vec3 rotation{0.0f};  // euler degrees
    glm::vec3 scale{1.0f};
    bool interactive = false;
};

struct PointLightDef {
    glm::vec3 position{0.0f};
    glm::vec3 color{1.0f};
    float radius = 5.0f;
    bool flicker = false;
};

struct RoomDef {
    std::string name;
    std::string backgroundPath;
    std::string collisionPath;
    std::string ambientAudioPath;

    // Camera
    glm::vec3 cameraPos{0.0f, 2.0f, 5.0f};
    glm::vec3 cameraTarget{0.0f, 0.0f, 0.0f};
    float cameraFov = 45.0f;

    // Props
    std::vector<RoomPropDef> props;

    // Lighting
    glm::vec3 ambientColor{0.1f, 0.1f, 0.12f};
    glm::vec3 lightDir{-0.5f, -1.0f, -0.3f};
    glm::vec3 lightColor{0.8f, 0.75f, 0.7f};
    std::vector<PointLightDef> pointLights;
};

bool loadRoomDef(const std::string& path, RoomDef& out);

} // namespace dw
