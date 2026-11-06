#pragma once

#include "core/GameSettings.h"

#include <SDL.h>
#include <string>
#include <memory>

namespace dw {

class Renderer;
class InputManager;
class Scene;
class AudioManager;
class UIOverlay;
class TitleScreen;
class TestDriver;

enum class GameState {
    TitleScreen,
    Playing
};

class Engine {
public:
    Engine();
    ~Engine();

    Engine(const Engine&) = delete;
    Engine& operator=(const Engine&) = delete;

    bool init(const std::string& title, int width, int height);
    // Path of a test-driver script; only honoured in DW_TEST_DRIVER builds.
    void setScriptPath(const std::string& path) { m_scriptPath = path; }
    void run();
    void shutdown();

    float getDeltaTime() const { return m_deltaTime; }
    int getWindowWidth() const { return m_windowWidth; }
    int getWindowHeight() const { return m_windowHeight; }

private:
#ifdef DW_TEST_DRIVER
    friend class TestDriver;
#endif
    void processEvents();
    void update(float dt);
    void render();
    void renderTitleScreen();
    void startGame();

    SDL_Window* m_window = nullptr;
    SDL_GLContext m_glContext = nullptr;

    std::unique_ptr<Renderer> m_renderer;
    std::unique_ptr<InputManager> m_inputManager;
    std::unique_ptr<Scene> m_scene;
    std::unique_ptr<AudioManager> m_audio;
    std::unique_ptr<UIOverlay> m_ui;
    std::unique_ptr<TitleScreen> m_titleScreen;

    GameState m_gameState = GameState::TitleScreen;

    int m_windowWidth = 1280;
    int m_windowHeight = 720;

    bool m_running = false;
    float m_deltaTime = 0.0f;
    float m_totalTime = 0.0f;

    GameSettings m_settings;

    std::string m_scriptPath;
#ifdef DW_TEST_DRIVER
    std::unique_ptr<TestDriver> m_driver;
#endif
};

} // namespace dw
