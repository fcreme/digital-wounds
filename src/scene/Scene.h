#pragma once

#include "core/GameSettings.h"
#include "scene/Room.h"
#include "scene/RoomTransition.h"
#include "fx/PostProcess.h"
#include "renderer/Camera.h"
#include "renderer/Mesh.h"
#include "renderer/Texture.h"
#include "renderer/Shader.h"
#include "renderer/Model.h"
#include "fx/ParticleSystem.h"
#include "fx/FMVOverlay.h"
#include "world/Player.h"
#include "world/Book.h"
#include "world/Item.h"
#include "world/Inventory.h"
#include "world/ArtistCatalog.h"
#include "world/PaintingData.h"
#include "world/PaintingWall.h"

#include <string>
#include <memory>
#include <vector>

namespace dw {

class Renderer;
class InputManager;
class AudioManager;
class UIOverlay;
class ShadowMap;

struct TriggerZone {
    glm::vec3 position{0.0f};
    float radius = 1.0f;
    std::string targetRoom;
    glm::vec3 spawnPos{0.0f};
    std::string requiresItem;
    std::string lockedMessage;
    bool consumeItem = false;
};

class Scene {
public:
    Scene();
    ~Scene();

    bool init(Renderer& renderer);
    bool loadRoom(const std::string& roomDefPath, Renderer& renderer);
    void update(float dt, const InputManager& input, Renderer& renderer, AudioManager* audio, UIOverlay* ui);
    void renderObjects();
    void renderFMVOverlays();
    void renderParticles();
    void renderOverlays();
    void renderUI(UIOverlay& ui, int screenWidth, int screenHeight);
    void shutdown();

    // Shadow/depth pass support
    void renderShadowCasters(Shader& shadowShader);
    void renderDepthGeometry(Shader& depthShader, Camera& camera);
    void bindShadowUniforms(ShadowMap& shadowMap);

    Camera& getCamera() { return m_camera; }
    // Keeps the room camera correct after the window or display changes.
    void onResize(int drawableWidth, int drawableHeight) {
        if (drawableWidth <= 0 || drawableHeight <= 0) return;  // minimized
        m_camera.setAspect(static_cast<float>(drawableWidth) / static_cast<float>(drawableHeight));
        m_transition.onResize(drawableWidth, drawableHeight);
    }
    Player& getPlayer() { return m_player; }
    ParticleSystem& getParticleSystem() { return m_particles; }
    const RoomDef& getCurrentRoom() const { return m_currentRoom; }
    void setAudioManager(AudioManager* audio) { m_audio = audio; }
    void setSettings(const GameSettings& s);
    bool wantsQuit() const { return m_wantsQuit; }
    bool isPaused() const { return m_paused; }

private:
    RoomDef m_currentRoom;
    Camera m_camera;
    Shader m_meshShader;
    Player m_player;
    RoomTransition m_transition;
    ParticleSystem m_particles;
    std::vector<FMVOverlay> m_fmvOverlays;

    struct PropInstance {
        Mesh mesh;
        Texture texture;
        std::unique_ptr<Model> model;  // GLB model (used instead of mesh+texture when set)
        glm::mat4 transform{1.0f};
        float rotationSpeed = 0.0f;
        glm::vec3 materialColor{0.5f, 0.5f, 0.5f};
        float roughness = 0.7f;  // 0 = mirror, 1 = matte
        glm::vec3 emissive{0.0f};
        int bookIndex = -1;  // if this prop represents a book, link to m_books index
        int itemIndex = -1;  // if this prop represents an item, link to m_worldItems index
    };
    std::vector<std::unique_ptr<PropInstance>> m_props;
    std::vector<TriggerZone> m_triggers;
    std::vector<PointLightDef> m_pointLights;

    // Framed artist paintings (only rooms with a "paintings" field)
    ArtistCatalog m_catalog;
    std::vector<Painting> m_paintings;
    PaintingWall m_paintingWall;

    // Depth pre-pass hidden geometry
    std::unique_ptr<Model> m_depthGeometry;

    std::vector<std::unique_ptr<Book>> m_books;
    int m_nearBookIndex = -1;  // index of book player is near, -1 if none
    Book* m_activeBook = nullptr;  // currently open book

    // Items and inventory
    std::vector<std::unique_ptr<WorldItem>> m_worldItems;
    int m_nearItemIndex = -1;
    Inventory m_inventory;
    std::string m_lockedMessage;
    float m_lockedMessageTimer = 0.0f;
    std::string m_pickupMessage;
    float m_pickupMessageTimer = 0.0f;
    float m_pickupFlashTimer = 0.0f;

    // Post-process lerp during room transitions
    PostProcessParams m_ppFrom;
    PostProcessParams m_ppTo;
    FogParamsDef m_fogFrom;
    FogParamsDef m_fogTo;
    bool m_ppLerping = false;
    Renderer* m_rendererCache = nullptr;  // cached for lerp application during update

    float m_propTime = 0.0f;
    bool m_playerMoving = false;
    float m_triggerCooldown = 0.0f;
    float m_highlightAmount = 0.0f;  // 0..1 smooth highlight for looked-at book/item

    AudioManager* m_audio = nullptr;  // non-owning, set during update

    // Pause menu
    enum class PauseScreen { Main, Settings };
    bool m_paused = false;
    bool m_wantsQuit = false;
    PauseScreen m_pauseScreen = PauseScreen::Main;
    int m_pauseSelection = 0;   // 0 = Resume, 1 = Settings, 2 = Quit
    float m_pauseAlpha = 0.0f;  // fade-in animation

    // Settings
    GameSettings m_settings;
    int m_settingsSelection = 0; // 0..5 (5 controls + Back)
    float m_settingsAdjustTimer = 0.0f;
    void applySettings();

    // Procedural texture generation
    static GLuint generateProceduralArt(int seed, int width, int height);
};

} // namespace dw
