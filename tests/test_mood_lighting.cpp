#include "test_util.h"
#include "world/MoodLighting.h"
#include "world/ArtistCatalog.h"
#include "world/PaintingData.h"

#include <cmath>

#ifndef DW_ASSETS_DIR
#error "DW_ASSETS_DIR must be defined by CMake"
#endif

using dw::MoodDef;
using dw::SpotLight;

namespace {

Painting hung(glm::vec3 center, glm::vec3 normal, glm::vec2 size = {2.0f, 2.0f}) {
    Painting p;
    p.center = center;
    p.normal = normal;
    p.size = size;
    return p;
}

// Two facing walls 20 apart, ten paintings each over 30 units of wall.
std::vector<Painting> corridor() {
    std::vector<Painting> v;
    for (int i = 0; i < 10; i++) {
        float z = -15.0f + i * 3.3f;
        v.push_back(hung({-10.0f, 6.0f + (i % 3), z}, {1.0f, 0.0f, 0.0f}));
        v.push_back(hung({10.0f, 5.5f + (i % 2), z}, {-1.0f, 0.0f, 0.0f}));
    }
    return v;
}

float coneCos(const SpotLight& s, const glm::vec3& p) {
    return glm::dot(s.direction, glm::normalize(p - s.position));
}

// True if p is inside the outer cone of at least one spot.
bool lit(const std::vector<SpotLight>& spots, const glm::vec3& p, const MoodDef& def) {
    const float outer = std::cos(def.spotOuterDeg * 3.14159265f / 180.0f);
    for (const auto& s : spots) if (coneCos(s, p) > outer) return true;
    return false;
}

} // anonymous namespace

TEST(spotsHangInFrontOfTheirWallAtLampHeight) {
    MoodDef def;
    auto paintings = corridor();
    auto spots = dw::placeMoodSpots(paintings, def);
    CHECK(!spots.empty());
    CHECK(static_cast<int>(spots.size()) <= dw::MAX_MOOD_SPOTS);
    for (const auto& s : spots) {
        CHECK(std::fabs(s.position.y - def.spotHeight) < 1e-4f);
        CHECK(std::fabs(glm::length(s.direction) - 1.0f) < 1e-4f);
        CHECK(s.direction.y < 0.0f);                       // aimed down at the art
        CHECK(std::fabs(s.position.x) < 10.0f);            // inside the corridor, off the walls
    }
    // Both walls get lamps: about one per spotSpacing of wall.
    int west = 0, east = 0;
    for (const auto& s : spots) (s.position.x < 0.0f ? west : east)++;
    CHECK(west >= 3 && east >= 3);
}

TEST(everyPaintingIsInsideACone) {
    MoodDef def;
    auto paintings = corridor();
    auto spots = dw::placeMoodSpots(paintings, def);
    for (const auto& p : paintings) CHECK(lit(spots, p.center, def));
}

TEST(spotCountRespectsTheCap) {
    MoodDef def;
    def.maxSpots = 3;
    CHECK(dw::placeMoodSpots(corridor(), def).size() <= 3u);
    def.maxSpots = 0;
    CHECK(dw::placeMoodSpots(corridor(), def).empty());
    def.maxSpots = 1000;  // never above what the shaders hold
    def.spotSpacing = 0.1f;
    CHECK(static_cast<int>(dw::placeMoodSpots(corridor(), def).size()) <= dw::MAX_MOOD_SPOTS);
    CHECK(dw::placeMoodSpots({}, MoodDef{}).empty());
}

TEST(museumPaintingsAreAllLit) {
    // The real gallery: with the default mood settings, no painting is left in the dark.
    ArtistCatalog catalog;
    catalog.loadFromDirectory(std::string(DW_ASSETS_DIR) + "/artists");
    auto paintings = loadPaintings(std::string(DW_ASSETS_DIR) + "/paintings/museum.json", catalog);
    CHECK(paintings.size() >= 100u);
    MoodDef def;
    auto spots = dw::placeMoodSpots(paintings, def);
    CHECK(static_cast<int>(spots.size()) <= dw::MAX_MOOD_SPOTS);
    int dark = 0;
    for (const auto& p : paintings) if (!lit(spots, p.center, def)) dark++;
    if (dark) std::cerr << "  " << dark << " museum paintings outside every cone\n";
    CHECK(dark == 0);
}
