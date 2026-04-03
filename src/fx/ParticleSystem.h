#pragma once

#include "renderer/Shader.h"
#include <glad/gl.h>
#include <glm/glm.hpp>
#include <vector>

namespace dw {

enum class ParticleType {
    Dust,       // slow floating specks
    Fog,        // slow drifting wisps
    Fireflies,  // glowing dots with random movement
    Fire        // upward flames at light sources
};

struct ParticleEmitter {
    ParticleType type = ParticleType::Dust;
    glm::vec3 origin{0.0f};
    glm::vec3 area{5.0f, 3.0f, 5.0f};  // spawn volume half-extents
    int count = 100;
    float baseSize = 3.0f;
    glm::vec4 color{1.0f, 1.0f, 1.0f, 0.3f};
    float speed = 0.3f;
};

class ParticleSystem {
public:
    ParticleSystem() = default;
    ~ParticleSystem() = default;

    bool init();
    void clear();
    void addEmitter(const ParticleEmitter& emitter);
    void update(float dt);
    void render(const glm::mat4& view, const glm::mat4& projection);
    void shutdown();

private:
    struct Particle {
        glm::vec3 position;
        glm::vec3 velocity;
        float size;
        float alpha;
        float life;       // 0..1 phase for animation
        float phaseOffset; // random offset for sin wobble
        glm::vec4 color;
        ParticleType type;
        // spawn volume for respawning
        glm::vec3 origin;
        glm::vec3 area;
    };

    void respawn(Particle& p);

    Shader m_shader;
    GLuint m_vao = 0;
    GLuint m_vbo = 0;

    std::vector<Particle> m_particles;
    std::vector<ParticleEmitter> m_emitters;
    float m_time = 0.0f;
};

} // namespace dw
