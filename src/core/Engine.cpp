#include "core/Engine.h"
#include "core/InputManager.h"
#include "renderer/Renderer.h"
#include "scene/Scene.h"
#include "audio/AudioManager.h"

#include <glad/gl.h>
#include <SDL.h>
#include <iostream>

namespace dw {

Engine::Engine() = default;
Engine::~Engine() = default;

bool Engine::init(const std::string& title, int width, int height) {
    m_windowWidth = width;
    m_windowHeight = height;

    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_AUDIO | SDL_INIT_TIMER) != 0) {
        std::cerr << "SDL_Init failed: " << SDL_GetError() << "\n";
        return false;
    }

    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 3);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE);
    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);
    SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 24);
    SDL_GL_SetAttribute(SDL_GL_STENCIL_SIZE, 8);

    m_window = SDL_CreateWindow(
        title.c_str(),
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
        m_windowWidth, m_windowHeight,
        SDL_WINDOW_OPENGL | SDL_WINDOW_SHOWN | SDL_WINDOW_RESIZABLE
    );

    if (!m_window) {
        std::cerr << "SDL_CreateWindow failed: " << SDL_GetError() << "\n";
        return false;
    }

    m_glContext = SDL_GL_CreateContext(m_window);
    if (!m_glContext) {
        std::cerr << "SDL_GL_CreateContext failed: " << SDL_GetError() << "\n";
        return false;
    }

    int version = gladLoadGL((GLADloadfunc)SDL_GL_GetProcAddress);
    if (version == 0) {
        std::cerr << "Failed to load OpenGL with GLAD\n";
        return false;
    }

    std::cout << "Engine initialized\n";
    std::cout << "  OpenGL: " << glGetString(GL_VERSION) << "\n";
    std::cout << "  GLSL: " << glGetString(GL_SHADING_LANGUAGE_VERSION) << "\n";
    std::cout << "  GPU: " << glGetString(GL_RENDERER) << "\n";

    SDL_GL_SetSwapInterval(1);

    glEnable(GL_DEPTH_TEST);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glClearColor(0.02f, 0.02f, 0.03f, 1.0f);
    glViewport(0, 0, m_windowWidth, m_windowHeight);

    // Input
    m_inputManager = std::make_unique<InputManager>();

    // Audio
    m_audio = std::make_unique<AudioManager>();
    if (!m_audio->init()) {
        std::cerr << "Audio init failed (continuing without audio)\n";
        m_audio.reset();
    } else {
        // Try to load ambient and footstep sounds (graceful if missing)
        m_audio->loadAmbient("assets/audio/ambient_forest.wav");
        m_audio->loadSound("footstep", "assets/audio/footstep.wav");
        m_audio->playAmbient();
    }

    // Renderer
    m_renderer = std::make_unique<Renderer>();
    if (!m_renderer->init(m_windowWidth, m_windowHeight)) {
        std::cerr << "Failed to init renderer\n";
        return false;
    }

    // Scene
    m_scene = std::make_unique<Scene>();
    if (!m_scene->init(*m_renderer)) {
        std::cerr << "Failed to init scene\n";
        return false;
    }

    m_scene->loadRoom("assets/rooms/test_room.json", *m_renderer);

    m_running = true;
    return true;
}

void Engine::run() {
    Uint64 lastTicks = SDL_GetPerformanceCounter();
    Uint64 freq = SDL_GetPerformanceFrequency();

    while (m_running) {
        Uint64 currentTicks = SDL_GetPerformanceCounter();
        m_deltaTime = static_cast<float>(currentTicks - lastTicks) / static_cast<float>(freq);
        lastTicks = currentTicks;

        if (m_deltaTime > 0.1f) m_deltaTime = 0.1f;
        m_totalTime += m_deltaTime;

        m_inputManager->preUpdate();
        processEvents();
        update(m_deltaTime);
        render();

        SDL_GL_SwapWindow(m_window);
    }
}

void Engine::processEvents() {
    SDL_Event event;
    while (SDL_PollEvent(&event)) {
        switch (event.type) {
            case SDL_QUIT:
                m_running = false;
                break;
            case SDL_KEYDOWN:
                m_inputManager->onKeyDown(event.key.keysym.scancode);
                if (event.key.keysym.sym == SDLK_ESCAPE) m_running = false;
                break;
            case SDL_KEYUP:
                m_inputManager->onKeyUp(event.key.keysym.scancode);
                break;
            case SDL_MOUSEMOTION:
                m_inputManager->onMouseMove(event.motion.xrel, event.motion.yrel);
                break;
            case SDL_MOUSEBUTTONDOWN:
                m_inputManager->onMouseDown(event.button.button);
                break;
            case SDL_MOUSEBUTTONUP:
                m_inputManager->onMouseUp(event.button.button);
                break;
            case SDL_WINDOWEVENT:
                if (event.window.event == SDL_WINDOWEVENT_RESIZED) {
                    m_windowWidth = event.window.data1;
                    m_windowHeight = event.window.data2;
                    m_renderer->onResize(m_windowWidth, m_windowHeight);
                }
                break;
        }
    }
}

void Engine::update(float dt) {
    m_scene->update(dt, *m_inputManager, *m_renderer, m_audio.get());
}

void Engine::render() {
    m_renderer->beginFrame();

    // 1. Pre-rendered background
    m_renderer->renderBackground();

    // 2. Real-time 3D objects (props, player)
    m_scene->renderObjects();

    // 3. Particles (fog, dust, fireflies)
    m_scene->renderParticles();

    // 4. Post-processing → screen
    m_renderer->endFrame(m_totalTime);

    // 5. Overlays (room transition fade)
    m_scene->renderOverlays();
}

void Engine::shutdown() {
    if (m_scene) m_scene->shutdown();
    m_scene.reset();
    if (m_renderer) m_renderer->shutdown();
    m_renderer.reset();
    if (m_audio) m_audio->shutdown();
    m_audio.reset();
    m_inputManager.reset();

    if (m_glContext) {
        SDL_GL_DeleteContext(m_glContext);
        m_glContext = nullptr;
    }
    if (m_window) {
        SDL_DestroyWindow(m_window);
        m_window = nullptr;
    }
    SDL_Quit();
    std::cout << "Engine shutdown\n";
}

} // namespace dw
