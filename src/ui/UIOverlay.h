#pragma once

#include "renderer/Shader.h"
#include "ui/Font.h"
#include <glad/gl.h>
#include <glm/glm.hpp>
#include <map>
#include <memory>
#include <string>
#include <vector>

namespace dw {

class UIOverlay {
public:
    UIOverlay();
    ~UIOverlay();

    bool init(int screenWidth, int screenHeight);
    void onResize(int width, int height);
    // Drawable pixels per logical unit (2 on Retina). Text is rasterised at this density.
    void setPixelRatio(float ratio);

    // Draw a colored rectangle (normalized coords 0..1)
    void drawRect(float x, float y, float w, float h, const glm::vec4& color);

    // Draw a textured quad (for book pages)
    void drawTexturedRect(float x, float y, float w, float h, GLuint texture, float alpha = 1.0f);

    // Show interaction prompt at bottom of screen
    void drawPrompt(const std::string& text);

    // Draw a small crosshair dot at screen center
    void drawCrosshair();

    // Draw UTF-8 text with its box's top-left at (x, y). See FontMetrics for what scale
    // means. spacing adds spacing * 8 * scale after each character.
    void drawText(const std::string& text, float x, float y, float scale, const glm::vec4& color,
                  float spacing = 0.0f);
    // Width drawText would use for this text, in logical units.
    float textWidth(const std::string& text, float scale, float spacing = 0.0f) const;
    const FontMetrics& font() const { return m_font; }

    void shutdown();

private:
    struct GlyphAtlas;

    void initFont();
    void drawQuad(float x, float y, float w, float h);
    void drawBitmapText(const std::string& text, float x, float y, float scale, const glm::vec4& color,
                        float spacing);
    const GlyphAtlas* atlasFor(float scale);
    void clearAtlases();

    Shader m_rectShader;
    Shader m_texShader;
    GLuint m_quadVao = 0;
    GLuint m_quadVbo = 0;

    // Fallback bitmap font, used only if the TrueType font cannot be loaded
    GLuint m_fontTexture = 0;
    Shader m_fontShader;

    // TrueType font: one baked atlas per drawn pixel size
    FontMetrics m_font;
    Shader m_textShader;
    GLuint m_textVao = 0;
    GLuint m_textVbo = 0;
    size_t m_textVboFloats = 0;
    std::vector<float> m_textVerts;
    std::map<int, std::unique_ptr<GlyphAtlas>> m_atlases;  // key: pixel height in 1/4 pixels
    float m_pixelRatio = 1.0f;

    int m_screenWidth = 1280;
    int m_screenHeight = 720;
};

} // namespace dw
