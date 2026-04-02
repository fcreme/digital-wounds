#pragma once

#include "renderer/Shader.h"
#include <glad/gl.h>

namespace dw {

class PostProcess {
public:
    PostProcess() = default;
    ~PostProcess() = default;

    bool init(int width, int height);
    void beginCapture();
    void endAndRender(float time);
    void onResize(int width, int height);
    void shutdown();

private:
    void createFBO(int width, int height);
    void destroyFBO();

    Shader m_shader;
    GLuint m_fbo = 0;
    GLuint m_colorTex = 0;
    GLuint m_depthRbo = 0;
    GLuint m_quadVao = 0;
    GLuint m_quadVbo = 0;

    int m_width = 1280;
    int m_height = 720;
};

} // namespace dw
