#include "test_util.h"
#include "world/ArtistCatalog.h"
#include "utils/Utf8.h"

#include <algorithm>

#ifndef DW_TEST_FIXTURES
#error "DW_TEST_FIXTURES must be defined by CMake"
#endif

static const std::string FIX = std::string(DW_TEST_FIXTURES) + "/artists";

static bool warned(const ArtistCatalog& c, const std::string& needle) {
    return std::any_of(c.warnings().begin(), c.warnings().end(),
        [&](const std::string& w) { return w.find(needle) != std::string::npos; });
}

TEST(loadsGoodArtist) {
    ArtistCatalog c;
    c.loadFromDirectory(FIX);
    const Artist* a = c.find("good");
    CHECK(a != nullptr);
    if (!a) return;
    CHECK(a->name == "Dark Ink Studio");
    CHECK(a->designs.size() == 2);
    CHECK(a->designs[0].id == "ravens-eye");
    CHECK(a->designs[0].imagePath.find("good") != std::string::npos);
    CHECK(a->designs[0].imagePath.find("a.png") != std::string::npos);
}

TEST(badJsonSkipsOnlyThatArtist) {
    ArtistCatalog c;
    c.loadFromDirectory(FIX);
    CHECK(c.find("bad-json") == nullptr);
    CHECK(c.find("good") != nullptr);
    CHECK(warned(c, "bad-json"));
}

TEST(artistWithNoDesignsIsSkipped) {
    ArtistCatalog c;
    c.loadFromDirectory(FIX);
    CHECK(c.find("no-designs") == nullptr);
}

TEST(missingImageDropsThatDesignAndWarns) {
    ArtistCatalog c;
    c.loadFromDirectory(FIX);
    const Artist* a = c.find("missing-image");
    CHECK(a != nullptr);
    if (!a) return;
    CHECK(a->designs.size() == 1);
    CHECK(warned(c, "gone.png"));
}

TEST(tooLongTextIsTruncatedAndWarns) {
    ArtistCatalog c;
    c.loadFromDirectory(FIX);
    const Artist* a = c.find("too-long");
    CHECK(a != nullptr);
    if (!a) return;
    CHECK(a->name.size() == MAX_NAME_CHARS);
    CHECK(a->description.size() == MAX_ARTIST_DESC_CHARS);
    CHECK(a->designs[0].title.size() == MAX_TITLE_CHARS);
    CHECK(a->designs[0].description.size() == MAX_DESIGN_DESC_CHARS);
    CHECK(warned(c, "too-long"));
}

TEST(accentsAndAmpersandAreSupported) {
    ArtistCatalog c;
    c.loadFromDirectory(FIX);
    const Artist* a = c.find("accented");
    CHECK(a != nullptr);
    if (!a) return;
    CHECK(a->name == "Jos\xC3\xA9");
    CHECK(a->designs[0].title == "Ink & Blood");
    CHECK(!warned(c, "Jos"));
    CHECK(!warned(c, "Ink & Blood"));
}

TEST(charactersOutsideTheFontWarn) {
    ArtistCatalog c;
    c.loadFromDirectory(FIX);
    const Artist* a = c.find("unsupported");
    CHECK(a != nullptr);  // still loaded; the UI shows '?' for those characters
    if (!a) return;
    CHECK(warned(c, "unsupported name: unsupported characters"));
    CHECK(warned(c, "Arrow"));
}

TEST(truncationNeverSplitsACharacter) {
    // 27 ASCII bytes then a two-byte e-acute: a 28-byte cut must drop the whole character.
    const std::string s = std::string(27, 'a') + "\xC3\xA9" + "b";
    CHECK(dw::truncateUtf8(s, 28) == std::string(27, 'a'));
    CHECK(dw::truncateUtf8(s, 29) == std::string(27, 'a') + "\xC3\xA9");
    CHECK(dw::truncateUtf8("short", 28) == "short");
    CHECK(dw::isValidUtf8(dw::truncateUtf8(s, 28)));
}

TEST(artistsAreSortedById) {
    ArtistCatalog c;
    c.loadFromDirectory(FIX);
    CHECK(std::is_sorted(c.artists().begin(), c.artists().end(),
        [](const Artist& x, const Artist& y) { return x.id < y.id; }));
}

TEST(missingDirectoryReturnsZero) {
    ArtistCatalog c;
    CHECK(c.loadFromDirectory(FIX + "/does-not-exist") == 0);
    CHECK(c.artists().empty());
}

TEST(wronglyTypedFieldsDoNotThrow) {
    ArtistCatalog c;
    c.loadFromDirectory(FIX);
    CHECK(c.find("good") != nullptr);
    CHECK(c.find("bad-types") == nullptr);
    CHECK(c.find("bad-designs-type") == nullptr);
    const Artist* m = c.find("mixed-entries");
    CHECK(m != nullptr);
    if (!m) return;
    CHECK(m->designs.size() == 1);
    CHECK(m->designs[0].id == "ok");
}
