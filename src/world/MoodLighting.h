#pragma once

#include "world/PaintingData.h"

#include <glm/glm.hpp>
#include <vector>

namespace dw {

constexpr int MAX_MOOD_SPOTS = 32;  // must match MAX_SPOTS in mesh.frag and painting.frag

// The "mood" block of a room file. It multiplies the room's baked light (and the
// paintings) by: ambient, fading toward ceilingLevel between ceilingStart and ceilingEnd
// in height, plus warm spotlight cones aimed at the paintings.
struct MoodDef {
    bool defined = false;
    float ambient = 0.45f;
    float ceilingStart = 9.0f, ceilingEnd = 14.5f, ceilingLevel = 0.35f;
    glm::vec3 spotColor{1.0f, 0.82f, 0.62f};
    float spotIntensity = 1.2f;
    float spotRange = 10.0f;       // distance at which a spot is down to half strength
    float spotInnerDeg = 18.0f;    // full strength inside this half-angle
    float spotOuterDeg = 34.0f;    // nothing outside this half-angle
    float spotSpacing = 7.0f;      // along a wall, one spot per this much wall with paintings
    float spotHeight = 13.0f;      // height of the lamps
    float spotOffset = 4.5f;       // how far out from the wall the lamps hang
    int maxSpots = MAX_MOOD_SPOTS;
};

struct SpotLight {
    glm::vec3 position{0.0f};
    glm::vec3 direction{0.0f, -1.0f, 0.0f};  // unit, from the lamp toward what it lights
};

// One lamp per stretch of wall with paintings: paintings are grouped by the wall they
// hang on, cut into runs of def.spotSpacing along it, and each run gets a lamp hanging
// def.spotOffset out from the wall at def.spotHeight, aimed at the run's centre. If that
// gives more than def.maxSpots (capped at MAX_MOOD_SPOTS), the runs are made longer.
std::vector<SpotLight> placeMoodSpots(const std::vector<Painting>& paintings, const MoodDef& def);

} // namespace dw
