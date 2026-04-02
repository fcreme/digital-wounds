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

    bool loadGLB(const std::string& path);
    void draw(Shader& shader) const;

private:
    struct SubMesh {
        Mesh mesh;
        Texture texture;
        glm::vec3 baseColor{1.0f};
    };
    std::vector<std::unique_ptr<SubMesh>> m_submeshes;
};

} // namespace dw
