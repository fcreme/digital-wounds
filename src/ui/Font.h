#pragma once

#include <cstdint>
#include <memory>
#include <string>
#include <vector>

namespace dw {

// The UI font path, relative to the working directory (the build folder at run time).
constexpr const char* UI_FONT_PATH = "assets/fonts/SpecialElite-Regular.ttf";

// Measures a TrueType font in UI units, with no OpenGL, so layout can be tested.
//
// Sizes keep the meaning the old 8x8 bitmap font gave them: at a given scale, the text
// box starts at y, capitals are 7 * scale tall and sit on a baseline 7 * scale below y.
// Descenders hang below that line, inside the 1.5 line spacing the UI already uses.
//
// Until a font is loaded, every character is 8 * scale wide, like the old font.
class FontMetrics {
public:
    FontMetrics();
    ~FontMetrics();
    FontMetrics(FontMetrics&&) noexcept;
    FontMetrics& operator=(FontMetrics&&) noexcept;

    bool loadFile(const std::string& path);
    bool loaded() const;

    // UI units per font unit at this scale.
    float unitScale(float scale) const;
    float baseline(float scale) const { return 7.0f * scale; }

    // Advance from cp to next, kerning included (next = 0 at the end of the text).
    float advance(uint32_t cp, uint32_t next, float scale) const;
    // Width of a UTF-8 string. spacing adds spacing * 8 * scale after every character.
    // Characters the UI cannot draw count as '?', which is what UIOverlay shows instead.
    float width(const std::string& utf8, float scale, float spacing = 0.0f) const;

    bool hasGlyph(uint32_t cp) const;

    // For the renderer: the font file bytes and the stbtt_fontinfo (opaque here).
    const std::vector<unsigned char>& data() const;
    const void* info() const;

private:
    struct Impl;
    std::unique_ptr<Impl> m_impl;
};

} // namespace dw
