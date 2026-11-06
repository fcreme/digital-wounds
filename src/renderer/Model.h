#pragma once

#include "renderer/Mesh.h"
#include "renderer/Texture.h"
#include "renderer/Shader.h"

#include <glm/glm.hpp>
#include <string>
#include <vector>
#include <memory>

namespace dw {

class Model {
public:
    Model() = default;
    ~Model() = default;

    Model(const Model&) = delete;
    Model& operator=(const Model&) = delete;
    Model(Model&&) = default;
    Model& operator=(Model&&) = default;

    bool load(const std::string& path);
    void draw(Shader& shader, const glm::vec3& tint = glm::vec3(1.0f)) const;

private:
    struct SubMesh {
        Mesh mesh;
        Texture texture;
        Texture normalMap;
        Texture emissiveMap;
        glm::vec3 baseColor{0.5f};
        float roughness = 0.5f;  // 0 = mirror, 1 = matte
        glm::vec3 emissive{0.0f};
    };
    std::vector<std::unique_ptr<SubMesh>> m_submeshes;
};

} // namespace dw
