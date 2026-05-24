#pragma once

#include <string>

namespace dw {

struct GameSettings {
    float masterVolume = 1.0f;
    float ambientVolume = 0.3f;
    float sfxVolume = 1.0f;
    int sensitivityLevel = 1;   // 0 = Low, 1 = Med, 2 = High
    bool headBobEnabled = true;
};

bool loadSettings(const std::string& path, GameSettings& out);
bool saveSettings(const std::string& path, const GameSettings& s);

} // namespace dw
