#include "test_util.h"
#include "ui/TextLayout.h"
#include "ui/ArtistView.h"
#include "ui/Font.h"
#include "utils/Utf8.h"

#include <cctype>
#include <cmath>

#ifndef DW_UI_FONT
#error "DW_UI_FONT must be defined by CMake"
#endif

namespace {
const dw::FontMetrics& uiFont() {
    static dw::FontMetrics f = [] {
        dw::FontMetrics m;
        m.loadFile(DW_UI_FONT);
        return m;
    }();
    return f;
}

Artist maxArtist(size_t words) {
    // Longest allowed text, built from the narrowest and the widest kinds of word.
    auto fill = [&](size_t n, char c) { return std::string(n, c); };
    Artist a;
    a.id = "max";
    a.name = fill(MAX_NAME_CHARS, 'W');
    // Words of 9 letters waste the most space on each line.
    std::string d;
    while (d.size() + 10 <= MAX_ARTIST_DESC_CHARS) d += "wwwwwwwww ";
    a.description = d;
    ArtistDesign g;
    g.title = (words == 0) ? fill(MAX_TITLE_CHARS, 'W') : std::string("WWWWWWWWWW WWWWWWWWWW WWWWWWWWW W");
    std::string e;
    while (e.size() + 10 <= MAX_DESIGN_DESC_CHARS) e += "wwwwwwwww ";
    g.description = e;
    a.designs.push_back(g);
    return a;
}

void checkFits(int w, int h) {
    ArtistViewLayout l = computeArtistViewLayout(w, h);
    // The real UI font, and the fixed-width fallback used if it fails to load.
    const dw::FontMetrics fallback;
    CHECK(uiFont().loaded());
    for (const dw::FontMetrics* font : {&uiFont(), &fallback}) {
        for (size_t variant = 0; variant < 2; variant++) {
            Artist a = maxArtist(variant);
            float height = artistViewTextHeight(a, a.designs[0], l, *font);
            CHECK(l.textTopY + height < l.hintY);
            // No wrapped line may run past the text column.
            ArtistViewText t = layoutArtistViewText(a, a.designs[0], l, *font);
            for (const auto& s : t.name) CHECK(font->width(s, l.nameScale, ARTIST_NAME_SPACING) <= l.textW);
            for (const auto& s : t.title) CHECK(font->width(s, l.titleScale) <= l.textW);
            for (const auto& s : t.designDesc) CHECK(font->width(s, l.bodyScale) <= l.textW);
        }
    }
    CHECK(l.textX + l.textW <= static_cast<float>(w));
    CHECK(l.imageX + l.imageW < l.textX);
    CHECK(l.imageY + l.imageH < l.hintY);
}
}

TEST(wrapKeepsWordsWhole) {
    auto lines = wrapText("one two three four", 9);
    CHECK(lines.size() == 3);
    CHECK(lines[0] == "one two");
    CHECK(lines[1] == "three");
    CHECK(lines[2] == "four");
    lines = wrapText("one two three four", 13);
    CHECK(lines.size() == 2);
    CHECK(lines[0] == "one two three");
    CHECK(lines[1] == "four");
}

TEST(wrapBreaksWordLongerThanLine) {
    auto lines = wrapText("ab abcdefghij cd", 4);
    CHECK(lines.size() == 5);
    CHECK(lines[0] == "ab");
    CHECK(lines[1] == "abcd");
    CHECK(lines[2] == "efgh");
    CHECK(lines[3] == "ij");
    CHECK(lines[4] == "cd");
    for (const auto& s : wrapText(std::string(100, 'x'), 7)) CHECK(s.size() <= 7);
    CHECK(wrapText("abc", 0).size() == 3);  // zero width must not loop forever
}

TEST(wrapByWidthNeverSplitsACharacter) {
    // Every character 1 wide, lines at most 3: the accented word must break between characters.
    auto count = [](const std::string& s) { return static_cast<float>(dw::decodeUtf8(s).size()); };
    auto lines = wrapText("\xC3\xA9\xC3\xA9\xC3\xA9\xC3\xA9\xC3\xA9", 3.0f, count);
    CHECK(lines.size() == 2);
    for (const auto& s : lines) CHECK(dw::isValidUtf8(s));
    CHECK(lines[0] == "\xC3\xA9\xC3\xA9\xC3\xA9");
    // A character wider than the line still goes out, one per line, without looping.
    lines = wrapText("abc", 0.5f, count);
    CHECK(lines.size() == 3);
}

TEST(fontMeasuresProportionally) {
    const dw::FontMetrics& f = uiFont();
    CHECK(f.loaded());
    CHECK(f.width("W", 2.0f) > f.width("i", 2.0f));
    CHECK(f.width("WW", 2.0f) > f.width("W", 2.0f));
    // Scale is linear, and spacing adds 8 * scale per character.
    CHECK(std::fabs(f.width("Hello", 4.0f) - 2.0f * f.width("Hello", 2.0f)) < 0.01f);
    CHECK(std::fabs(f.width("ab", 2.0f, 0.25f) - f.width("ab", 2.0f) - 2 * 0.25f * 16.0f) < 0.01f);
    // Accented capitals and the ampersand are in the font.
    for (uint32_t cp : {0xC9u, 0xD1u, 0xDCu, static_cast<uint32_t>('&')}) CHECK(f.hasGlyph(cp));
    // Unloaded metrics fall back to the old fixed 8 units per character.
    const dw::FontMetrics none;
    CHECK(none.width("Jos\xC3\xA9", 1.0f) == 32.0f);
}

TEST(upperCaseKeepsAccents) {
    CHECK(dw::upperLatin1("Jos\xC3\xA9 Mu\xC3\xB1oz") == "JOS\xC3\x89 MU\xC3\x91OZ");
    CHECK(dw::upperLatin1("Stra\xC3\x9F" "e") == "STRA\xC3\x9F" "E");  // sharp s has no Latin-1 capital
    CHECK(dw::upperLatin1("a\xC3\xB7" "b") == "A\xC3\xB7" "B");         // division sign is not a letter
}

TEST(wrapHandlesEmptyText) {
    CHECK(wrapText("", 10).empty());
    CHECK(wrapText("   ", 10).empty());
}

TEST(imageTakesAbout46PercentOfWidth) {
    ArtistViewLayout l = computeArtistViewLayout(1280, 720);
    CHECK(l.imageW / 1280.0f > 0.44f);
    CHECK(l.imageW / 1280.0f < 0.48f);
}

TEST(maxLengthTextFitsAt1280x720) { checkFits(1280, 720); }
TEST(maxLengthTextFitsAtMinimumWindow) { checkFits(960, 540); }
TEST(maxLengthTextFitsAtLargeWindows) { checkFits(1920, 1080); checkFits(1600, 900); }

TEST(pageTurnStopsAtEnds) {
    dw::ArtistViewState s;
    s.open(3, 0);
    s.update(1.0f, {});  // finish opening
    CHECK(s.isInteractive());
    dw::ArtistViewKeys prev; prev.prev = true;
    dw::ArtistViewKeys next; next.next = true;
    s.update(0.016f, prev);
    CHECK(s.page() == 0);
    s.update(0.016f, next); CHECK(s.page() == 1);
    s.update(0.016f, next); CHECK(s.page() == 2);
    s.update(0.016f, next); CHECK(s.page() == 2);
    s.update(0.016f, prev); CHECK(s.page() == 1);
}

TEST(pageKeysIgnoredWhileOpening) {
    dw::ArtistViewState s;
    s.open(3, 1);
    dw::ArtistViewKeys next; next.next = true;
    dw::ArtistViewKeys close; close.close = true;
    s.update(0.1f, next);
    s.update(0.1f, close);
    CHECK(s.page() == 1);
    CHECK(s.isOpen());
    CHECK(!s.isInteractive());
    s.update(1.0f, {});
    CHECK(s.isInteractive());
    // While closing, keys do nothing and it ends closed.
    s.update(0.016f, close);
    s.update(0.1f, next);
    CHECK(s.page() == 1);
    s.update(1.0f, {});
    CHECK(!s.isOpen());
}

TEST(opensOnChosenDesign) {
    dw::ArtistViewState s;
    s.open(6, 3);
    CHECK(s.page() == 3);
    s.open(6, 99);  // out of range clamps
    CHECK(s.page() == 5);
    s.open(6, -4);
    CHECK(s.page() == 0);
}
