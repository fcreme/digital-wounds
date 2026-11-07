#pragma once

#include "renderer/Shader.h"
#include "world/MoodLighting.h"

#include <vector>

namespace dw {

// Sets the moodLight() uniforms that mesh.frag and painting.frag share. Call it every
// frame the shader draws: with def.defined false it switches the mood light off.
void applyMoodUniforms(const Shader& shader, const MoodDef& def, const std::vector<SpotLight>& spots);

} // namespace dw
