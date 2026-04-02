#pragma once

#include <SDL.h>
#include <string>
#include <memory>

namespace dw {

class Renderer;
class InputManager;
class Scene;
class AudioManager;

class Engine {
public:
    Engine();
    ~Engine();

    Engine(const Engine&) = delete;
    Engine& operator=(const Engine&) = delete;

    bool init(const std::string& title, int width, int height);
    void run();
    void shutdown();

    float getDeltaTime() const { return m_deltaTime; }
    int getWindowWidth() const { return m_windowWidth; }
    int getWindowHeight() const { return m_windowHeight; }

private:
    void processEvents();
    void update(float dt);
    void render();

    SDL_Window* m_window = nullptr;
    SDL_GLContext m_glContext = nullptr;

    std::unique_ptr<Renderer> m_renderer;
    std::unique_ptr<InputManager> m_inputManager;
    std::unique_ptr<Scene> m_scene;
    std::unique_ptr<AudioManager> m_audio;

    int m_windowWidth = 1280;
    int m_windowHeight = 720;

    bool m_running = false;
    float m_deltaTime = 0.0f;
    float m_totalTime = 0.0f;
};

} // namespace dw
