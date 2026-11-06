#pragma once

#include "renderer/Camera.h"
#include "renderer/Shader.h"
#include "renderer/Texture.h"
#include "world/PaintingData.h"

#include <glad/gl.h>
#include <unordered_map>
#include <vector>

class ArtistCatalog;

namespace dw {

// Draws every painting as a framed quad hung on its wall. Unlit; the frame
// takes a warm glow when highlighted. Never throws: missing images or shaders
// just leave those paintings undrawn.
class PaintingWall {
public:
    PaintingWall() = default;
    ~PaintingWall();
    PaintingWall(const PaintingWall&) = delete;
    PaintingWall& operator=(const PaintingWall&) = delete;

    // Builds quads and loads one 512 px texture per distinct design image.
    // Returns the number of paintings that will be drawn.
    int load(const std::vector<Painting>& paintings, const ArtistCatalog& catalog);
    void setBrightness(float brightness) { m_brightness = brightness; }
    void render(const Camera& camera, int highlightedIndex, float highlightAmount);
    void shutdown();

private:
    struct Item {
        int firstVertex = 0;
        glm::vec2 size{1.0f};
        float imageAspect = 1.0f;
        int texture = -1;  // index in m_textures
    };

    Shader m_shader;
    GLuint m_vao = 0;
    GLuint m_vbo = 0;
    float m_brightness = 1.0f;
    std::vector<Texture> m_textures;
    std::vector<Item> m_items;  // parallel to the painting list; texture -1 = skipped
};

} // namespace dw
