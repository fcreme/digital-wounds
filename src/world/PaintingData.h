#pragma once

#include <glm/glm.hpp>
#include <string>
#include <vector>

class ArtistCatalog;

struct Painting {
    std::string id, artistId, designId;
    glm::vec3 center{0.0f}, right{1.0f, 0.0f, 0.0f}, up{0.0f, 1.0f, 0.0f}, normal{0.0f, 0.0f, 1.0f};
    glm::vec2 size{1.0f};    // full width and height in world units
    int designIndex = -1;    // index in the artist's designs
};

// Loads assets/paintings/*.json. Malformed entries and entries naming an
// unknown artist/design are logged to cerr and skipped; never throws.
std::vector<Painting> loadPaintings(const std::string& path, const ArtistCatalog& catalog);

// Returns the index of the nearest painting whose front face the ray hits, or -1.
int pickPainting(const std::vector<Painting>& paintings, const glm::vec3& eye,
                 const glm::vec3& lookDir, float maxDistance = 16.0f);
