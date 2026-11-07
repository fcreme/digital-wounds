#include "world/MoodUniforms.h"

#include <algorithm>
#include <cmath>
#include <string>

namespace dw {

void applyMoodUniforms(const Shader& shader, const MoodDef& def, const std::vector<SpotLight>& spots) {
    shader.setInt("uMoodEnabled", def.defined ? 1 : 0);
    if (!def.defined) return;
    shader.setFloat("uMoodAmbient", def.ambient);
    shader.setVec3("uMoodCeiling", def.ceilingStart, def.ceilingEnd, def.ceilingLevel);
    const glm::vec3 c = def.spotColor * def.spotIntensity;
    shader.setVec3("uSpotColor", c.x, c.y, c.z);
    const float toRad = 3.14159265f / 180.0f;
    shader.setVec3("uSpotShape", std::cos(def.spotOuterDeg * toRad), std::cos(def.spotInnerDeg * toRad),
                   std::max(0.01f, def.spotRange));
    const int n = std::min(static_cast<int>(spots.size()), MAX_MOOD_SPOTS);
    shader.setInt("uNumSpots", n);
    for (int i = 0; i < n; i++) {
        const std::string idx = "[" + std::to_string(i) + "]";
        shader.setVec3("uSpotPos" + idx, spots[i].position.x, spots[i].position.y, spots[i].position.z);
        shader.setVec3("uSpotDir" + idx, spots[i].direction.x, spots[i].direction.y, spots[i].direction.z);
    }
}

} // namespace dw
