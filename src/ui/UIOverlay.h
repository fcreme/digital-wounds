#pragma once

#include "renderer/Shader.h"
#include <glad/gl.h>
#include <glm/glm.hpp>
#include <string>

namespace dw {

class UIOverlay {
public:
    UIOverlay() = default;
    ~UIOverlay() = default;

    bool init(int screenWidth, int screenHeight);
    void onResize(int width, int height);

    // Draw a colored rectangle (normalized coords 0..1)
    void drawRect(float x, float y, float w, float h, const glm::vec4& color);

    // Draw a textured quad (for book pages)
    void drawTexturedRect(float x, float y, float w, float h, GLuint texture, float alpha = 1.0f);

    // Show interaction prompt at bottom of screen
    void drawPrompt(const std::string& text);

    // Draw a small crosshair dot at screen center
    void drawCrosshair();

    // Draw a simple text label (bitmap font - characters as quads)
    void drawText(const std::string& text, float x, float y, float scale, const glm::vec4& color);

    void shutdown();

private:
    void initFont();
    void drawQuad(float x, float y, float w, float h);

    Shader m_rectShader;
    Shader m_texShader;
    GLuint m_quadVao = 0;
    GLuint m_quadVbo = 0;

    // Bitmap font
    GLuint m_fontTexture = 0;
    Shader m_fontShader;

    int m_screenWidth = 1280;
    int m_screenHeight = 720;
};

} // namespace dw
