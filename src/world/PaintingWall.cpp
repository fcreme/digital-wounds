#include "world/PaintingWall.h"
#include "world/ArtistCatalog.h"

#include <glm/gtc/type_ptr.hpp>
#include <chrono>
#include <iostream>

namespace dw {

namespace {
constexpr int WALL_TEXTURE_SIZE = 512;
}

PaintingWall::~PaintingWall() { shutdown(); }

int PaintingWall::load(const std::vector<Painting>& paintings, const ArtistCatalog& catalog) {
    shutdown();
    if (paintings.empty()) return 0;

    if (!m_shader.loadFromFile("assets/shaders/painting.vert", "assets/shaders/painting.frag")) {
        std::cerr << "PaintingWall: failed to load shader; paintings not drawn\n";
        return 0;
    }

    auto t0 = std::chrono::steady_clock::now();
    std::unordered_map<std::string, int> byPath;
    std::vector<float> verts;  // pos(3) uv(2) per vertex, 6 per painting
    m_items.assign(paintings.size(), Item{});
    int drawn = 0;

    for (size_t i = 0; i < paintings.size(); i++) {
        const Painting& p = paintings[i];
        const Artist* artist = catalog.find(p.artistId);
        if (!artist || p.designIndex < 0 || p.designIndex >= static_cast<int>(artist->designs.size()))
            continue;
        const std::string& path = artist->designs[p.designIndex].imagePath;

        int texIndex;
        auto it = byPath.find(path);
        if (it != byPath.end()) {
            texIndex = it->second;
        } else {
            Texture tex;
            if (!tex.loadScaled(path, true, WALL_TEXTURE_SIZE)) continue;
            glBindTexture(GL_TEXTURE_2D, tex.getID());
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
            texIndex = static_cast<int>(m_textures.size());
            m_textures.push_back(std::move(tex));
            byPath[path] = texIndex;
        }

        Item& item = m_items[i];
        item.texture = texIndex;
        item.size = p.size;
        item.imageAspect = static_cast<float>(m_textures[texIndex].getWidth()) /
                           static_cast<float>(m_textures[texIndex].getHeight());
        item.firstVertex = static_cast<int>(verts.size() / 5);

        const glm::vec3 r = p.right * (p.size.x * 0.5f);
        const glm::vec3 u = p.up * (p.size.y * 0.5f);
        // Hung just off the wall so it never z-fights with it.
        const glm::vec3 c = p.center + p.normal * 0.03f;
        // Counter-clockwise seen from the front; uv (0,0) is the top-left corner.
        const glm::vec3 bl = c - r - u, br = c + r - u, tr = c + r + u, tl = c - r + u;
        auto push = [&](const glm::vec3& v, float s, float t) {
            verts.insert(verts.end(), {v.x, v.y, v.z, s, t});
        };
        push(bl, 0, 1); push(br, 1, 1); push(tr, 1, 0);
        push(bl, 0, 1); push(tr, 1, 0); push(tl, 0, 0);
        drawn++;
    }

    glGenVertexArrays(1, &m_vao);
    glGenBuffers(1, &m_vbo);
    glBindVertexArray(m_vao);
    glBindBuffer(GL_ARRAY_BUFFER, m_vbo);
    glBufferData(GL_ARRAY_BUFFER, static_cast<GLsizeiptr>(verts.size() * sizeof(float)),
                 verts.data(), GL_STATIC_DRAW);
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(float), nullptr);
    glEnableVertexAttribArray(1);
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(float),
                          reinterpret_cast<void*>(3 * sizeof(float)));
    glBindVertexArray(0);

    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now() - t0).count();
    std::cout << "PaintingWall: " << drawn << "/" << paintings.size() << " paintings, "
              << m_textures.size() << " textures in " << ms << " ms\n";
    return drawn;
}

void PaintingWall::render(const Camera& camera, int highlightedIndex, float highlightAmount) {
    if (m_vao == 0) return;
    m_shader.use();
    m_shader.setMat4("uView", glm::value_ptr(camera.getView()));
    m_shader.setMat4("uProjection", glm::value_ptr(camera.getProjection()));
    m_shader.setFloat("uBrightness", m_brightness);
    m_shader.setInt("uArt", 0);

    glEnable(GL_DEPTH_TEST);
    glDepthMask(GL_TRUE);
    glBindVertexArray(m_vao);
    for (size_t i = 0; i < m_items.size(); i++) {
        const Item& item = m_items[i];
        if (item.texture < 0) continue;
        m_shader.setVec2("uSize", item.size.x, item.size.y);
        m_shader.setFloat("uImageAspect", item.imageAspect);
        m_shader.setFloat("uHighlight",
                          static_cast<int>(i) == highlightedIndex ? highlightAmount : 0.0f);
        m_textures[item.texture].bind(GL_TEXTURE0);
        glDrawArrays(GL_TRIANGLES, item.firstVertex, 6);
    }
    glBindVertexArray(0);
}

void PaintingWall::shutdown() {
    if (m_vbo) glDeleteBuffers(1, &m_vbo);
    if (m_vao) glDeleteVertexArrays(1, &m_vao);
    m_vbo = m_vao = 0;
    m_textures.clear();
    m_items.clear();
}

} // namespace dw
