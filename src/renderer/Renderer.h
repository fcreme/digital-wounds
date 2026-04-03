#pragma once

#include "renderer/BackgroundLayer.h"
#include "renderer/Shader.h"
#include "renderer/ShadowMap.h"
#include "fx/PostProcess.h"
#include <glm/glm.hpp>

namespace dw {

class Scene;
class Camera;

class Renderer {
public:
    Renderer() = default;
    ~Renderer() = default;

    Renderer(const Renderer&) = delete;
    Renderer& operator=(const Renderer&) = delete;

    bool init(int windowWidth, int windowHeight);
    void beginFrame();
    void renderBackground();
    void renderShadowPass(Scene& scene, const glm::vec3& lightDir);
    void renderDepthPrePass(Scene& scene, Camera& camera);
    void endFrame(float time, const glm::mat4& projection);
    void onResize(int width, int height);
    void shutdown();

    int getWidth() const { return m_windowWidth; }
    int getHeight() const { return m_windowHeight; }

    BackgroundLayer& getBackgroundLayer() { return m_backgroundLayer; }
    PostProcess& getPostProcess() { return m_postProcess; }
    ShadowMap& getShadowMap() { return m_shadowMap; }
    Shader& getShadowShader() { return m_shadowShader; }
    Shader& getDepthShader() { return m_depthShader; }

private:
    BackgroundLayer m_backgroundLayer;
    PostProcess m_postProcess;
    ShadowMap m_shadowMap;
    Shader m_shadowShader;
    Shader m_depthShader;
    int m_windowWidth = 1280;
    int m_windowHeight = 720;
};

} // namespace dw
