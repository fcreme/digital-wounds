#pragma once

namespace dw {

struct GameSettings {
    float masterVolume = 1.0f;
    float ambientVolume = 0.3f;
    float sfxVolume = 1.0f;
    int sensitivityLevel = 1;   // 0 = Low, 1 = Med, 2 = High
    bool headBobEnabled = true;
};

} // namespace dw
