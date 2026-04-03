#include "renderer/Renderer.h"
#include "renderer/Camera.h"
#include "scene/Scene.h"

#include <glad/gl.h>
#include <glm/gtc/type_ptr.hpp>
#include <iostream>

namespace dw {

bool Renderer::init(int windowWidth, int windowHeight) {
    m_windowWidth = windowWidth;
    m_windowHeight = windowHeight;

    if (!m_backgroundLayer.init()) {
        std::cerr << "Renderer: failed to init background layer\n";
        return false;
    }

    if (!m_postProcess.init(windowWidth, windowHeight)) {
        std::cerr << "Renderer: failed to init post-processing\n";
        return false;
    }

    if (!m_shadowMap.init(2048)) {
        std::cerr << "Renderer: failed to init shadow map\n";
        return false;
    }

    if (!m_shadowShader.loadFromFile("assets/shaders/shadow.vert", "assets/shaders/shadow.frag")) {
        std::cerr << "Renderer: failed to load shadow shader\n";
        return false;
    }

    if (!m_depthShader.loadFromFile("assets/shaders/depth.vert", "assets/shaders/depth.frag")) {
        std::cerr << "Renderer: failed to load depth shader\n";
        return false;
    }

    std::cout << "Renderer initialized\n";
    return true;
}

void Renderer::beginFrame() {
    m_postProcess.beginCapture();
}

void Renderer::renderBackground() {
    glDepthMask(GL_FALSE);
    m_backgroundLayer.render();
    glDepthMask(GL_TRUE);
}

void Renderer::renderShadowPass(Scene& scene, const glm::vec3& lightDir) {
    // Update light space matrix centered on scene origin
    m_shadowMap.updateLightSpaceMatrix(lightDir, glm::vec3(0.0f, 0.5f, 0.0f), 10.0f);

    m_shadowMap.beginCapture();

    m_shadowShader.use();
    m_shadowShader.setMat4("uLightSpaceMatrix",
                           glm::value_ptr(m_shadowMap.getLightSpaceMatrix()));

    scene.renderShadowCasters(m_shadowShader);

    m_shadowMap.endCapture(m_windowWidth, m_windowHeight);
}

void Renderer::renderDepthPrePass(Scene& scene, Camera& camera) {
    scene.renderDepthGeometry(m_depthShader, camera);
}

void Renderer::endFrame(float time, const glm::mat4& projection) {
    m_postProcess.endAndRender(time, projection);
}

void Renderer::onResize(int width, int height) {
    m_windowWidth = width;
    m_windowHeight = height;
    glViewport(0, 0, width, height);
    m_postProcess.onResize(width, height);
}

void Renderer::shutdown() {
    m_shadowMap.shutdown();
    m_postProcess.shutdown();
    m_backgroundLayer.shutdown();
}

} // namespace dw
