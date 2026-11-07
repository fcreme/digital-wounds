#include "renderer/Texture.h"
#include "stb_image.h"

#include <iostream>
#include <vector>
#include <algorithm>

namespace dw {

namespace {

// Walls and floors are seen at grazing angles, where plain trilinear filtering picks a
// mip level for the blurriest direction. Anisotropic filtering keeps them sharp.
void applyAnisotropy() {
    if (!GLAD_GL_EXT_texture_filter_anisotropic && !GLAD_GL_ARB_texture_filter_anisotropic) return;
    static float maxAniso = 0.0f;
    if (maxAniso == 0.0f) {
        glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY, &maxAniso);
        if (maxAniso < 1.0f) maxAniso = 1.0f;
    }
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY, std::min(maxAniso, 16.0f));
}

} // anonymous namespace

Texture::~Texture() { destroy(); }

Texture::Texture(Texture&& other) noexcept
    : m_id(other.m_id), m_width(other.m_width), m_height(other.m_height) {
    other.m_id = 0;
}

Texture& Texture::operator=(Texture&& other) noexcept {
    if (this != &other) {
        destroy();
        m_id = other.m_id; m_width = other.m_width; m_height = other.m_height;
        other.m_id = 0;
    }
    return *this;
}

bool Texture::load(const std::string& path, bool sRGB, bool flipVertically) {
    destroy();

    int channels;
    stbi_set_flip_vertically_on_load(flipVertically);
    unsigned char* data = stbi_load(path.c_str(), &m_width, &m_height, &channels, 4);
    if (!data) {
        std::cerr << "Texture: failed to load: " << path << "\n";
        return false;
    }

    GLenum internalFmt = sRGB ? GL_SRGB8_ALPHA8 : GL_RGBA;
    glGenTextures(1, &m_id);
    glBindTexture(GL_TEXTURE_2D, m_id);
    glTexImage2D(GL_TEXTURE_2D, 0, internalFmt, m_width, m_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data);
    glGenerateMipmap(GL_TEXTURE_2D);

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    applyAnisotropy();

    stbi_image_free(data);
    return true;
}

bool Texture::loadScaled(const std::string& path, bool sRGB, int maxSize) {
    destroy();

    int channels, w = 0, h = 0;
    stbi_set_flip_vertically_on_load(false);
    unsigned char* loaded = stbi_load(path.c_str(), &w, &h, &channels, 4);
    if (!loaded) {
        std::cerr << "Texture: failed to load: " << path << "\n";
        return false;
    }
    std::vector<unsigned char> pixels(loaded, loaded + static_cast<size_t>(w) * h * 4);
    stbi_image_free(loaded);

    while (std::max(w, h) > maxSize && w > 1 && h > 1) {
        const int nw = w / 2, nh = h / 2;
        std::vector<unsigned char> half(static_cast<size_t>(nw) * nh * 4);
        for (int y = 0; y < nh; y++) {
            for (int x = 0; x < nw; x++) {
                for (int c = 0; c < 4; c++) {
                    auto at = [&](int dx, int dy) {
                        return pixels[(static_cast<size_t>(2 * y + dy) * w + (2 * x + dx)) * 4 + c];
                    };
                    half[(static_cast<size_t>(y) * nw + x) * 4 + c] =
                        static_cast<unsigned char>((at(0, 0) + at(1, 0) + at(0, 1) + at(1, 1) + 2) / 4);
                }
            }
        }
        pixels.swap(half);
        w = nw; h = nh;
    }
    m_width = w; m_height = h;

    glGenTextures(1, &m_id);
    glBindTexture(GL_TEXTURE_2D, m_id);
    glPixelStorei(GL_UNPACK_ALIGNMENT, 4);
    glTexImage2D(GL_TEXTURE_2D, 0, sRGB ? GL_SRGB8_ALPHA8 : GL_RGBA, w, h, 0, GL_RGBA,
                 GL_UNSIGNED_BYTE, pixels.data());
    glGenerateMipmap(GL_TEXTURE_2D);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    applyAnisotropy();
    return true;
}

bool Texture::loadFromMemory(const unsigned char* data, int length, bool sRGB) {
    destroy();

    int channels;
    stbi_set_flip_vertically_on_load(false); // GLB textures are already oriented correctly
    unsigned char* pixels = stbi_load_from_memory(data, length, &m_width, &m_height, &channels, 4);
    if (!pixels) {
        std::cerr << "Texture: failed to load from memory\n";
        return false;
    }

    GLenum internalFmt = sRGB ? GL_SRGB8_ALPHA8 : GL_RGBA;
    glGenTextures(1, &m_id);
    glBindTexture(GL_TEXTURE_2D, m_id);
    glTexImage2D(GL_TEXTURE_2D, 0, internalFmt, m_width, m_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixels);
    glGenerateMipmap(GL_TEXTURE_2D);

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    applyAnisotropy();

    stbi_image_free(pixels);
    return true;
}

void Texture::bind(GLenum unit) const {
    glActiveTexture(unit);
    glBindTexture(GL_TEXTURE_2D, m_id);
}

void Texture::destroy() {
    if (m_id != 0) {
        glDeleteTextures(1, &m_id);
        m_id = 0;
    }
}

} // namespace dw
