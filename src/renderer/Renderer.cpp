#include "renderer/Renderer.h"

#include <glad/gl.h>
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

void Renderer::endFrame(float time) {
    m_postProcess.endAndRender(time);
}

void Renderer::onResize(int width, int height) {
    m_windowWidth = width;
    m_windowHeight = height;
    glViewport(0, 0, width, height);
    m_postProcess.onResize(width, height);
}

void Renderer::shutdown() {
    m_postProcess.shutdown();
    m_backgroundLayer.shutdown();
}

} // namespace dw
