#pragma once

#include "world/ArtistCatalog.h"

#include <cstddef>
#include <string>
#include <vector>

// Greedy word wrap. Words longer than a line are cut into maxChars pieces.
// Runs of whitespace collapse to one space; empty text gives no lines.
std::vector<std::string> wrapText(const std::string& text, size_t maxChars);

// Everything is in logical window units, like UIOverlay. The font is 8 units
// wide per character at scale 1, and glyphs are 8 tall.
struct ArtistViewLayout {
    float imageX, imageY, imageW, imageH;  // the paper box that holds the design
    float textX, textW, textTopY;          // right column; textTopY is the top of the area the text may use
    float nameScale, bodyScale, titleScale;
    float hintY, hintScale;                // the hint line sits here; text must end above it
};
ArtistViewLayout computeArtistViewLayout(int screenW, int screenH);

// Extra horizontal gap between the letters of the artist's name, in characters.
constexpr float ARTIST_NAME_SPACING = 0.25f;

// How many characters of the given scale fit on one line of the text column.
size_t charsPerLine(float textW, float scale, float spacing = 0.0f);

// The wrapped lines of one page's text column and where each block starts,
// measured down from the top of the block. Drawing and the fit check share this.
struct ArtistViewText {
    std::vector<std::string> name, artistDesc, title, designDesc;  // name is upper case
    float nameY, artistY, titleY, descY, pageY;
    float height;
};
ArtistViewText layoutArtistViewText(const Artist& artist, const ArtistDesign& design,
                                    const ArtistViewLayout& layout);

// Height of the whole text block (name down to page number) for one page.
float artistViewTextHeight(const Artist& artist, const ArtistDesign& design, const ArtistViewLayout& layout);
