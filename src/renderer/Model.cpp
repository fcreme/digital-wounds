#include "renderer/Model.h"
#include "cgltf.h"

#include <iostream>

namespace dw {

bool Model::loadGLB(const std::string& path) {
    cgltf_options options{};
    cgltf_data* data = nullptr;

    cgltf_result result = cgltf_parse_file(&options, path.c_str(), &data);
    if (result != cgltf_result_success) {
        std::cerr << "Model: failed to parse GLB: " << path << "\n";
        return false;
    }

    result = cgltf_load_buffers(&options, data, path.c_str());
    if (result != cgltf_result_success) {
        std::cerr << "Model: failed to load GLB buffers: " << path << "\n";
        cgltf_free(data);
        return false;
    }

    // Pre-load all images into textures
    std::vector<Texture> textures(data->images_count);
    for (cgltf_size i = 0; i < data->images_count; i++) {
        const cgltf_image& img = data->images[i];
        if (img.buffer_view && img.buffer_view->buffer->data) {
            const auto* ptr = static_cast<const unsigned char*>(img.buffer_view->buffer->data) + img.buffer_view->offset;
            int len = static_cast<int>(img.buffer_view->size);
            if (!textures[i].loadFromMemory(ptr, len)) {
                std::cerr << "Model: failed to load embedded texture " << i << "\n";
            }
        }
    }

    // Process each mesh
    for (cgltf_size mi = 0; mi < data->meshes_count; mi++) {
        const cgltf_mesh& mesh = data->meshes[mi];

        for (cgltf_size pi = 0; pi < mesh.primitives_count; pi++) {
            const cgltf_primitive& prim = mesh.primitives[pi];
            if (prim.type != cgltf_primitive_type_triangles) continue;

            std::vector<Vertex> vertices;
            std::vector<uint32_t> indices;

            // Find accessors
            const cgltf_accessor* posAccessor = nullptr;
            const cgltf_accessor* normAccessor = nullptr;
            const cgltf_accessor* uvAccessor = nullptr;

            for (cgltf_size ai = 0; ai < prim.attributes_count; ai++) {
                if (prim.attributes[ai].type == cgltf_attribute_type_position)
                    posAccessor = prim.attributes[ai].data;
                else if (prim.attributes[ai].type == cgltf_attribute_type_normal)
                    normAccessor = prim.attributes[ai].data;
                else if (prim.attributes[ai].type == cgltf_attribute_type_texcoord)
                    uvAccessor = prim.attributes[ai].data;
            }

            if (!posAccessor) continue;

            // Read vertices
            cgltf_size vertCount = posAccessor->count;
            vertices.resize(vertCount);

            for (cgltf_size v = 0; v < vertCount; v++) {
                cgltf_accessor_read_float(posAccessor, v, &vertices[v].position.x, 3);
                if (normAccessor)
                    cgltf_accessor_read_float(normAccessor, v, &vertices[v].normal.x, 3);
                else
                    vertices[v].normal = glm::vec3(0.0f, 1.0f, 0.0f);
                if (uvAccessor)
                    cgltf_accessor_read_float(uvAccessor, v, &vertices[v].texcoord.x, 2);
            }

            // Read indices
            if (prim.indices) {
                indices.resize(prim.indices->count);
                for (cgltf_size i = 0; i < prim.indices->count; i++) {
                    indices[i] = static_cast<uint32_t>(cgltf_accessor_read_index(prim.indices, i));
                }
            } else {
                // Non-indexed: generate sequential indices
                indices.resize(vertCount);
                for (cgltf_size i = 0; i < vertCount; i++)
                    indices[i] = static_cast<uint32_t>(i);
            }

            auto submesh = std::make_unique<SubMesh>();
            submesh->mesh.upload(vertices, indices);

            // Extract material
            if (prim.material) {
                const cgltf_material& mat = *prim.material;
                if (mat.has_pbr_metallic_roughness) {
                    const auto& pbr = mat.pbr_metallic_roughness;
                    submesh->baseColor = glm::vec3(pbr.base_color_factor[0],
                                                    pbr.base_color_factor[1],
                                                    pbr.base_color_factor[2]);

                    // Bind diffuse texture if available
                    if (pbr.base_color_texture.texture && pbr.base_color_texture.texture->image) {
                        cgltf_size imgIdx = pbr.base_color_texture.texture->image - data->images;
                        if (imgIdx < data->images_count && textures[imgIdx].getID() != 0) {
                            submesh->texture = std::move(textures[imgIdx]);
                        }
                    }
                }
            }

            m_submeshes.push_back(std::move(submesh));
        }
    }

    cgltf_free(data);
    std::cout << "Model: loaded " << path << " (" << m_submeshes.size() << " submeshes)\n";
    return true;
}

void Model::draw(Shader& shader) const {
    for (const auto& sub : m_submeshes) {
        bool hasTex = sub->texture.getID() != 0;
        shader.setInt("uHasTexture", hasTex ? 1 : 0);
        shader.setVec3("uMaterialColor", sub->baseColor.x, sub->baseColor.y, sub->baseColor.z);
        if (hasTex) {
            sub->texture.bind(GL_TEXTURE0);
            shader.setInt("uDiffuse", 0);
        }
        sub->mesh.draw();
    }
}

} // namespace dw
