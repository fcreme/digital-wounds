#include "scene/Scene.h"
#include "renderer/Renderer.h"
#include "renderer/BackgroundLayer.h"
#include "renderer/ShadowMap.h"
#include "core/InputManager.h"
#include "audio/AudioManager.h"
#include "ui/UIOverlay.h"

#include <SDL.h>
#include <glad/gl.h>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <iostream>
#include <cmath>
#include <random>
#include <vector>
#include <algorithm>

namespace dw {

namespace {
ParticleType parseParticleType(const std::string& s) {
    if (s == "fog") return ParticleType::Fog;
    if (s == "fireflies") return ParticleType::Fireflies;
    if (s == "fire") return ParticleType::Fire;
    return ParticleType::Dust;
}
} // anonymous namespace

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
    m_fmvOverlays.clear();
    m_books.clear();
    m_nearBookIndex = -1;
    m_activeBook = nullptr;
    m_worldItems.clear();
    m_nearItemIndex = -1;
    m_depthGeometry.reset();

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

    // Load props from room definition (handles model files, cubes, and planes)
    for (const auto& propDef : m_currentRoom.props) {
        auto prop = std::make_unique<PropInstance>();

        if (propDef.meshType == "cube") {
            prop->mesh = Mesh::createCube(propDef.meshSize.x);
        } else if (propDef.meshType == "plane") {
            prop->mesh = Mesh::createPlane(propDef.meshSize.x, propDef.meshSize.y);
        } else if (!propDef.modelPath.empty()) {
            prop->model = std::make_unique<Model>();
            if (!prop->model->load(propDef.modelPath)) {
                std::cerr << "Scene: failed to load model: " << propDef.modelPath << "\n";
                continue;
            }
        }

        if (!propDef.texturePath.empty()) prop->texture.load(propDef.texturePath);

        // Procedural art texture
        if (propDef.proceduralArtSeed >= 0) {
            GLuint artTex = generateProceduralArt(propDef.proceduralArtSeed, 256, 256);
            prop->texture.setID(artTex);
        }

        glm::mat4 t(1.0f);
        t = glm::translate(t, propDef.position);
        t = glm::rotate(t, glm::radians(propDef.rotation.y), glm::vec3(0, 1, 0));
        t = glm::rotate(t, glm::radians(propDef.rotation.x), glm::vec3(1, 0, 0));
        t = glm::rotate(t, glm::radians(propDef.rotation.z), glm::vec3(0, 0, 1));
        t = glm::scale(t, propDef.scale);
        prop->transform = t;

        prop->materialColor = propDef.color;
        prop->roughness = propDef.roughness;
        prop->emissive = propDef.emissive;
        prop->rotationSpeed = propDef.rotationSpeed;
        prop->bookIndex = propDef.bookIndex;
        prop->itemIndex = propDef.itemIndex;

        m_props.push_back(std::move(prop));
    }

    // Load point lights from room definition
    for (const auto& pl : m_currentRoom.pointLights) {
        m_pointLights.push_back(pl);
    }

    // Load trigger zones from room definition
    for (const auto& td : m_currentRoom.triggers) {
        TriggerZone tz;
        tz.position = td.position;
        tz.radius = td.radius;
        tz.targetRoom = td.targetRoom;
        tz.spawnPos = td.spawnPos;
        tz.requiresItem = td.requiresItem;
        tz.lockedMessage = td.lockedMessage;
        tz.consumeItem = td.consumeItem;
        m_triggers.push_back(tz);
    }

    // Load books from room definition
    for (const auto& bd : m_currentRoom.books) {
        auto b = std::make_unique<Book>();
        b->init(bd.position, bd.interactRadius);
        for (const auto& page : bd.pages) {
            b->addPage(page);
        }
        m_books.push_back(std::move(b));
    }

    // Load items from room definition (skip items already in inventory)
    for (int idx = 0; idx < static_cast<int>(m_currentRoom.items.size()); idx++) {
        const auto& idef = m_currentRoom.items[idx];
        auto item = std::make_unique<WorldItem>();
        item->init(idef.id, idef.name, idef.description, idef.iconPath,
                   idef.position, idef.interactRadius);
        bool alreadyOwned = m_inventory.hasItem(idef.id);
        if (alreadyOwned) {
            item->setGone();
        }
        m_worldItems.push_back(std::move(item));

        // Create a floating cube prop for the item (visible in-world)
        if (!alreadyOwned) {
            auto prop = std::make_unique<PropInstance>();
            prop->mesh = Mesh::createCube(0.15f);
            glm::mat4 t(1.0f);
            t = glm::translate(t, idef.position);
            t = glm::scale(t, glm::vec3(0.15f));
            prop->transform = t;
            prop->materialColor = glm::vec3(0.8f, 0.6f, 0.2f);
            prop->emissive = glm::vec3(0.4f, 0.3f, 0.1f);
            prop->roughness = 0.3f;
            prop->rotationSpeed = 2.0f;
            prop->itemIndex = idx;
            m_props.push_back(std::move(prop));
        }
    }

    // Set fog params from room definition
    if (m_currentRoom.fogParams.defined) {
        renderer.getPostProcess().setFogParams(
            m_currentRoom.fogParams.color,
            m_currentRoom.fogParams.density,
            m_currentRoom.fogParams.maxDistance,
            m_currentRoom.fogParams.near,
            m_currentRoom.fogParams.far);
    }

    // Spawn particle emitters from room JSON
    for (const auto& pdef : m_currentRoom.particles) {
        ParticleEmitter e;
        e.type = parseParticleType(pdef.type);
        e.origin = pdef.origin;
        e.area = pdef.area;
        e.count = pdef.count;
        e.color = pdef.color;
        e.speed = pdef.speed;
        e.baseSize = pdef.baseSize;
        m_particles.addEmitter(e);
    }

    // Spawn FMV overlays from room JSON
    FMVOverlay::initShared();
    for (const auto& fdef : m_currentRoom.fmvOverlays) {
        FMVOverlay overlay;
        overlay.loadFromDef(fdef);
        m_fmvOverlays.push_back(std::move(overlay));
    }

    // Set player world bounds and collision boxes from room definition
    m_player.setWorldBounds(m_currentRoom.boundsMinX, m_currentRoom.boundsMaxX,
                            m_currentRoom.boundsMinZ, m_currentRoom.boundsMaxZ);
    m_player.setCollisionBoxes(m_currentRoom.collisionBoxes);

    // Load depth pre-pass geometry (hidden geometry for occlusion)
    if (!m_currentRoom.depthGeometryPath.empty()) {
        m_depthGeometry = std::make_unique<Model>();
        if (!m_depthGeometry->load(m_currentRoom.depthGeometryPath)) {
            std::cerr << "Scene: failed to load depth geometry: " << m_currentRoom.depthGeometryPath << "\n";
            m_depthGeometry.reset();
        }
    }

    // Set mouse mode based on first-person flag
    SDL_SetRelativeMouseMode(m_currentRoom.firstPerson ? SDL_TRUE : SDL_FALSE);

    // Load room-specific ambient audio
    if (m_audio && !m_currentRoom.ambientAudioPath.empty()) {
        m_audio->stopAmbient();
        m_audio->loadAmbient(m_currentRoom.ambientAudioPath);
        m_audio->playAmbient();
    }

    // Set reverb from room definition (once per room load, not per frame)
    if (m_audio) {
        m_audio->setReverb(m_currentRoom.reverb.enabled,
                           m_currentRoom.reverb.feedback,
                           m_currentRoom.reverb.delayMs);
    }

    std::cout << "Scene: room '" << m_currentRoom.name << "' loaded — "
              << m_props.size() << " props, " << m_pointLights.size() << " lights, "
              << m_triggers.size() << " triggers, " << m_books.size() << " books, "
              << m_worldItems.size() << " items, "
              << m_fmvOverlays.size() << " FMV overlays"
              << (m_currentRoom.firstPerson ? " [FP]" : " [Fixed]") << "\n";
    return true;
}

void Scene::update(float dt, const InputManager& input, Renderer& renderer, AudioManager* audio, UIOverlay* /*ui*/) {
    m_audio = audio;  // cache for use in loadRoom (called from transitions)

    m_transition.update(dt);
    if (m_transition.isActive()) return;

    // If inventory is open, only update inventory (block player movement)
    if (m_inventory.isOpen()) {
        m_inventory.update(dt, input);
        // Tab to close is handled inside inventory, but also check here
        if (input.isKeyPressed(SDL_SCANCODE_TAB)) {
            m_inventory.toggle();
        }
        return;
    }

    // If a book is open, only update the book (block player movement)
    if (m_activeBook) {
        m_activeBook->update(dt, input);
        if (!m_activeBook->isOpen()) {
            m_activeBook = nullptr;
        }
        return;
    }

    // Tab to open inventory
    if (input.isKeyPressed(SDL_SCANCODE_TAB)) {
        m_inventory.toggle();
        return;
    }

    glm::vec3 prevPos = m_player.getPosition();
    m_player.update(dt, input, m_camera);
    m_playerMoving = glm::distance(prevPos, m_player.getPosition()) > 0.001f;

    // Update camera shake before camera setup
    m_camera.updateShake(dt);

    // Camera update: FP or fixed
    if (m_currentRoom.firstPerson) {
        float eyeHeight = m_currentRoom.eyeHeight + m_player.getHeadBob();
        m_camera.updateFromPlayer(m_player.getPosition(), eyeHeight,
                                  m_player.getSmoothYaw(), m_player.getSmoothPitch());
    }
    // else: camera stays as set from room def (fixed)

    m_propTime += dt;
    m_particles.update(dt);
    for (auto& overlay : m_fmvOverlays) overlay.update(dt);

    // Audio: footsteps, reverb, listener position
    if (audio) {
        audio->updateFootsteps(dt, m_playerMoving);

        // Update listener for spatial audio
        glm::vec3 lookDir = m_player.getLookDirection();
        glm::vec3 rightDir = glm::normalize(glm::cross(lookDir, glm::vec3(0, 1, 0)));
        audio->setListenerPos(m_camera.getPosition(), lookDir, rightDir);
    }

    // Check book proximity / look-at
    m_nearBookIndex = -1;
    glm::vec3 camPos = m_camera.getPosition();
    glm::vec3 lookDir = m_player.getLookDirection();

    for (int i = 0; i < static_cast<int>(m_books.size()); i++) {
        if (!m_books[i]->isPlayerNear(m_player.getPosition())) continue;

        if (m_currentRoom.firstPerson) {
            // FP mode: must also be looking at the book
            glm::vec3 toBook = glm::normalize(m_books[i]->getPosition() - camPos);
            float dotAngle = glm::dot(lookDir, toBook);
            // cos(30 deg) ~= 0.866
            if (dotAngle > 0.866f) {
                m_nearBookIndex = i;
                break;
            }
        } else {
            // Fixed-cam: proximity only
            m_nearBookIndex = i;
            break;
        }
    }

    // Check item proximity / look-at
    m_nearItemIndex = -1;
    for (int i = 0; i < static_cast<int>(m_worldItems.size()); i++) {
        if (!m_worldItems[i]->isIdle()) continue;
        if (!m_worldItems[i]->isPlayerNear(m_player.getPosition())) continue;

        if (m_currentRoom.firstPerson) {
            glm::vec3 toItem = glm::normalize(m_worldItems[i]->getPosition() - camPos);
            float dotAngle = glm::dot(lookDir, toItem);
            if (dotAngle > 0.866f) {
                m_nearItemIndex = i;
                break;
            }
        } else {
            m_nearItemIndex = i;
            break;
        }
    }

    // Smooth highlight animation
    float targetHighlight = (m_nearBookIndex >= 0 || m_nearItemIndex >= 0) ? 1.0f : 0.0f;
    m_highlightAmount += (targetHighlight - m_highlightAmount) * std::min(dt * 8.0f, 1.0f);

    // E to interact with nearby item (priority over book)
    if (m_nearItemIndex >= 0 && input.isKeyPressed(SDL_SCANCODE_E)) {
        auto& item = m_worldItems[m_nearItemIndex];
        item->pickUp();
        m_inventory.addItem(item->getId(), item->getName(),
                           item->getDescription(), item->getIconPath());
        m_pickupMessage = "Picked up: " + item->getName();
        m_pickupMessageTimer = 2.0f;
        m_pickupFlashTimer = 0.3f;
        m_particles.spawnBurst(item->getPosition(), 20, ParticleType::Sparkle);
        if (m_audio) {
            m_audio->playSound("pickup", 0.6f);
        }
    }
    // E to interact with nearby book (with lock check)
    else if (m_nearBookIndex >= 0 && input.isKeyPressed(SDL_SCANCODE_E)) {
        const auto& bookDef = m_currentRoom.books[m_nearBookIndex];
        if (!bookDef.requiresItem.empty() && !m_inventory.hasItem(bookDef.requiresItem)) {
            m_lockedMessage = bookDef.lockedMessage;
            m_lockedMessageTimer = 2.0f;
            m_camera.shake(0.05f, 0.2f);
        } else {
            if (!bookDef.requiresItem.empty() && bookDef.consumeItem) {
                m_inventory.removeItem(bookDef.requiresItem);
            }
            m_books[m_nearBookIndex]->open();
            m_activeBook = m_books[m_nearBookIndex].get();
        }
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
            float flicker = 0.9f + 0.1f * std::sin(m_propTime * 8.0f + light.position.x * 7.0f)
                          + 0.05f * std::sin(m_propTime * 13.0f + light.position.z * 11.0f);
            light.radius = light.baseRadius * flicker;
        }
    }

    // Update world items (pickup animation)
    for (auto& item : m_worldItems) {
        item->update(dt);
    }

    // Decrement message timers
    if (m_lockedMessageTimer > 0.0f) m_lockedMessageTimer -= dt;
    if (m_pickupMessageTimer > 0.0f) m_pickupMessageTimer -= dt;
    if (m_pickupFlashTimer > 0.0f) m_pickupFlashTimer -= dt;

    // After a room load, wait until player leaves all trigger zones before re-arming
    if (m_triggerCooldown > 0.0f) {
        bool insideAny = false;
        for (const auto& trigger : m_triggers) {
            float dist = glm::distance(glm::vec2(m_player.getPosition().x, m_player.getPosition().z),
                                        glm::vec2(trigger.position.x, trigger.position.z));
            if (dist < trigger.radius) {
                insideAny = true;
                break;
            }
        }
        if (!insideAny) {
            m_triggerCooldown = 0.0f;
        }
        return;
    }

    // Check trigger zones
    for (const auto& trigger : m_triggers) {
        float dist = glm::distance(glm::vec2(m_player.getPosition().x, m_player.getPosition().z),
                                    glm::vec2(trigger.position.x, trigger.position.z));
        if (dist < trigger.radius) {
            // Check if trigger requires an item
            if (!trigger.requiresItem.empty() && !m_inventory.hasItem(trigger.requiresItem)) {
                m_lockedMessage = trigger.lockedMessage;
                m_lockedMessageTimer = 2.0f;
                m_triggerCooldown = 1.0f;  // prevent spamming the message
                m_camera.shake(0.08f, 0.3f);
                break;
            }

            // Consume item if needed
            if (!trigger.requiresItem.empty() && trigger.consumeItem) {
                m_inventory.removeItem(trigger.requiresItem);
            }

            std::string targetRoom = trigger.targetRoom;
            glm::vec3 spawnPos = trigger.spawnPos;
            m_transition.startTransition(1.5f, [this, targetRoom, spawnPos, &renderer]() {
                loadRoom(targetRoom, renderer);
                m_player.setPosition(spawnPos);
                m_triggerCooldown = 1.0f;
            });
            break;
        }
    }
}

void Scene::renderObjects() {
    m_meshShader.use();
    m_meshShader.setMat4("uView", glm::value_ptr(m_camera.getView()));
    m_meshShader.setMat4("uProjection", glm::value_ptr(m_camera.getProjection()));

    // Camera position for specular
    glm::vec3 camPos = m_camera.getPosition();
    m_meshShader.setVec3("uViewPos", camPos.x, camPos.y, camPos.z);

    // Directional light
    m_meshShader.setVec3("uAmbient", m_currentRoom.ambientColor.x, m_currentRoom.ambientColor.y, m_currentRoom.ambientColor.z);
    m_meshShader.setVec3("uLightDir", m_currentRoom.lightDir.x, m_currentRoom.lightDir.y, m_currentRoom.lightDir.z);
    m_meshShader.setVec3("uLightColor", m_currentRoom.lightColor.x, m_currentRoom.lightColor.y, m_currentRoom.lightColor.z);

    // Point lights
    int numLights = std::min(static_cast<int>(m_pointLights.size()), 8);
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
        // Skip item props that are already picked up (Gone)
        if (prop->itemIndex >= 0 && prop->itemIndex < static_cast<int>(m_worldItems.size())) {
            if (m_worldItems[prop->itemIndex]->isGone()) continue;
        }

        // During pickup animation, scale the item prop down
        glm::mat4 drawTransform = prop->transform;
        if (prop->itemIndex >= 0 && prop->itemIndex < static_cast<int>(m_worldItems.size())) {
            float progress = m_worldItems[prop->itemIndex]->getPickupProgress();
            if (progress > 0.0f) {
                float shrink = 1.0f - progress;
                glm::vec3 pos = glm::vec3(drawTransform[3]);
                drawTransform = glm::translate(glm::mat4(1.0f), pos);
                drawTransform = glm::scale(drawTransform, glm::vec3(0.15f * shrink));
            }
        }

        m_meshShader.setMat4("uModel", glm::value_ptr(drawTransform));
        glm::mat3 normalMatrix = glm::transpose(glm::inverse(glm::mat3(prop->transform)));
        m_meshShader.setMat3("uNormalMatrix", glm::value_ptr(normalMatrix));

        // Highlight for book-linked or item-linked props
        float highlight = 0.0f;
        if (prop->bookIndex >= 0 && prop->bookIndex == m_nearBookIndex) highlight = m_highlightAmount;
        if (prop->itemIndex >= 0 && prop->itemIndex == m_nearItemIndex) highlight = m_highlightAmount;
        m_meshShader.setFloat("uHighlight", highlight);

        m_meshShader.setFloat("uRoughness", prop->roughness);

        if (prop->model) {
            glDisable(GL_CULL_FACE);
            prop->model->draw(m_meshShader);
            glEnable(GL_CULL_FACE);
        } else {
            m_meshShader.setVec3("uMaterialColor", prop->materialColor.x, prop->materialColor.y, prop->materialColor.z);
            m_meshShader.setVec3("uEmissive", prop->emissive.x, prop->emissive.y, prop->emissive.z);
            m_meshShader.setInt("uHasNormalMap", 0);

            bool hasTex = prop->texture.getID() != 0;
            m_meshShader.setInt("uHasTexture", hasTex ? 1 : 0);
            if (hasTex) {
                prop->texture.bind(GL_TEXTURE0);
                m_meshShader.setInt("uDiffuse", 0);
            }

            prop->mesh.draw();
        }
    }

    // Render player cube only in fixed-camera rooms
    if (!m_currentRoom.firstPerson) {
        m_meshShader.setVec3("uMaterialColor", 0.6f, 0.3f, 0.2f);
        m_meshShader.setInt("uHasTexture", 0);
        m_meshShader.setVec3("uEmissive", 0.0f, 0.0f, 0.0f);
        m_meshShader.setInt("uHasNormalMap", 0);
        m_player.render(m_meshShader);
    }
}

void Scene::renderFMVOverlays() {
    if (m_fmvOverlays.empty()) return;

    glDisable(GL_DEPTH_TEST);
    for (auto& overlay : m_fmvOverlays) {
        overlay.render();
    }
    glEnable(GL_DEPTH_TEST);
}

void Scene::renderParticles() {
    m_particles.render(m_camera.getView(), m_camera.getProjection());
}

void Scene::renderOverlays() {
    m_transition.render();
}

void Scene::renderUI(UIOverlay& ui, int screenWidth, int screenHeight) {
    // Pickup flash effect (white overlay fading out)
    if (m_pickupFlashTimer > 0.0f) {
        float alpha = m_pickupFlashTimer * 0.5f;  // max 0.15 at start (0.3 * 0.5)
        ui.drawRect(0.0f, 0.0f, static_cast<float>(screenWidth), static_cast<float>(screenHeight),
                    glm::vec4(1.0f, 1.0f, 1.0f, alpha));
    }

    // Render inventory UI (on top of everything when open)
    if (m_inventory.isOpen()) {
        m_inventory.renderUI(ui, screenWidth, screenHeight);
        return;
    }

    // Crosshair in FP mode (only when no book open)
    if (m_currentRoom.firstPerson && !m_activeBook) {
        ui.drawCrosshair();
    }

    // Show interaction prompt when looking at an item
    if (m_nearItemIndex >= 0 && !m_activeBook) {
        ui.drawPrompt("Press E to pick up");
    }
    // Show interaction prompt when looking at a book
    else if (m_nearBookIndex >= 0 && !m_activeBook) {
        ui.drawPrompt("Press E to read");
    }

    // Render active book viewer
    if (m_activeBook) {
        m_activeBook->renderUI(ui, screenWidth, screenHeight);
    }

    // Locked message (red, centered, fading)
    if (m_lockedMessageTimer > 0.0f && !m_lockedMessage.empty()) {
        float alpha = std::min(m_lockedMessageTimer, 1.0f);
        float textScale = 2.5f;
        float textW = m_lockedMessage.length() * 8.0f * textScale;
        float textX = (screenWidth - textW) * 0.5f;
        float textY = screenHeight * 0.4f;
        ui.drawText(m_lockedMessage, textX, textY, textScale,
                    glm::vec4(0.9f, 0.2f, 0.15f, alpha));
    }

    // Pickup notification (white, top-center, fading)
    if (m_pickupMessageTimer > 0.0f && !m_pickupMessage.empty()) {
        float alpha = std::min(m_pickupMessageTimer, 1.0f);
        float textScale = 2.0f;
        float textW = m_pickupMessage.length() * 8.0f * textScale;
        float textX = (screenWidth - textW) * 0.5f;
        float textY = screenHeight * 0.15f;
        ui.drawText(m_pickupMessage, textX, textY, textScale,
                    glm::vec4(0.9f, 0.85f, 0.7f, alpha));
    }
}

void Scene::renderShadowCasters(Shader& shadowShader) {
    // Render all props into shadow map
    for (const auto& prop : m_props) {
        shadowShader.setMat4("uModel", glm::value_ptr(prop->transform));
        if (prop->model) {
            prop->model->draw(shadowShader);
        } else {
            prop->mesh.draw();
        }
    }

    // Render player shadow only in fixed-camera mode
    if (!m_currentRoom.firstPerson) {
        m_player.render(shadowShader);
    }
}

void Scene::renderDepthGeometry(Shader& depthShader, Camera& camera) {
    if (!m_depthGeometry) return;

    depthShader.use();
    depthShader.setMat4("uView", glm::value_ptr(camera.getView()));
    depthShader.setMat4("uProjection", glm::value_ptr(camera.getProjection()));

    // Write depth only, no color
    glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE);

    glm::mat4 identity(1.0f);
    depthShader.setMat4("uModel", glm::value_ptr(identity));
    m_depthGeometry->draw(depthShader);

    glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE);
}

void Scene::bindShadowUniforms(ShadowMap& shadowMap) {
    m_meshShader.use();

    // Bind shadow map to texture unit 1
    shadowMap.bind(GL_TEXTURE1);
    m_meshShader.setInt("uShadowMap", 1);
    m_meshShader.setMat4("uLightSpaceMatrix",
                         glm::value_ptr(shadowMap.getLightSpaceMatrix()));
    m_meshShader.setInt("uUseShadows", 1);
}

GLuint Scene::generateProceduralArt(int seed, int width, int height) {
    std::mt19937 gen(seed);
    std::uniform_real_distribution<float> dist(0.0f, 1.0f);

    std::vector<unsigned char> pixels(width * height * 3);

    // Choose a color palette based on seed
    float hue = dist(gen);
    float baseR = 0.05f + hue * 0.15f;
    float baseG = 0.03f + (1.0f - hue) * 0.1f;
    float baseB = 0.08f + dist(gen) * 0.12f;

    // Generate abstract pattern: layered circles and gradients
    float cx1 = dist(gen), cy1 = dist(gen);
    float cx2 = dist(gen), cy2 = dist(gen);
    float cx3 = dist(gen), cy3 = dist(gen);

    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            float u = static_cast<float>(x) / width;
            float v = static_cast<float>(y) / height;

            float d1 = std::sqrt((u - cx1) * (u - cx1) + (v - cy1) * (v - cy1));
            float d2 = std::sqrt((u - cx2) * (u - cx2) + (v - cy2) * (v - cy2));
            float d3 = std::sqrt((u - cx3) * (u - cx3) + (v - cy3) * (v - cy3));

            float pattern = std::sin(d1 * 12.0f) * 0.3f
                          + std::cos(d2 * 8.0f + d1 * 4.0f) * 0.25f
                          + std::sin(d3 * 15.0f) * 0.2f;

            // Add noise
            pattern += (dist(gen) - 0.5f) * 0.1f;

            float r = std::clamp(baseR + pattern * 0.4f + d1 * 0.3f, 0.0f, 1.0f);
            float g = std::clamp(baseG + pattern * 0.3f + d2 * 0.2f, 0.0f, 1.0f);
            float b = std::clamp(baseB + pattern * 0.35f + d3 * 0.25f, 0.0f, 1.0f);

            // Dark border (frame edge)
            float border = std::min(std::min(u, v), std::min(1.0f - u, 1.0f - v));
            float borderFade = std::clamp(border * 15.0f, 0.0f, 1.0f);
            r *= borderFade;
            g *= borderFade;
            b *= borderFade;

            int idx = (y * width + x) * 3;
            pixels[idx + 0] = static_cast<unsigned char>(r * 255);
            pixels[idx + 1] = static_cast<unsigned char>(g * 255);
            pixels[idx + 2] = static_cast<unsigned char>(b * 255);
        }
    }

    GLuint tex;
    glGenTextures(1, &tex);
    glBindTexture(GL_TEXTURE_2D, tex);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, pixels.data());
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);

    return tex;
}

void Scene::shutdown() {
    m_particles.shutdown();
    m_fmvOverlays.clear();
    FMVOverlay::shutdownShared();
    m_transition.shutdown();
    m_props.clear();
    m_triggers.clear();
    m_pointLights.clear();
    m_worldItems.clear();
}

} // namespace dw
