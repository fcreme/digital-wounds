#pragma once

#include "renderer/BackgroundLayer.h"
#include "renderer/Shader.h"
#include "fx/PostProcess.h"

namespace dw {

class Renderer {
public:
    Renderer() = default;
    ~Renderer() = default;

    Renderer(const Renderer&) = delete;
    Renderer& operator=(const Renderer&) = delete;

    bool init(int windowWidth, int windowHeight);
    void beginFrame();
    void renderBackground();
    void endFrame(float time);
    void onResize(int width, int height);
    void shutdown();

    int getWidth() const { return m_windowWidth; }
    int getHeight() const { return m_windowHeight; }

    BackgroundLayer& getBackgroundLayer() { return m_backgroundLayer; }
    PostProcess& getPostProcess() { return m_postProcess; }

private:
    BackgroundLayer m_backgroundLayer;
    PostProcess m_postProcess;
    int m_windowWidth = 1280;
    int m_windowHeight = 720;
};

} // namespace dw
