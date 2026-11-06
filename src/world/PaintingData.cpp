#include "world/PaintingData.h"
#include "world/ArtistCatalog.h"

#include <nlohmann/json.hpp>

#include <cmath>
#include <fstream>
#include <iostream>

namespace {

bool readNumber(const nlohmann::json& j, float& out) {
    if (!j.is_number()) return false;
    out = j.get<float>();
    return std::isfinite(out);
}

bool readVec(const nlohmann::json& j, const char* key, float* out, size_t n) {
    auto it = j.find(key);
    if (it == j.end() || !it->is_array() || it->size() != n) return false;
    for (size_t i = 0; i < n; ++i)
        if (!readNumber((*it)[i], out[i])) return false;
    return true;
}

bool readString(const nlohmann::json& j, const char* key, std::string& out) {
    auto it = j.find(key);
    if (it == j.end() || !it->is_string()) return false;
    out = it->get<std::string>();
    return !out.empty();
}

bool parseEntry(const nlohmann::json& j, const ArtistCatalog& catalog, Painting& p, std::string& why) {
    if (!j.is_object()) { why = "not an object"; return false; }
    if (!readString(j, "id", p.id)) { why = "missing or invalid id"; return false; }
    float c[3], r[3], n[3], s[2];
    if (!readVec(j, "center", c, 3)) { why = "bad center"; return false; }
    if (!readVec(j, "right", r, 3)) { why = "bad right"; return false; }
    if (!readVec(j, "normal", n, 3)) { why = "bad normal"; return false; }
    if (!readVec(j, "size", s, 2)) { why = "bad size"; return false; }
    if (s[0] <= 0.0f || s[1] <= 0.0f) { why = "size must be positive"; return false; }
    if (!readString(j, "artist", p.artistId)) { why = "missing or invalid artist"; return false; }
    if (!readString(j, "design", p.designId)) { why = "missing or invalid design"; return false; }

    glm::vec3 nrm(n[0], n[1], n[2]);
    if (glm::length(nrm) < 1e-6f) { why = "zero-length normal"; return false; }
    nrm = glm::normalize(nrm);
    glm::vec3 rt(r[0], r[1], r[2]);
    rt -= nrm * glm::dot(rt, nrm);   // make right perpendicular to normal
    if (glm::length(rt) < 1e-4f) { why = "right is zero or parallel to normal"; return false; }
    rt = glm::normalize(rt);

    const Artist* artist = catalog.find(p.artistId);
    if (!artist) { why = "unknown artist '" + p.artistId + "'"; return false; }
    for (size_t i = 0; i < artist->designs.size(); ++i)
        if (artist->designs[i].id == p.designId) { p.designIndex = static_cast<int>(i); break; }
    if (p.designIndex < 0) { why = "unknown design '" + p.designId + "'"; return false; }

    p.center = glm::vec3(c[0], c[1], c[2]);
    p.normal = nrm;
    p.right = rt;
    p.up = glm::cross(nrm, rt);
    p.size = glm::vec2(s[0], s[1]);
    return true;
}

} // namespace

std::vector<Painting> loadPaintings(const std::string& path, const ArtistCatalog& catalog) {
    std::vector<Painting> out;
    std::ifstream in(path);
    if (!in) {
        std::cerr << "[paintings] cannot open " << path << "\n";
        return out;
    }
    nlohmann::json doc = nlohmann::json::parse(in, nullptr, false);
    if (doc.is_discarded() || !doc.is_object()) {
        std::cerr << "[paintings] " << path << " is not a valid painting file\n";
        return out;
    }
    auto it = doc.find("paintings");
    if (it == doc.end() || !it->is_array()) {
        std::cerr << "[paintings] " << path << ": 'paintings' is missing or not an array\n";
        return out;
    }
    for (size_t i = 0; i < it->size(); ++i) {
        Painting p;
        std::string why;
        if (parseEntry((*it)[i], catalog, p, why))
            out.push_back(std::move(p));
        else
            std::cerr << "[paintings] skipping entry " << i << ": " << why << "\n";
    }
    return out;
}

int pickPainting(const std::vector<Painting>& paintings, const glm::vec3& eye,
                 const glm::vec3& lookDir, float maxDistance) {
    int best = -1;
    float bestT = maxDistance;
    for (size_t i = 0; i < paintings.size(); ++i) {
        const Painting& p = paintings[i];
        float denom = glm::dot(lookDir, p.normal);
        if (denom >= 0.0f) continue;   // not heading toward the front face
        float t = glm::dot(p.center - eye, p.normal) / denom;
        if (t < 0.0f || t > bestT) continue;
        glm::vec3 d = eye + lookDir * t - p.center;
        if (std::fabs(glm::dot(d, p.right)) > p.size.x * 0.5f) continue;
        if (std::fabs(glm::dot(d, p.up)) > p.size.y * 0.5f) continue;
        best = static_cast<int>(i);
        bestT = t;
    }
    return best;
}
