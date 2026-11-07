#pragma once

#include "world/ArtistCatalog.h"
#include "ui/Font.h"

#include <cstddef>
#include <functional>
#include <string>
#include <vector>

// Width of a piece of text, in whatever unit maxWidth uses.
using TextMeasure = std::function<float(const std::string&)>;

// Greedy word wrap by measured width. Words wider than a line are cut between
// characters (never inside a UTF-8 sequence), at least one character per line.
// Runs of whitespace collapse to one space; empty text gives no lines.
std::vector<std::string> wrapText(const std::string& text, float maxWidth, const TextMeasure& measure);
// The same, counting characters: at most maxChars per line.
std::vector<std::string> wrapText(const std::string& text, size_t maxChars);

// Everything is in logical window units, like UIOverlay. Text at scale s has
// capitals 7 * s tall in an 8 * s box (see FontMetrics).
struct ArtistViewLayout {
    float imageX, imageY, imageW, imageH;  // the paper box that holds the design
    float textX, textW, textTopY;          // right column; textTopY is the top of the area the text may use
    float nameScale, bodyScale, titleScale;
    float hintY, hintScale;                // the hint line sits here; text must end above it
};
ArtistViewLayout computeArtistViewLayout(int screenW, int screenH);

// Extra horizontal gap after each letter of the artist's name, in units of 8 * scale.
constexpr float ARTIST_NAME_SPACING = 0.25f;

// The wrapped lines of one page's text column and where each block starts,
// measured down from the top of the block. Drawing and the fit check share this.
struct ArtistViewText {
    std::vector<std::string> name, artistDesc, title, designDesc;  // name is upper case
    float nameY, artistY, titleY, descY, pageY;
    float height;
};
ArtistViewText layoutArtistViewText(const Artist& artist, const ArtistDesign& design,
                                    const ArtistViewLayout& layout, const dw::FontMetrics& font);

// Height of the whole text block (name down to page number) for one page.
float artistViewTextHeight(const Artist& artist, const ArtistDesign& design, const ArtistViewLayout& layout,
                           const dw::FontMetrics& font);
