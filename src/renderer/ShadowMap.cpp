#include "renderer/ShadowMap.h"

#include <glm/gtc/matrix_transform.hpp>
#include <iostream>

namespace dw {

bool ShadowMap::init(int resolution) {
    m_resolution = resolution;

    glGenFramebuffers(1, &m_fbo);

    glGenTextures(1, &m_depthTexture);
    glBindTexture(GL_TEXTURE_2D, m_depthTexture);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT16,
                 m_resolution, m_resolution, 0,
                 GL_DEPTH_COMPONENT, GL_FLOAT, nullptr);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER);
    float borderColor[] = {1.0f, 1.0f, 1.0f, 1.0f};
    glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, borderColor);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE, GL_NONE);

    glBindFramebuffer(GL_FRAMEBUFFER, m_fbo);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT,
                           GL_TEXTURE_2D, m_depthTexture, 0);
    glDrawBuffer(GL_NONE);
    glReadBuffer(GL_NONE);

    GLenum status = glCheckFramebufferStatus(GL_FRAMEBUFFER);
    if (status != GL_FRAMEBUFFER_COMPLETE) {
        std::cerr << "ShadowMap: framebuffer incomplete (0x"
                  << std::hex << status << std::dec << ")\n";
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        return false;
    }

    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    glBindTexture(GL_TEXTURE_2D, 0);

    std::cout << "ShadowMap initialized (" << m_resolution << "x" << m_resolution << ")\n";
    return true;
}

void ShadowMap::beginCapture() {
    glBindFramebuffer(GL_FRAMEBUFFER, m_fbo);
    glViewport(0, 0, m_resolution, m_resolution);
    glClear(GL_DEPTH_BUFFER_BIT);
    glEnable(GL_DEPTH_TEST);
    glDepthFunc(GL_LESS);
    // Cull front faces to reduce shadow acne
    glEnable(GL_CULL_FACE);
    glCullFace(GL_FRONT);
}

void ShadowMap::endCapture(int viewportW, int viewportH) {
    glCullFace(GL_BACK);
    glDisable(GL_CULL_FACE);
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    glViewport(0, 0, viewportW, viewportH);
}

void ShadowMap::bind(GLenum unit) const {
    glActiveTexture(unit);
    glBindTexture(GL_TEXTURE_2D, m_depthTexture);
}

void ShadowMap::updateLightSpaceMatrix(const glm::vec3& lightDir,
                                        const glm::vec3& sceneCenter,
                                        float sceneRadius) {
    glm::vec3 dir = glm::normalize(lightDir);
    glm::vec3 lightPos = sceneCenter - dir * sceneRadius * 2.0f;

    glm::mat4 lightView = glm::lookAt(lightPos, sceneCenter, glm::vec3(0.0f, 1.0f, 0.0f));

    // If light is nearly vertical, use a different up vector
    if (std::abs(glm::dot(dir, glm::vec3(0.0f, 1.0f, 0.0f))) > 0.99f) {
        lightView = glm::lookAt(lightPos, sceneCenter, glm::vec3(0.0f, 0.0f, 1.0f));
    }

    float extent = sceneRadius * 1.5f;
    glm::mat4 lightProj = glm::ortho(-extent, extent, -extent, extent,
                                      0.1f, sceneRadius * 4.0f);

    m_lightSpaceMatrix = lightProj * lightView;
}

void ShadowMap::shutdown() {
    if (m_fbo) {
        glDeleteFramebuffers(1, &m_fbo);
        m_fbo = 0;
    }
    if (m_depthTexture) {
        glDeleteTextures(1, &m_depthTexture);
        m_depthTexture = 0;
    }
}

} // namespace dw
