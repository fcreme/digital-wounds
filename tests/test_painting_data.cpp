#include "test_util.h"
#include "world/PaintingData.h"
#include "world/ArtistCatalog.h"

#ifndef DW_TEST_FIXTURES
#error "DW_TEST_FIXTURES must be defined by CMake"
#endif

static const std::string PFIX = std::string(DW_TEST_FIXTURES) + "/paintings";

// Painting on the z=0 plane facing +z, width w, height h, centred at (x,y).
static Painting make(float x, float y, float w, float h, float z = 0.0f) {
    Painting p;
    p.center = {x, y, z};
    p.right = {1, 0, 0};
    p.normal = {0, 0, 1};
    p.up = {0, 1, 0};
    p.size = {w, h};
    return p;
}

TEST(picksPaintingUnderCrosshair) {
    std::vector<Painting> v{make(0, 2, 2, 3), make(10, 2, 2, 3)};
    CHECK(pickPainting(v, {0, 2, 5}, {0, 0, -1}) == 0);
}

TEST(picksAmongNeighbours) {
    std::vector<Painting> v{make(0, 2, 2, 3), make(2.1f, 2, 2, 3)};
    CHECK(pickPainting(v, {2.1f, 2, 5}, {0, 0, -1}) == 1);
}

TEST(gapBetweenFramesPicksNothing) {
    std::vector<Painting> v{make(0, 2, 2, 3), make(2.1f, 2, 2, 3)};
    CHECK(pickPainting(v, {1.05f, 2, 5}, {0, 0, -1}) == -1);
}

TEST(behindPaintingPicksNothing) {
    std::vector<Painting> v{make(0, 2, 2, 3)};
    CHECK(pickPainting(v, {0, 2, -5}, {0, 0, 1}) == -1);
}

TEST(tooFarPicksNothing) {
    std::vector<Painting> v{make(0, 2, 2, 3)};
    CHECK(pickPainting(v, {0, 2, 20}, {0, 0, -1}) == -1);
    CHECK(pickPainting(v, {0, 2, 20}, {0, 0, -1}, 25.0f) == 0);
}

TEST(nearestWinsWhenOverlapping) {
    std::vector<Painting> v{make(0, 2, 2, 3, 0.0f), make(0, 2, 2, 3, 1.0f)};
    CHECK(pickPainting(v, {0, 2, 5}, {0, 0, -1}) == 1);
}

TEST(emptyListPicksNothing) {
    CHECK(pickPainting({}, {0, 0, 0}, {0, 0, -1}) == -1);
}

TEST(topRowPickableFromFloor) {
    std::vector<Painting> v{make(0, 10, 2, 3)};
    glm::vec3 eye{0, 5, 2};
    glm::vec3 dir = glm::normalize(glm::vec3(0, 10, 0) - glm::vec3(0, 5, -0.0f) - glm::vec3(0, 0, 2));
    CHECK(pickPainting(v, eye, dir) == 0);
}

TEST(unknownArtistOrDesignIsSkipped) {
    ArtistCatalog c;
    c.loadFromDirectory(std::string(DW_TEST_FIXTURES) + "/artists");
    std::vector<Painting> v = loadPaintings(PFIX + "/good.json", c);
    CHECK(v.size() == 2);
    if (v.size() != 2) return;
    CHECK(v[0].id == "p1");
    CHECK(v[0].designIndex == 1);
    CHECK(v[1].id == "p2");
    CHECK(v[1].designIndex == 0);
    CHECK(v[1].right.x > 0.99f && v[1].right.x < 1.01f);
    CHECK(v[1].normal.z > 0.99f && v[1].normal.z < 1.01f);
    CHECK(v[1].up.y > 0.99f && v[1].up.y < 1.01f);
}

TEST(missingFileReturnsEmpty) {
    ArtistCatalog c;
    CHECK(loadPaintings(PFIX + "/nope.json", c).empty());
}

TEST(wrongTopLevelTypeReturnsEmpty) {
    ArtistCatalog c;
    CHECK(loadPaintings(PFIX + "/wrong-type.json", c).empty());
}
