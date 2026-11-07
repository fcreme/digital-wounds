#include "world/MoodLighting.h"

#include <algorithm>
#include <cmath>
#include <map>
#include <tuple>

namespace dw {

namespace {

struct WallKey {
    int nx, nz, plane;  // rounded outward normal and the wall's offset along it
    bool operator<(const WallKey& o) const {
        return std::tie(nx, nz, plane) < std::tie(o.nx, o.nz, o.plane);
    }
};

std::vector<SpotLight> place(const std::vector<Painting>& paintings, const MoodDef& def, float spacing) {
    // Group by wall: same facing (to 1 decimal) and same plane (to half a unit).
    std::map<WallKey, std::vector<const Painting*>> walls;
    for (const Painting& p : paintings) {
        glm::vec3 n(p.normal.x, 0.0f, p.normal.z);
        if (glm::length(n) < 1e-3f) continue;  // not hung on a wall
        n = glm::normalize(n);
        WallKey k{static_cast<int>(std::lround(n.x * 10.0f)), static_cast<int>(std::lround(n.z * 10.0f)),
                  static_cast<int>(std::lround(glm::dot(p.center, n) * 2.0f))};
        walls[k].push_back(&p);
    }

    std::vector<SpotLight> spots;
    for (auto& [key, list] : walls) {
        glm::vec3 n = glm::normalize(glm::vec3(key.nx, 0.0f, key.nz));
        glm::vec3 along = glm::normalize(glm::cross(glm::vec3(0.0f, 1.0f, 0.0f), n));
        std::sort(list.begin(), list.end(), [&](const Painting* a, const Painting* b) {
            return glm::dot(a->center, along) < glm::dot(b->center, along);
        });
        const float lo = glm::dot(list.front()->center, along);
        const float hi = glm::dot(list.back()->center, along);
        const int runs = std::max(1, static_cast<int>(std::ceil((hi - lo + 1e-3f) / spacing)));
        const float runLen = (hi - lo) / runs;

        std::vector<glm::vec3> sum(runs, glm::vec3(0.0f));
        std::vector<float> weight(runs, 0.0f);
        for (const Painting* p : list) {
            const float t = glm::dot(p->center, along) - lo;
            const int r = runLen > 0.0f ? std::min(runs - 1, static_cast<int>(t / runLen)) : 0;
            const float w = std::max(1e-3f, p->size.x * p->size.y);
            sum[r] += p->center * w;
            weight[r] += w;
        }
        for (int r = 0; r < runs; r++) {
            if (weight[r] <= 0.0f) continue;
            const glm::vec3 target = sum[r] / weight[r];
            SpotLight s;
            s.position = target + n * def.spotOffset;
            s.position.y = def.spotHeight;
            s.direction = glm::normalize(target - s.position);
            spots.push_back(s);
        }
    }
    return spots;
}

} // anonymous namespace

std::vector<SpotLight> placeMoodSpots(const std::vector<Painting>& paintings, const MoodDef& def) {
    const int cap = std::clamp(def.maxSpots, 0, MAX_MOOD_SPOTS);
    if (cap == 0 || paintings.empty()) return {};
    float spacing = std::max(0.5f, def.spotSpacing);
    std::vector<SpotLight> spots = place(paintings, def, spacing);
    for (int tries = 0; static_cast<int>(spots.size()) > cap && tries < 64; tries++) {
        spacing *= 1.25f;
        spots = place(paintings, def, spacing);
    }
    if (static_cast<int>(spots.size()) > cap) spots.resize(cap);
    return spots;
}

} // namespace dw
