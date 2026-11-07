#include "ui/Font.h"
#include "utils/Utf8.h"

#include "stb_truetype.h"

#include <fstream>
#include <iostream>
#include <iterator>

namespace dw {

struct FontMetrics::Impl {
    std::vector<unsigned char> data;
    stbtt_fontinfo info{};
    float capHeight = 0.0f;  // in font units
};

FontMetrics::FontMetrics() = default;
FontMetrics::~FontMetrics() = default;
FontMetrics::FontMetrics(FontMetrics&&) noexcept = default;
FontMetrics& FontMetrics::operator=(FontMetrics&&) noexcept = default;

bool FontMetrics::loadFile(const std::string& path) {
    m_impl.reset();
    std::ifstream in(path, std::ios::binary);
    if (!in) {
        std::cerr << "Font: cannot open " << path << "\n";
        return false;
    }
    auto impl = std::make_unique<Impl>();
    impl->data.assign(std::istreambuf_iterator<char>(in), std::istreambuf_iterator<char>());
    if (impl->data.empty() ||
        !stbtt_InitFont(&impl->info, impl->data.data(), stbtt_GetFontOffsetForIndex(impl->data.data(), 0))) {
        std::cerr << "Font: not a usable TrueType font: " << path << "\n";
        return false;
    }
    // Capital height from 'H', so scale 1 keeps the old font's 7-unit capitals.
    int x0, y0, x1, y1;
    if (stbtt_GetCodepointBox(&impl->info, 'H', &x0, &y0, &x1, &y1) && y1 > 0) {
        impl->capHeight = static_cast<float>(y1);
    } else {
        int ascent, descent, gap;
        stbtt_GetFontVMetrics(&impl->info, &ascent, &descent, &gap);
        impl->capHeight = 0.7f * static_cast<float>(ascent);
    }
    m_impl = std::move(impl);
    return true;
}

bool FontMetrics::loaded() const { return m_impl != nullptr; }

float FontMetrics::unitScale(float scale) const {
    return m_impl ? 7.0f * scale / m_impl->capHeight : 0.0f;
}

float FontMetrics::advance(uint32_t cp, uint32_t next, float scale) const {
    if (!m_impl) return 8.0f * scale;
    int adv = 0, lsb = 0;
    stbtt_GetCodepointHMetrics(&m_impl->info, static_cast<int>(cp), &adv, &lsb);
    float units = static_cast<float>(adv);
    if (next) units += static_cast<float>(
        stbtt_GetCodepointKernAdvance(&m_impl->info, static_cast<int>(cp), static_cast<int>(next)));
    return units * unitScale(scale);
}

float FontMetrics::width(const std::string& utf8, float scale, float spacing) const {
    std::vector<uint32_t> cps = decodeUtf8(utf8);
    for (uint32_t& cp : cps) if (!isUiDrawable(cp)) cp = '?';  // as UIOverlay draws them
    float w = 0.0f;
    for (size_t i = 0; i < cps.size(); i++) {
        w += advance(cps[i], i + 1 < cps.size() ? cps[i + 1] : 0, scale);
        w += spacing * 8.0f * scale;
    }
    return w;
}

bool FontMetrics::hasGlyph(uint32_t cp) const {
    return m_impl && stbtt_FindGlyphIndex(&m_impl->info, static_cast<int>(cp)) != 0;
}

const std::vector<unsigned char>& FontMetrics::data() const {
    static const std::vector<unsigned char> empty;
    return m_impl ? m_impl->data : empty;
}

const void* FontMetrics::info() const { return m_impl ? &m_impl->info : nullptr; }

} // namespace dw
