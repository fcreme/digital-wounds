#pragma once

#include "fx/ParticleSystem.h"
#include "renderer/Camera.h"
#include <memory>

namespace dw {

class UIOverlay;
class InputManager;

class TitleScreen {
public:
    TitleScreen() = default;
    ~TitleScreen() = default;

    bool init(int screenWidth, int screenHeight);
    void update(float dt, const InputManager& input);
    void render(UIOverlay& ui, int screenWidth, int screenHeight);
    void onResize(int width, int height);
    void shutdown();

    bool isFinished() const { return m_finished; }

private:
    ParticleSystem m_particles;
    Camera m_camera;

    float m_time = 0.0f;
    bool m_fadeOut = false;
    float m_fadeAlpha = 0.0f;
    bool m_finished = false;

    int m_screenWidth = 1280;
    int m_screenHeight = 720;
};

} // namespace dw
