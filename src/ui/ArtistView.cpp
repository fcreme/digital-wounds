#include "ui/ArtistView.h"
#include "ui/TextLayout.h"
#include "ui/UIOverlay.h"
#include "core/InputManager.h"
#include "renderer/Texture.h"

#include <algorithm>
#include <iostream>

namespace dw {

ArtistView::ArtistView() = default;
ArtistView::~ArtistView() = default;

void ArtistView::open(const Artist& artist, int startDesign) {
    m_artist = artist;
    m_artistId = artist.id;
    m_images.clear();
    for (const auto& d : m_artist.designs) {
        auto tex = std::make_unique<Texture>();
        // The UI draws these directly: top-down rows, no colour-space conversion.
        if (!tex->load(d.imagePath, false, false))
            std::cerr << "ArtistView: failed to load " << d.imagePath << "\n";
        m_images.push_back(std::move(tex));
    }
    m_state.open(static_cast<int>(m_artist.designs.size()), startDesign);
}

void ArtistView::reset() {
    m_state = ArtistViewState();
    m_images.clear();
    m_artist = Artist();
    m_artistId.clear();
}

void ArtistView::update(float dt, const InputManager& input) {
    ArtistViewKeys keys;
    keys.next = input.isKeyPressed(SDL_SCANCODE_D) || input.isKeyPressed(SDL_SCANCODE_RIGHT);
    keys.prev = input.isKeyPressed(SDL_SCANCODE_A) || input.isKeyPressed(SDL_SCANCODE_LEFT);
    keys.close = input.isKeyPressed(SDL_SCANCODE_Q);
    m_state.update(dt, keys);
    if (!m_state.isOpen()) m_images.clear();
}

void ArtistView::renderUI(UIOverlay& ui, int screenW, int screenH) {
    if (!m_state.isOpen() || m_artist.designs.empty()) return;
    const float a = m_state.alpha();
    const ArtistViewLayout l = computeArtistViewLayout(screenW, screenH);
    const int page = m_state.page();
    const ArtistDesign& design = m_artist.designs[page];

    ui.drawRect(0, 0, static_cast<float>(screenW), static_cast<float>(screenH),
                glm::vec4(0.05f, 0.045f, 0.04f, 0.97f * a));

    // Paper (#E6DCC8), with the design fitted inside it, never stretched.
    ui.drawRect(l.imageX, l.imageY, l.imageW, l.imageH,
                glm::vec4(0xE6 / 255.0f, 0xDC / 255.0f, 0xC8 / 255.0f, a));
    const Texture* tex = page < static_cast<int>(m_images.size()) ? m_images[page].get() : nullptr;
    if (tex && tex->getID() != 0 && tex->getWidth() > 0 && tex->getHeight() > 0) {
        const float pad = std::min(l.imageW, l.imageH) * 0.05f;
        const float boxW = l.imageW - 2 * pad, boxH = l.imageH - 2 * pad;
        const float fit = std::min(boxW / tex->getWidth(), boxH / tex->getHeight());
        const float w = tex->getWidth() * fit, h = tex->getHeight() * fit;
        ui.drawTexturedRect(l.imageX + (l.imageW - w) * 0.5f, l.imageY + (l.imageH - h) * 0.5f,
                            w, h, tex->getID(), a);
    }

    // Text column, centred vertically between the top and the hint.
    const ArtistViewText t = layoutArtistViewText(m_artist, design, l, ui.font());
    const float avail = l.hintY - l.textTopY;
    const float y0 = l.textTopY + std::max(0.0f, (avail - t.height) * 0.5f);
    auto lines = [&](const std::vector<std::string>& v, float y, float scale, float lineH,
                     const glm::vec4& c, float spacing) {
        for (size_t i = 0; i < v.size(); i++) ui.drawText(v[i], l.textX, y + i * lineH, scale, c, spacing);
    };
    lines(t.name, y0 + t.nameY, l.nameScale, 8.0f * l.nameScale * 1.5f,
          glm::vec4(0.78f, 0.7f, 0.5f, a), ARTIST_NAME_SPACING);
    lines(t.artistDesc, y0 + t.artistY, l.bodyScale, 8.0f * l.bodyScale * 1.5f,
          glm::vec4(0.7f, 0.66f, 0.58f, a), 0.0f);
    lines(t.title, y0 + t.titleY, l.titleScale, 8.0f * l.titleScale * 1.5f,
          glm::vec4(0.94f, 0.89f, 0.76f, a), 0.0f);
    lines(t.designDesc, y0 + t.descY, l.bodyScale, 8.0f * l.bodyScale * 1.5f,
          glm::vec4(0.82f, 0.78f, 0.7f, a), 0.0f);
    ui.drawText(std::to_string(page + 1) + " / " + std::to_string(m_state.pageCount()), l.textX,
                y0 + t.pageY, l.bodyScale, glm::vec4(0.65f, 0.6f, 0.5f, a));

    const std::string hint = "A/D: Turn page   Q: Close";
    const float hintW = ui.textWidth(hint, l.hintScale);
    ui.drawText(hint, (screenW - hintW) * 0.5f, l.hintY, l.hintScale,
                glm::vec4(0.5f, 0.5f, 0.4f, a * 0.8f));
}

} // namespace dw
