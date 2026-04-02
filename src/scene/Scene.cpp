#include "scene/Scene.h"
#include "renderer/Renderer.h"
#include "renderer/BackgroundLayer.h"
#include "core/InputManager.h"
#include "audio/AudioManager.h"
#include "ui/UIOverlay.h"

#include <glad/gl.h>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <iostream>
#include <cmath>

namespace dw {

Scene::Scene() = default;
Scene::~Scene() = default;

bool Scene::init(Renderer& renderer) {
    (void)renderer;

    if (!m_meshShader.loadFromFile("assets/shaders/mesh.vert", "assets/shaders/mesh.frag")) {
        std::cerr << "Scene: failed to load mesh shader\n";
        return false;
    }

    if (!m_player.init()) {
        std::cerr << "Scene: failed to init player\n";
        return false;
    }

    if (!m_transition.init()) {
        std::cerr << "Scene: failed to init room transition\n";
        return false;
    }

    if (!m_particles.init()) {
        std::cerr << "Scene: failed to init particle system\n";
        return false;
    }

    std::cout << "Scene initialized\n";
    return true;
}

bool Scene::loadRoom(const std::string& roomDefPath, Renderer& renderer) {
    m_props.clear();
    m_triggers.clear();
    m_pointLights.clear();
    m_particles.clear();
    m_books.clear();
    m_nearBookIndex = -1;
    m_activeBook = nullptr;

    if (!loadRoomDef(roomDefPath, m_currentRoom)) {
        return false;
    }

    // Camera
    float aspect = static_cast<float>(renderer.getWidth()) / static_cast<float>(renderer.getHeight());
    m_camera.setup(m_currentRoom.cameraPos, m_currentRoom.cameraTarget);
    m_camera.setPerspective(m_currentRoom.cameraFov, aspect, 0.1f, 100.0f);

    // Background
    if (!m_currentRoom.backgroundPath.empty()) {
        renderer.getBackgroundLayer().loadTexture(m_currentRoom.backgroundPath);
    }

    // Load props (any format via Assimp)
    for (const auto& propDef : m_currentRoom.props) {
        auto prop = std::make_unique<PropInstance>();

        if (!propDef.modelPath.empty()) {
            prop->model = std::make_unique<Model>();
            prop->model->load(propDef.modelPath);
        }
        if (!propDef.texturePath.empty()) prop->texture.load(propDef.texturePath);

        glm::mat4 t(1.0f);
        t = glm::translate(t, propDef.position);
        t = glm::rotate(t, glm::radians(propDef.rotation.y), glm::vec3(0, 1, 0));
        t = glm::rotate(t, glm::radians(propDef.rotation.x), glm::vec3(1, 0, 0));
        t = glm::rotate(t, glm::radians(propDef.rotation.z), glm::vec3(0, 0, 1));
        t = glm::scale(t, propDef.scale);
        prop->transform = t;
        m_props.push_back(std::move(prop));
    }

    // === Room-specific procedural content ===
    if (m_currentRoom.name == "Forest Clearing") {
        // Stone pillars (dark gray)
        auto addPillar = [&](float x, float z) {
            auto p = std::make_unique<PropInstance>();
            p->mesh = Mesh::createCube(1.0f);
            p->transform = glm::scale(glm::translate(glm::mat4(1.0f), glm::vec3(x, 0.75f, z)), glm::vec3(0.5f, 1.5f, 0.5f));
            p->materialColor = glm::vec3(0.25f, 0.23f, 0.22f);
            m_props.push_back(std::move(p));
        };
        addPillar(-2.0f, -1.0f);
        addPillar(2.0f, -1.0f);

        // Floating book (animated)
        auto book = std::make_unique<PropInstance>();
        book->mesh = Mesh::createCube(1.0f);
        book->transform = glm::scale(glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, 1.2f, -2.0f)), glm::vec3(0.6f, 0.05f, 0.4f));
        book->rotationSpeed = 0.8f;
        book->materialColor = glm::vec3(0.4f, 0.2f, 0.1f); // leather brown
        m_props.push_back(std::move(book));

        // Ground plane
        auto ground = std::make_unique<PropInstance>();
        ground->mesh = Mesh::createPlane(12.0f, 12.0f);
        ground->transform = glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, 0.0f, 0.0f));
        ground->materialColor = glm::vec3(0.08f, 0.1f, 0.06f); // dark earth
        m_props.push_back(std::move(ground));

        // Point lights (lanterns near pillars)
        m_pointLights.push_back({{-2.0f, 2.0f, -1.0f}, {0.9f, 0.6f, 0.2f}, 6.0f, true});
        m_pointLights.push_back({{2.0f, 2.0f, -1.0f}, {0.9f, 0.6f, 0.2f}, 6.0f, true});

        // Particles: fireflies
        ParticleEmitter fireflies;
        fireflies.type = ParticleType::Fireflies;
        fireflies.origin = glm::vec3(0.0f, 1.5f, 0.0f);
        fireflies.area = glm::vec3(5.0f, 2.0f, 5.0f);
        fireflies.count = 30;
        fireflies.color = glm::vec4(0.8f, 1.0f, 0.3f, 0.6f);
        m_particles.addEmitter(fireflies);

        // Particles: dust
        ParticleEmitter dust;
        dust.type = ParticleType::Dust;
        dust.origin = glm::vec3(0.0f, 1.0f, 0.0f);
        dust.area = glm::vec3(6.0f, 3.0f, 6.0f);
        dust.count = 80;
        dust.color = glm::vec4(0.7f, 0.7f, 0.6f, 0.15f);
        m_particles.addEmitter(dust);

        // Particles: fog wisps
        ParticleEmitter fog;
        fog.type = ParticleType::Fog;
        fog.origin = glm::vec3(0.0f, 0.3f, 0.0f);
        fog.area = glm::vec3(6.0f, 0.8f, 6.0f);
        fog.count = 40;
        fog.color = glm::vec4(0.6f, 0.65f, 0.7f, 0.06f);
        m_particles.addEmitter(fog);

        // Trigger
        TriggerZone door;
        door.position = glm::vec3(0.0f, 0.0f, -4.0f);
        door.radius = 1.5f;
        door.targetRoom = "assets/rooms/hallway.json";
        door.spawnPos = glm::vec3(0.0f, 0.0f, 3.0f);
        m_triggers.push_back(door);

        // Interactive book at the floating book position
        {
            auto b = std::make_unique<Book>();
            b->init(glm::vec3(0.0f, 1.2f, -2.0f), 2.5f);
            b->addPage("assets/textures/book_page1.png");
            b->addPage("assets/textures/book_page2.png");
            b->addPage("assets/textures/book_page3.png");
            m_books.push_back(std::move(b));
        }

        m_player.setWorldBounds(-4.0f, 4.0f, -4.5f, 4.0f);
    }
    else if (m_currentRoom.name == "Dark Hallway") {
        // Picture Gallery GLB model
        {
            auto prop = std::make_unique<PropInstance>();
            prop->model = std::make_unique<Model>();
            if (prop->model->load("props/the_picture_gallery_low_poly__vr.glb")) {
                glm::mat4 t(1.0f);
                t = glm::translate(t, glm::vec3(0.0f, 0.0f, -2.0f));
                t = glm::scale(t, glm::vec3(1.0f));
                prop->transform = t;
                m_props.push_back(std::move(prop));
            }
        }

        // Hospital props (FBX) — abandoned hospital atmosphere
        auto addModelProp = [&](const std::string& modelPath, glm::vec3 pos, glm::vec3 rot, glm::vec3 scale) {
            auto prop = std::make_unique<PropInstance>();
            prop->model = std::make_unique<Model>();
            if (prop->model->load(modelPath)) {
                glm::mat4 t(1.0f);
                t = glm::translate(t, pos);
                t = glm::rotate(t, glm::radians(rot.y), glm::vec3(0, 1, 0));
                t = glm::rotate(t, glm::radians(rot.x), glm::vec3(1, 0, 0));
                t = glm::rotate(t, glm::radians(rot.z), glm::vec3(0, 0, 1));
                t = glm::scale(t, scale);
                prop->transform = t;
                m_props.push_back(std::move(prop));
            }
        };

        addModelProp("props/hospital_desk.fbx",       glm::vec3(-1.2f, 0.0f, -3.0f), glm::vec3(0, 90, 0),  glm::vec3(0.01f));
        addModelProp("props/hospital_cabinet.fbx",     glm::vec3(1.5f, 0.0f, -4.0f),  glm::vec3(0, 0, 0),   glm::vec3(0.01f));
        addModelProp("props/hospital_wheelchair.fbx",  glm::vec3(0.5f, 0.0f, -1.5f),  glm::vec3(0, -30, 0), glm::vec3(0.01f));
        addModelProp("props/church_pew.obj",           glm::vec3(-1.0f, 0.0f, -5.0f), glm::vec3(0, 0, 0),   glm::vec3(0.5f));

        // Lanterns on walls
        auto addLantern = [&](float x, float y, float z) {
            auto l = std::make_unique<PropInstance>();
            l->mesh = Mesh::createCube(1.0f);
            l->transform = glm::scale(glm::translate(glm::mat4(1.0f), glm::vec3(x, y, z)), glm::vec3(0.15f, 0.25f, 0.15f));
            l->materialColor = glm::vec3(0.6f, 0.4f, 0.1f); // bronze
            m_props.push_back(std::move(l));
        };
        addLantern(-1.5f, 1.8f, 0.0f);
        addLantern(1.5f, 1.8f, 0.0f);
        addLantern(-1.5f, 1.8f, -2.0f);
        addLantern(1.5f, 1.8f, -2.0f);

        // Table
        auto table = std::make_unique<PropInstance>();
        table->mesh = Mesh::createCube(1.0f);
        table->transform = glm::scale(glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, 0.4f, -1.0f)), glm::vec3(1.2f, 0.05f, 0.6f));
        table->materialColor = glm::vec3(0.3f, 0.18f, 0.08f); // dark wood
        m_props.push_back(std::move(table));

        // Floor
        auto floor = std::make_unique<PropInstance>();
        floor->mesh = Mesh::createPlane(4.0f, 10.0f);
        floor->transform = glm::translate(glm::mat4(1.0f), glm::vec3(0.0f, 0.0f, 0.0f));
        floor->materialColor = glm::vec3(0.12f, 0.1f, 0.08f);
        m_props.push_back(std::move(floor));

        // Warm lantern lights
        m_pointLights.push_back({{-1.5f, 2.0f, 0.0f}, {1.0f, 0.7f, 0.3f}, 5.0f, true});
        m_pointLights.push_back({{1.5f, 2.0f, 0.0f}, {1.0f, 0.7f, 0.3f}, 5.0f, true});
        m_pointLights.push_back({{-1.5f, 2.0f, -2.0f}, {0.8f, 0.5f, 0.2f}, 4.0f, true});
        m_pointLights.push_back({{1.5f, 2.0f, -2.0f}, {0.8f, 0.5f, 0.2f}, 4.0f, true});

        // Dust in the hallway
        ParticleEmitter dust;
        dust.type = ParticleType::Dust;
        dust.origin = glm::vec3(0.0f, 1.0f, 0.0f);
        dust.area = glm::vec3(2.0f, 2.0f, 4.0f);
        dust.count = 60;
        dust.color = glm::vec4(0.9f, 0.8f, 0.5f, 0.2f); // warm tint from lanterns
        m_particles.addEmitter(dust);

        // Trigger back
        TriggerZone back;
        back.position = glm::vec3(0.0f, 0.0f, 4.0f);
        back.radius = 1.5f;
        back.targetRoom = "assets/rooms/test_room.json";
        back.spawnPos = glm::vec3(0.0f, 0.0f, -3.0f);
        m_triggers.push_back(back);

        // Book on the table
        {
            auto b = std::make_unique<Book>();
            b->init(glm::vec3(0.0f, 0.5f, -1.0f), 2.0f);
            b->addPage("assets/textures/book_page1.png");
            b->addPage("assets/textures/book_page2.png");
            m_books.push_back(std::move(b));
        }

        m_player.setWorldBounds(-1.8f, 1.8f, -3.0f, 4.5f);
    }

    // Copy point lights from room def (if any were in JSON)
    for (const auto& pl : m_currentRoom.pointLights) {
        m_pointLights.push_back(pl);
    }

    std::cout << "Scene: room '" << m_currentRoom.name << "' loaded — "
              << m_props.size() << " props, " << m_pointLights.size() << " lights, "
              << m_triggers.size() << " triggers\n";
    return true;
}

void Scene::update(float dt, const InputManager& input, Renderer& renderer, AudioManager* audio, UIOverlay* /*ui*/) {
    m_transition.update(dt);
    if (m_transition.isActive()) return;

    // If a book is open, only update the book (block player movement)
    if (m_activeBook) {
        m_activeBook->update(dt, input);
        if (!m_activeBook->isOpen()) {
            m_activeBook = nullptr;
        }
        return;
    }

    glm::vec3 prevPos = m_player.getPosition();
    m_player.update(dt, input, m_camera);
    m_playerMoving = glm::distance(prevPos, m_player.getPosition()) > 0.001f;

    m_propTime += dt;
    m_particles.update(dt);

    // Footstep audio
    if (audio) {
        audio->updateFootsteps(dt, m_playerMoving);
    }

    // Check book proximity
    m_nearBookIndex = -1;
    for (int i = 0; i < static_cast<int>(m_books.size()); i++) {
        if (m_books[i]->isPlayerNear(m_player.getPosition())) {
            m_nearBookIndex = i;
            break;
        }
    }

    // E to interact with nearby book
    if (m_nearBookIndex >= 0 && input.isKeyPressed(SDL_SCANCODE_E)) {
        m_books[m_nearBookIndex]->open();
        m_activeBook = m_books[m_nearBookIndex].get();
    }

    // Animate rotating props
    for (auto& prop : m_props) {
        if (prop->rotationSpeed != 0.0f) {
            glm::vec3 pos = glm::vec3(prop->transform[3]);
            glm::vec3 scl = glm::vec3(
                glm::length(glm::vec3(prop->transform[0])),
                glm::length(glm::vec3(prop->transform[1])),
                glm::length(glm::vec3(prop->transform[2]))
            );
            float bob = std::sin(m_propTime * 2.0f) * 0.1f;
            glm::mat4 t(1.0f);
            t = glm::translate(t, pos + glm::vec3(0.0f, bob, 0.0f));
            t = glm::rotate(t, m_propTime * prop->rotationSpeed, glm::vec3(0.0f, 1.0f, 0.0f));
            t = glm::scale(t, scl);
            prop->transform = t;
        }
    }

    // Flicker point lights
    for (auto& light : m_pointLights) {
        if (light.flicker) {
            // Subtle random intensity variation
            float flicker = 0.9f + 0.1f * std::sin(m_propTime * 8.0f + light.position.x * 7.0f)
                          + 0.05f * std::sin(m_propTime * 13.0f + light.position.z * 11.0f);
            light.radius = light.radius * flicker / (0.9f + 0.1f); // normalize
        }
    }

    // Check trigger zones
    for (const auto& trigger : m_triggers) {
        float dist = glm::distance(glm::vec2(m_player.getPosition().x, m_player.getPosition().z),
                                    glm::vec2(trigger.position.x, trigger.position.z));
        if (dist < trigger.radius) {
            std::string targetRoom = trigger.targetRoom;
            glm::vec3 spawnPos = trigger.spawnPos;
            m_transition.startTransition(1.5f, [this, targetRoom, spawnPos, &renderer]() {
                loadRoom(targetRoom, renderer);
                m_player.setPosition(spawnPos);
            });
            break;
        }
    }
}

void Scene::renderObjects() {
    m_meshShader.use();
    m_meshShader.setMat4("uView", glm::value_ptr(m_camera.getView()));
    m_meshShader.setMat4("uProjection", glm::value_ptr(m_camera.getProjection()));

    // Directional light
    m_meshShader.setVec3("uAmbient", m_currentRoom.ambientColor.x, m_currentRoom.ambientColor.y, m_currentRoom.ambientColor.z);
    m_meshShader.setVec3("uLightDir", m_currentRoom.lightDir.x, m_currentRoom.lightDir.y, m_currentRoom.lightDir.z);
    m_meshShader.setVec3("uLightColor", m_currentRoom.lightColor.x, m_currentRoom.lightColor.y, m_currentRoom.lightColor.z);

    // Point lights
    int numLights = std::min(static_cast<int>(m_pointLights.size()), 4);
    m_meshShader.setInt("uNumPointLights", numLights);
    for (int i = 0; i < numLights; i++) {
        std::string prefix = "uPointLightPos[" + std::to_string(i) + "]";
        m_meshShader.setVec3(prefix, m_pointLights[i].position.x, m_pointLights[i].position.y, m_pointLights[i].position.z);
        prefix = "uPointLightColor[" + std::to_string(i) + "]";
        m_meshShader.setVec3(prefix, m_pointLights[i].color.x, m_pointLights[i].color.y, m_pointLights[i].color.z);
        prefix = "uPointLightRadius[" + std::to_string(i) + "]";
        m_meshShader.setFloat(prefix, m_pointLights[i].radius);
    }

    // Render props
    for (const auto& prop : m_props) {
        m_meshShader.setMat4("uModel", glm::value_ptr(prop->transform));

        if (prop->model) {
            // GLB model handles its own materials/textures per submesh
            prop->model->draw(m_meshShader);
        } else {
            m_meshShader.setVec3("uMaterialColor", prop->materialColor.x, prop->materialColor.y, prop->materialColor.z);

            bool hasTex = prop->texture.getID() != 0;
            m_meshShader.setInt("uHasTexture", hasTex ? 1 : 0);
            if (hasTex) {
                prop->texture.bind(GL_TEXTURE0);
                m_meshShader.setInt("uDiffuse", 0);
            }

            prop->mesh.draw();
        }
    }

    // Render player
    m_meshShader.setVec3("uMaterialColor", 0.35f, 0.3f, 0.28f);
    m_meshShader.setInt("uHasTexture", 0);
    m_player.render(m_meshShader);
}

void Scene::renderParticles() {
    m_particles.render(m_camera.getView(), m_camera.getProjection());
}

void Scene::renderOverlays() {
    m_transition.render();
}

void Scene::renderUI(UIOverlay& ui, int screenWidth, int screenHeight) {
    // Show interaction prompt when near a book
    if (m_nearBookIndex >= 0 && !m_activeBook) {
        ui.drawPrompt("Press E to read");
    }

    // Render active book viewer
    if (m_activeBook) {
        m_activeBook->renderUI(ui, screenWidth, screenHeight);
    }
}

void Scene::shutdown() {
    m_particles.shutdown();
    m_transition.shutdown();
    m_props.clear();
    m_triggers.clear();
    m_pointLights.clear();
}

} // namespace dw
