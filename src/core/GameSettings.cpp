#include "core/GameSettings.h"

#include <nlohmann/json.hpp>
#include <fstream>
#include <iostream>

using json = nlohmann::json;

namespace {

template<typename T>
T getOr(const json& j, const std::string& key, const T& def) {
    if (j.contains(key)) return j[key].get<T>();
    return def;
}

} // anonymous namespace

namespace dw {

bool loadSettings(const std::string& path, GameSettings& out) {
    std::ifstream file(path);
    if (!file.is_open()) return false;

    try {
        json j = json::parse(file);
        out.masterVolume   = getOr<float>(j, "master_volume",   1.0f);
        out.ambientVolume  = getOr<float>(j, "ambient_volume",  0.3f);
        out.sfxVolume      = getOr<float>(j, "sfx_volume",      1.0f);
        out.sensitivityLevel = getOr<int>(j, "sensitivity",     1);
        out.headBobEnabled = getOr<bool>(j, "head_bob",         true);
    } catch (const json::parse_error& e) {
        std::cerr << "Settings: parse error — " << e.what() << "\n";
        return false;
    }

    return true;
}

bool saveSettings(const std::string& path, const GameSettings& s) {
    json j;
    j["master_volume"]  = s.masterVolume;
    j["ambient_volume"] = s.ambientVolume;
    j["sfx_volume"]     = s.sfxVolume;
    j["sensitivity"]    = s.sensitivityLevel;
    j["head_bob"]       = s.headBobEnabled;

    std::ofstream file(path);
    if (!file.is_open()) {
        std::cerr << "Settings: failed to write " << path << "\n";
        return false;
    }

    file << j.dump(4) << "\n";
    return true;
}

} // namespace dw
