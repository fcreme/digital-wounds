#include "scene/Room.h"

#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

// Minimal JSON parsing — enough for room definitions
// (avoids pulling in a full JSON lib for now)
namespace {

std::string trim(const std::string& s) {
    size_t start = s.find_first_not_of(" \t\n\r\"");
    size_t end = s.find_last_not_of(" \t\n\r\"");
    if (start == std::string::npos) return "";
    return s.substr(start, end - start + 1);
}

float parseFloat(const std::string& s) {
    try { return std::stof(trim(s)); }
    catch (...) { return 0.0f; }
}

glm::vec3 parseVec3(const std::string& s) {
    // Expects "[x, y, z]"
    glm::vec3 v(0.0f);
    std::string inner = s;
    size_t a = inner.find('[');
    size_t b = inner.find(']');
    if (a != std::string::npos && b != std::string::npos) {
        inner = inner.substr(a + 1, b - a - 1);
    }
    std::istringstream iss(inner);
    char comma;
    iss >> v.x >> comma >> v.y >> comma >> v.z;
    return v;
}

} // anonymous namespace

namespace dw {

bool loadRoomDef(const std::string& path, RoomDef& out) {
    std::ifstream file(path);
    if (!file.is_open()) {
        std::cerr << "Room: cannot open: " << path << "\n";
        return false;
    }

    // Simple key-value parsing from JSON-like format
    std::string content((std::istreambuf_iterator<char>(file)),
                         std::istreambuf_iterator<char>());

    auto getValue = [&](const std::string& key) -> std::string {
        std::string search = "\"" + key + "\"";
        size_t pos = content.find(search);
        if (pos == std::string::npos) return "";
        pos = content.find(':', pos);
        if (pos == std::string::npos) return "";
        pos++;
        // Skip whitespace
        while (pos < content.size() && (content[pos] == ' ' || content[pos] == '\t')) pos++;
        if (pos >= content.size()) return "";

        if (content[pos] == '[') {
            // Array value
            size_t end = content.find(']', pos);
            if (end == std::string::npos) return "";
            return content.substr(pos, end - pos + 1);
        } else if (content[pos] == '"') {
            // String value
            size_t end = content.find('"', pos + 1);
            if (end == std::string::npos) return "";
            return content.substr(pos + 1, end - pos - 1);
        } else {
            // Number or bool
            size_t end = content.find_first_of(",}\n", pos);
            if (end == std::string::npos) end = content.size();
            return trim(content.substr(pos, end - pos));
        }
    };

    out.name = getValue("name");
    out.backgroundPath = getValue("background");
    out.collisionPath = getValue("collision");

    std::string camPos = getValue("camera_position");
    if (!camPos.empty()) out.cameraPos = parseVec3(camPos);

    std::string camTarget = getValue("camera_target");
    if (!camTarget.empty()) out.cameraTarget = parseVec3(camTarget);

    std::string fov = getValue("camera_fov");
    if (!fov.empty()) out.cameraFov = parseFloat(fov);

    std::string amb = getValue("ambient");
    if (!amb.empty()) out.ambientColor = parseVec3(amb);

    std::string ldir = getValue("light_direction");
    if (!ldir.empty()) out.lightDir = parseVec3(ldir);

    std::string lcol = getValue("light_color");
    if (!lcol.empty()) out.lightColor = parseVec3(lcol);

    std::cout << "Room: loaded '" << out.name << "' from " << path << "\n";
    return true;
}

} // namespace dw
