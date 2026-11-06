#pragma once

#include "world/ArtistCatalog.h"

#include <memory>
#include <string>
#include <vector>

namespace dw {

class UIOverlay;
class InputManager;
class Texture;

struct ArtistViewKeys {
    bool next = false, prev = false, close = false;
};

enum class ArtistViewPhase { Closed, Opening, Open, Closing };

// Page and fade logic with no OpenGL, so the unit tests can drive it.
class ArtistViewState {
public:
    void open(int pageCount, int startPage) {
        m_pageCount = pageCount < 1 ? 1 : pageCount;
        m_page = startPage < 0 ? 0 : (startPage >= m_pageCount ? m_pageCount - 1 : startPage);
        m_phase = ArtistViewPhase::Opening;
        m_timer = 0.0f;
    }

    // Keys only act once fully open; during the fades they are ignored.
    void update(float dt, const ArtistViewKeys& keys) {
        switch (m_phase) {
            case ArtistViewPhase::Opening:
                m_timer += dt;
                if (m_timer >= FADE_SECONDS) { m_phase = ArtistViewPhase::Open; m_timer = 0.0f; }
                break;
            case ArtistViewPhase::Closing:
                m_timer += dt;
                if (m_timer >= FADE_SECONDS) { m_phase = ArtistViewPhase::Closed; m_timer = 0.0f; }
                break;
            case ArtistViewPhase::Open:
                if (keys.next && m_page < m_pageCount - 1) m_page++;
                if (keys.prev && m_page > 0) m_page--;
                if (keys.close) { m_phase = ArtistViewPhase::Closing; m_timer = 0.0f; }
                break;
            case ArtistViewPhase::Closed:
                break;
        }
    }

    bool isOpen() const { return m_phase != ArtistViewPhase::Closed; }
    bool isInteractive() const { return m_phase == ArtistViewPhase::Open; }
    ArtistViewPhase phase() const { return m_phase; }
    int page() const { return m_page; }
    int pageCount() const { return m_pageCount; }
    float alpha() const {
        float f = m_timer / FADE_SECONDS;
        f = f > 1.0f ? 1.0f : f;
        switch (m_phase) {
            case ArtistViewPhase::Opening: return f;
            case ArtistViewPhase::Closing: return 1.0f - f;
            case ArtistViewPhase::Open: return 1.0f;
            default: return 0.0f;
        }
    }

    static constexpr float FADE_SECONDS = 0.4f;  // the same as Book

private:
    ArtistViewPhase m_phase = ArtistViewPhase::Closed;
    int m_page = 0, m_pageCount = 1;
    float m_timer = 0.0f;
};

// One artist's designs, full screen, one at a time. Images are loaded on
// open and freed when the close fade ends.
class ArtistView {
public:
    ArtistView();
    ~ArtistView();
    ArtistView(const ArtistView&) = delete;
    ArtistView& operator=(const ArtistView&) = delete;

    void open(const Artist& artist, int startDesign);
    void update(float dt, const InputManager& input);
    void renderUI(UIOverlay& ui, int screenW, int screenH);
    // Drops everything at once, with no fade (room change).
    void reset();

    bool isOpen() const { return m_state.isOpen(); }
    int currentPage() const { return m_state.page(); }
    const std::string& artistId() const { return m_artistId; }

private:
    ArtistViewState m_state;
    Artist m_artist;  // a copy, so a reload of the catalog cannot leave it dangling
    std::string m_artistId;
    std::vector<std::unique_ptr<Texture>> m_images;
};

} // namespace dw
