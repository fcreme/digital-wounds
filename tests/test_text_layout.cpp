#include "test_util.h"
#include "ui/TextLayout.h"
#include "ui/ArtistView.h"

#include <cctype>

namespace {
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
    for (size_t variant = 0; variant < 2; variant++) {
        Artist a = maxArtist(variant);
        float height = artistViewTextHeight(a, a.designs[0], l);
        CHECK(l.textTopY + height < l.hintY);
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
