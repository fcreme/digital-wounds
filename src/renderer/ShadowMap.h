#pragma once

#include <glad/gl.h>
#include <glm/glm.hpp>

namespace dw {

class ShadowMap {
public:
    ShadowMap() = default;
    ~ShadowMap() = default;

    ShadowMap(const ShadowMap&) = delete;
    ShadowMap& operator=(const ShadowMap&) = delete;

    bool init(int resolution = 2048);
    void beginCapture();
    void endCapture(int viewportW, int viewportH);
    void bind(GLenum unit) const;
    void shutdown();

    void updateLightSpaceMatrix(const glm::vec3& lightDir,
                                const glm::vec3& sceneCenter,
                                float sceneRadius);

    const glm::mat4& getLightSpaceMatrix() const { return m_lightSpaceMatrix; }
    GLuint getDepthTexture() const { return m_depthTexture; }

private:
    GLuint m_fbo = 0;
    GLuint m_depthTexture = 0;
    int m_resolution = 2048;
    glm::mat4 m_lightSpaceMatrix{1.0f};
};

} // namespace dw
