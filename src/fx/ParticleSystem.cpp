#include "fx/ParticleSystem.h"

#include <glad/gl.h>
#include <glm/gtc/type_ptr.hpp>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include <iostream>

namespace dw {

static float randFloat() {
    return static_cast<float>(rand()) / static_cast<float>(RAND_MAX);
}

static float randRange(float lo, float hi) {
    return lo + randFloat() * (hi - lo);
}

bool ParticleSystem::init() {
    srand(static_cast<unsigned int>(time(nullptr)));

    if (!m_shader.loadFromFile("assets/shaders/particle.vert", "assets/shaders/particle.frag")) {
        std::cerr << "ParticleSystem: failed to load shaders\n";
        return false;
    }

    // Single point per particle — we'll use GL_POINTS with point size
    glGenVertexArrays(1, &m_vao);
    glGenBuffers(1, &m_vbo);

    glBindVertexArray(m_vao);
    glBindBuffer(GL_ARRAY_BUFFER, m_vbo);

    // Per-particle data: vec3 position + float size + vec4 color + float type
    // Stride = 36 bytes (3+1+4+1 = 9 floats)
    glEnableVertexAttribArray(0); // position
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(1); // size
    glVertexAttribPointer(1, 1, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)(3 * sizeof(float)));
    glEnableVertexAttribArray(2); // color
    glVertexAttribPointer(2, 4, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)(4 * sizeof(float)));
    glEnableVertexAttribArray(3); // type
    glVertexAttribPointer(3, 1, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)(8 * sizeof(float)));

    glBindVertexArray(0);

    std::cout << "ParticleSystem initialized\n";
    return true;
}

void ParticleSystem::clear() {
    m_particles.clear();
    m_emitters.clear();
}

void ParticleSystem::addEmitter(const ParticleEmitter& emitter) {
    m_emitters.push_back(emitter);

    for (int i = 0; i < emitter.count; i++) {
        Particle p{};
        p.type = emitter.type;
        p.color = emitter.color;
        p.origin = emitter.origin;
        p.area = emitter.area;
        p.phaseOffset = randFloat() * 6.283f;
        p.life = randFloat(); // start at random phase
        respawn(p);
        // Randomize initial position within volume
        p.position = emitter.origin + glm::vec3(
            randRange(-emitter.area.x, emitter.area.x),
            randRange(-emitter.area.y, emitter.area.y),
            randRange(-emitter.area.z, emitter.area.z)
        );
        m_particles.push_back(p);
    }
}

void ParticleSystem::respawn(Particle& p) {
    p.position = p.origin + glm::vec3(
        randRange(-p.area.x, p.area.x),
        randRange(0.0f, p.area.y),
        randRange(-p.area.z, p.area.z)
    );
    p.life = 0.0f;

    switch (p.type) {
        case ParticleType::Dust:
            p.velocity = glm::vec3(randRange(-0.1f, 0.1f), randRange(0.05f, 0.2f), randRange(-0.1f, 0.1f));
            p.size = randRange(1.5f, 3.5f);
            p.alpha = randRange(0.1f, 0.3f);
            break;
        case ParticleType::Fog:
            p.velocity = glm::vec3(randRange(-0.3f, 0.3f), randRange(-0.02f, 0.05f), randRange(-0.2f, 0.2f));
            p.size = randRange(8.0f, 20.0f);
            p.alpha = randRange(0.03f, 0.08f);
            break;
        case ParticleType::Fireflies:
            p.velocity = glm::vec3(randRange(-0.2f, 0.2f), randRange(-0.1f, 0.1f), randRange(-0.2f, 0.2f));
            p.size = randRange(3.0f, 6.0f);
            p.alpha = 0.0f; // will pulse
            break;
        case ParticleType::Fire:
            p.velocity = glm::vec3(randRange(-0.3f, 0.3f), randRange(1.0f, 2.5f), randRange(-0.3f, 0.3f));
            p.size = randRange(4.0f, 8.0f);
            p.alpha = randRange(0.5f, 0.9f);
            break;
    }
}

void ParticleSystem::update(float dt) {
    m_time += dt;

    for (auto& p : m_particles) {
        p.life += dt * 0.15f;
        p.position += p.velocity * dt;

        switch (p.type) {
            case ParticleType::Dust:
                // Respawn before updating position so there's no pop at origin
                if (p.life >= 1.0f) { respawn(p); break; }
                // Gentle sine wobble
                p.position.x += std::sin(m_time * 0.5f + p.phaseOffset) * 0.01f;
                p.alpha = 0.2f * (1.0f - std::abs(p.life * 2.0f - 1.0f)); // fade in/out
                break;

            case ParticleType::Fog:
                if (p.life >= 1.0f) { respawn(p); break; }
                p.position.x += std::sin(m_time * 0.2f + p.phaseOffset) * 0.02f;
                p.position.z += std::cos(m_time * 0.15f + p.phaseOffset * 1.3f) * 0.015f;
                p.alpha = 0.06f * (1.0f - std::abs(p.life * 2.0f - 1.0f));
                break;

            case ParticleType::Fireflies:
                // Erratic movement
                p.velocity.x += randRange(-1.0f, 1.0f) * dt * 2.0f;
                p.velocity.y += randRange(-0.5f, 0.5f) * dt * 2.0f;
                p.velocity.z += randRange(-1.0f, 1.0f) * dt * 2.0f;
                // Dampen
                p.velocity *= 0.98f;
                // Pulsing glow
                p.alpha = std::max(0.0f, std::sin(m_time * 3.0f + p.phaseOffset) * 0.5f + 0.3f);
                p.size = 4.0f + std::sin(m_time * 2.5f + p.phaseOffset) * 2.0f;
                // Keep in bounds
                if (glm::distance(p.position, p.origin) > glm::length(p.area)) {
                    p.velocity = (p.origin - p.position) * 0.5f;
                }
                break;

            case ParticleType::Fire:
                // Fast lifecycle — short-lived flames
                p.life += dt * 1.5f; // extra speed on top of base 0.15
                // Flicker sideways
                p.velocity.x += randRange(-2.0f, 2.0f) * dt;
                p.velocity.z += randRange(-2.0f, 2.0f) * dt;
                // Fade out as it rises, shrink
                {
                    float t = std::min(p.life * 6.6f, 1.0f); // normalize to ~1s lifespan
                    p.alpha = (1.0f - t) * 0.8f;
                    p.size = (1.0f - t * 0.7f) * 6.0f;
                    // Color shift: yellow-orange at birth → red-dark at death
                    float r = 1.0f;
                    float g = std::max(0.0f, 0.7f - t * 0.6f);
                    float b = std::max(0.0f, 0.2f - t * 0.3f);
                    p.color = glm::vec4(r, g, b, 1.0f);
                }
                if (p.life > 0.15f) respawn(p); // very short life
                break;
        }
    }
}

void ParticleSystem::setDepthTexture(GLuint tex, float nearPlane, float farPlane, int screenW, int screenH) {
    m_depthTex = tex;
    m_nearPlane = nearPlane;
    m_farPlane = farPlane;
    m_screenW = screenW;
    m_screenH = screenH;
}

void ParticleSystem::render(const glm::mat4& view, const glm::mat4& projection) {
    if (m_particles.empty()) return;

    // Build vertex data: position(3) + size(1) + color(4) + type(1) per particle
    std::vector<float> data;
    data.reserve(m_particles.size() * 9);

    for (const auto& p : m_particles) {
        if (p.alpha <= 0.001f) continue;
        data.push_back(p.position.x);
        data.push_back(p.position.y);
        data.push_back(p.position.z);
        data.push_back(p.size);
        data.push_back(p.color.r);
        data.push_back(p.color.g);
        data.push_back(p.color.b);
        data.push_back(p.alpha);
        data.push_back(static_cast<float>(static_cast<int>(p.type)));
    }

    int vertexCount = static_cast<int>(data.size()) / 9;
    if (vertexCount == 0) return;

    glBindBuffer(GL_ARRAY_BUFFER, m_vbo);
    glBufferData(GL_ARRAY_BUFFER, data.size() * sizeof(float), data.data(), GL_DYNAMIC_DRAW);

    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE); // additive blending for glow
    glDepthMask(GL_FALSE);
    glEnable(GL_PROGRAM_POINT_SIZE);

    m_shader.use();
    m_shader.setMat4("uView", glm::value_ptr(view));
    m_shader.setMat4("uProjection", glm::value_ptr(projection));

    // Bind depth texture for soft particles
    if (m_depthTex != 0) {
        glActiveTexture(GL_TEXTURE0);
        glBindTexture(GL_TEXTURE_2D, m_depthTex);
        m_shader.setInt("uDepthTex", 0);
        m_shader.setFloat("uNearPlane", m_nearPlane);
        m_shader.setFloat("uFarPlane", m_farPlane);
        m_shader.setVec2("uResolution", static_cast<float>(m_screenW), static_cast<float>(m_screenH));
        m_shader.setInt("uHasDepth", 1);
    } else {
        m_shader.setInt("uHasDepth", 0);
    }

    glBindVertexArray(m_vao);
    glDrawArrays(GL_POINTS, 0, vertexCount);
    glBindVertexArray(0);

    glDepthMask(GL_TRUE);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glDisable(GL_PROGRAM_POINT_SIZE);
}

void ParticleSystem::shutdown() {
    m_particles.clear();
    if (m_vbo) { glDeleteBuffers(1, &m_vbo); m_vbo = 0; }
    if (m_vao) { glDeleteVertexArrays(1, &m_vao); m_vao = 0; }
}

} // namespace dw
