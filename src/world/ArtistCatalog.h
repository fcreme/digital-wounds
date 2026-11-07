#pragma once

#include <cstddef>
#include <string>
#include <vector>

constexpr size_t MAX_NAME_CHARS = 28;
constexpr size_t MAX_ARTIST_DESC_CHARS = 120;
constexpr size_t MAX_TITLE_CHARS = 40;
constexpr size_t MAX_DESIGN_DESC_CHARS = 200;

struct ArtistDesign {
    std::string id, title, description, imagePath;
};

struct Artist {
    std::string id, name, description;
    std::vector<ArtistDesign> designs;
};

// Loads assets/artists/<id>/artist.json folders. Problems are logged to cerr
// and collected in warnings(); one bad artist never blocks the others.
class ArtistCatalog {
public:
    int loadFromDirectory(const std::string& dir);
    const Artist* find(const std::string& id) const;
    const std::vector<Artist>& artists() const { return m_artists; }
    const std::vector<std::string>& warnings() const { return m_warnings; }

private:
    void warn(const std::string& msg);
    std::string cleanText(const std::string& text, size_t maxChars, const std::string& what);

    std::vector<Artist> m_artists;
    std::vector<std::string> m_warnings;
};
