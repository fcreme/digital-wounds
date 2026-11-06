#include "ui/TextLayout.h"

#include <algorithm>
#include <cctype>
#include <cmath>

std::vector<std::string> wrapText(const std::string& text, size_t maxChars) {
    if (maxChars == 0) maxChars = 1;
    std::vector<std::string> lines;
    std::string line;
    size_t i = 0;
    while (i < text.size()) {
        while (i < text.size() && std::isspace(static_cast<unsigned char>(text[i]))) i++;
        size_t start = i;
        while (i < text.size() && !std::isspace(static_cast<unsigned char>(text[i]))) i++;
        std::string word = text.substr(start, i - start);
        if (word.empty()) break;

        if (!line.empty() && line.size() + 1 + word.size() <= maxChars) {
            line += ' ';
            line += word;
            continue;
        }
        if (!line.empty()) {
            lines.push_back(line);
            line.clear();
        }
        while (word.size() > maxChars) {
            lines.push_back(word.substr(0, maxChars));
            word.erase(0, maxChars);
        }
        line = word;
    }
    if (!line.empty()) lines.push_back(line);
    return lines;
}

size_t charsPerLine(float textW, float scale, float spacing) {
    float advance = 8.0f * scale * (1.0f + spacing);
    return static_cast<size_t>(std::max(1.0f, std::floor(textW / advance)));
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
                                    const ArtistViewLayout& l) {
    ArtistViewText t{};
    std::string upper = artist.name;
    for (char& c : upper) c = static_cast<char>(std::toupper(static_cast<unsigned char>(c)));
    t.name = wrapText(upper, charsPerLine(l.textW, l.nameScale, ARTIST_NAME_SPACING));
    t.artistDesc = wrapText(artist.description, charsPerLine(l.textW, l.bodyScale));
    t.title = wrapText(design.title, charsPerLine(l.textW, l.titleScale));
    t.designDesc = wrapText(design.description, charsPerLine(l.textW, l.bodyScale));

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

float artistViewTextHeight(const Artist& artist, const ArtistDesign& design, const ArtistViewLayout& l) {
    return layoutArtistViewText(artist, design, l).height;
}
