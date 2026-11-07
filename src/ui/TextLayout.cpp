#include "ui/TextLayout.h"
#include "utils/Utf8.h"

#include <algorithm>
#include <cmath>

namespace {

bool isSpace(char c) { return c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\v' || c == '\f'; }

// Byte length of the UTF-8 character starting at s[i] (1 for a malformed byte).
size_t charLen(const std::string& s, size_t i) {
    size_t n = 1;
    while (i + n < s.size() && (static_cast<unsigned char>(s[i + n]) & 0xC0) == 0x80) n++;
    return n;
}

} // anonymous namespace

std::vector<std::string> wrapText(const std::string& text, float maxWidth, const TextMeasure& measure) {
    std::vector<std::string> lines;
    std::string line;
    size_t i = 0;
    while (i < text.size()) {
        while (i < text.size() && isSpace(text[i])) i++;
        size_t start = i;
        while (i < text.size() && !isSpace(text[i])) i++;
        std::string word = text.substr(start, i - start);
        if (word.empty()) break;

        if (!line.empty() && measure(line + " " + word) <= maxWidth) {
            line += ' ';
            line += word;
            continue;
        }
        if (!line.empty()) {
            lines.push_back(line);
            line.clear();
        }
        // Cut words that are too wide on their own, keeping at least one character per piece.
        while (measure(word) > maxWidth) {
            size_t cut = charLen(word, 0);
            if (cut >= word.size()) break;
            for (;;) {
                const size_t next = cut + charLen(word, cut);
                if (next >= word.size() || measure(word.substr(0, next)) > maxWidth) break;
                cut = next;
            }
            lines.push_back(word.substr(0, cut));
            word.erase(0, cut);
        }
        line = word;
    }
    if (!line.empty()) lines.push_back(line);
    return lines;
}

std::vector<std::string> wrapText(const std::string& text, size_t maxChars) {
    const float limit = static_cast<float>(std::max<size_t>(1, maxChars));
    return wrapText(text, limit, [](const std::string& s) {
        return static_cast<float>(dw::decodeUtf8(s).size());
    });
}

ArtistViewLayout computeArtistViewLayout(int screenW, int screenH) {
    ArtistViewLayout l{};
    const float W = static_cast<float>(screenW), H = static_cast<float>(screenH);
    const float margin = W * 0.0375f;

    // Text sizes step with the window height so the column keeps its proportions.
    l.bodyScale = H >= 1000.0f ? 3.0f : (H >= 648.0f ? 2.0f : 1.5f);
    l.nameScale = l.bodyScale;
    l.titleScale = l.bodyScale * 2.0f;
    l.hintScale = H >= 648.0f ? 1.5f : 1.0f;

    l.hintY = H - margin * 0.5f - 8.0f * l.hintScale;
    const float top = margin * 0.75f;

    l.imageW = W * 0.46f;
    l.imageX = margin;
    l.imageY = top;
    l.imageH = std::max(1.0f, l.hintY - top - margin * 0.5f);

    l.textX = l.imageX + l.imageW + margin;
    l.textW = std::max(8.0f, W - l.textX - margin);
    l.textTopY = top;
    return l;
}

namespace {
float lineHeight(float scale) { return 8.0f * scale * 1.5f; }
}

ArtistViewText layoutArtistViewText(const Artist& artist, const ArtistDesign& design,
                                    const ArtistViewLayout& l, const dw::FontMetrics& font) {
    ArtistViewText t{};
    auto wrap = [&](const std::string& text, float scale, float spacing) {
        return wrapText(text, l.textW, [&](const std::string& s) { return font.width(s, scale, spacing); });
    };
    t.name = wrap(dw::upperLatin1(artist.name), l.nameScale, ARTIST_NAME_SPACING);
    t.artistDesc = wrap(artist.description, l.bodyScale, 0.0f);
    t.title = wrap(design.title, l.titleScale, 0.0f);
    t.designDesc = wrap(design.description, l.bodyScale, 0.0f);

    const float gapSmall = l.bodyScale * 6.0f, gapBig = l.bodyScale * 12.0f;
    float y = 0.0f;
    t.nameY = y;
    y += t.name.size() * lineHeight(l.nameScale) + gapSmall;
    t.artistY = y;
    y += t.artistDesc.size() * lineHeight(l.bodyScale) + gapBig;
    t.titleY = y;
    y += t.title.size() * lineHeight(l.titleScale) + gapSmall;
    t.descY = y;
    y += t.designDesc.size() * lineHeight(l.bodyScale) + gapBig;
    t.pageY = y;
    t.height = y + 8.0f * l.bodyScale;
    return t;
}

float artistViewTextHeight(const Artist& artist, const ArtistDesign& design, const ArtistViewLayout& l,
                           const dw::FontMetrics& font) {
    return layoutArtistViewText(artist, design, l, font).height;
}
