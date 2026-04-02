#pragma once

#include "renderer/Shader.h"

#include <glad/gl.h>
#include <string>

namespace dw {

class BackgroundLayer {
public:
    BackgroundLayer() = default;
    ~BackgroundLayer() = default;

    bool init();
    bool loadTexture(const std::string& imagePath);
    void render();
    void shutdown();

private:
    Shader m_shader;
    GLuint m_vao = 0;
    GLuint m_vbo = 0;
    GLuint m_texture = 0;
};

} // namespace dw
