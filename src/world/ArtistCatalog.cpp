#include "world/ArtistCatalog.h"

#include <nlohmann/json.hpp>

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>

namespace fs = std::filesystem;

void ArtistCatalog::warn(const std::string& msg) {
    std::cerr << "ArtistCatalog: " << msg << "\n";
    m_warnings.push_back(msg);
}

std::string ArtistCatalog::cleanText(const std::string& text, size_t maxChars, const std::string& what) {
    std::string out = text;
    if (out.size() > maxChars) {
        out.resize(maxChars);
        warn(what + ": text truncated to " + std::to_string(maxChars) + " characters: \"" + text + "\"");
    }
    // The UI font covers ASCII 32..122 with '&' left blank.
    bool bad = std::any_of(out.begin(), out.end(), [](char ch) {
        unsigned char c = static_cast<unsigned char>(ch);
        return c < 32 || c > 122 || c == '&';
    });
    if (bad) warn(what + ": unsupported characters in \"" + out + "\"");
    return out;
}

int ArtistCatalog::loadFromDirectory(const std::string& dir) {
    m_artists.clear();
    m_warnings.clear();

    std::error_code ec;
    if (!fs::is_directory(dir, ec)) {
        warn("artist directory not found: " + dir);
        return 0;
    }

    std::vector<fs::path> folders;
    for (const auto& entry : fs::directory_iterator(dir, ec)) {
        if (entry.is_directory()) folders.push_back(entry.path());
    }
    std::sort(folders.begin(), folders.end());

    for (const auto& folder : folders) {
        const std::string id = folder.filename().string();
        const fs::path jsonPath = folder / "artist.json";
        std::ifstream in(jsonPath);
        if (!in) {
            warn(id + ": missing artist.json");
            continue;
        }

        nlohmann::json j = nlohmann::json::parse(in, nullptr, false);
        if (j.is_discarded() || !j.is_object()) {
            warn(id + ": artist.json is not valid JSON");
            continue;
        }

        Artist artist;
        artist.id = id;
        artist.name = cleanText(j.value("name", std::string()), MAX_NAME_CHARS, id + " name");
        artist.description = cleanText(j.value("description", std::string()), MAX_ARTIST_DESC_CHARS, id + " description");
        if (artist.name.empty()) {
            warn(id + ": artist has no name");
            continue;
        }

        if (j.contains("designs") && j["designs"].is_array()) {
            for (const auto& d : j["designs"]) {
                if (!d.is_object()) continue;
                ArtistDesign design;
                design.id = d.value("id", std::string());
                const std::string image = d.value("image", std::string());
                const std::string label = id + "/" + (design.id.empty() ? "?" : design.id);
                if (design.id.empty() || image.empty()) {
                    warn(label + ": design needs an id and an image");
                    continue;
                }
                const fs::path imagePath = folder / image;
                if (!fs::is_regular_file(imagePath, ec)) {
                    warn(label + ": image file missing: " + image);
                    continue;
                }
                design.imagePath = imagePath.generic_string();
                design.title = cleanText(d.value("title", std::string()), MAX_TITLE_CHARS, label + " title");
                design.description = cleanText(d.value("description", std::string()), MAX_DESIGN_DESC_CHARS, label + " description");
                artist.designs.push_back(std::move(design));
            }
        }

        if (artist.designs.empty()) {
            warn(id + ": artist has no usable designs, skipped");
            continue;
        }
        m_artists.push_back(std::move(artist));
    }

    return static_cast<int>(m_artists.size());
}

const Artist* ArtistCatalog::find(const std::string& id) const {
    for (const auto& a : m_artists) {
        if (a.id == id) return &a;
    }
    return nullptr;
}
