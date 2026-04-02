#pragma once

#include "scene/Room.h"
#include "scene/RoomTransition.h"
#include "renderer/Camera.h"
#include "renderer/Mesh.h"
#include "renderer/Texture.h"
#include "renderer/Shader.h"
#include "fx/ParticleSystem.h"
#include "world/Player.h"

#include <string>
#include <memory>
#include <vector>

namespace dw {

class Renderer;
class InputManager;
class AudioManager;

struct TriggerZone {
    glm::vec3 position{0.0f};
    float radius = 1.0f;
    std::string targetRoom;
    glm::vec3 spawnPos{0.0f};
};

class Scene {
public:
    Scene();
    ~Scene();

    bool init(Renderer& renderer);
    bool loadRoom(const std::string& roomDefPath, Renderer& renderer);
    void update(float dt, const InputManager& input, Renderer& renderer, AudioManager* audio);
    void renderObjects();
    void renderParticles();
    void renderOverlays();
    void shutdown();

    Camera& getCamera() { return m_camera; }
    Player& getPlayer() { return m_player; }
    const RoomDef& getCurrentRoom() const { return m_currentRoom; }

private:
    RoomDef m_currentRoom;
    Camera m_camera;
    Shader m_meshShader;
    Player m_player;
    RoomTransition m_transition;
    ParticleSystem m_particles;

    struct PropInstance {
        Mesh mesh;
        Texture texture;
        glm::mat4 transform{1.0f};
        float rotationSpeed = 0.0f;
        glm::vec3 materialColor{0.5f, 0.5f, 0.5f};
    };
    std::vector<std::unique_ptr<PropInstance>> m_props;
    std::vector<TriggerZone> m_triggers;
    std::vector<PointLightDef> m_pointLights;

    float m_propTime = 0.0f;
    bool m_playerMoving = false;
};

} // namespace dw
