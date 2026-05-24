#include "audio/AudioManager.h"

#include <cstring>
#include <iostream>
#include <algorithm>
#include <cmath>
#include <random>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace dw {

bool AudioManager::init() {
    SDL_AudioSpec desired{};
    desired.freq = 44100;
    desired.format = AUDIO_S16LSB;
    desired.channels = 2;
    desired.samples = 2048;
    desired.callback = audioCallback;
    desired.userdata = this;

    m_device = SDL_OpenAudioDevice(nullptr, 0, &desired, &m_spec, SDL_AUDIO_ALLOW_FORMAT_CHANGE);
    if (m_device == 0) {
        std::cerr << "AudioManager: failed to open audio device: " << SDL_GetError() << "\n";
        return false;
    }

    // Init reverb buffer (stereo samples, so multiply by channels)
    m_reverbDelaySamples = static_cast<size_t>(m_spec.freq * 0.5f) * m_spec.channels;
    m_reverbBuffer.resize(m_reverbDelaySamples, 0.0f);
    m_reverbPos = 0;

    // Start audio playback
    SDL_PauseAudioDevice(m_device, 0);

    std::cout << "AudioManager initialized (" << m_spec.freq << " Hz, "
              << (int)m_spec.channels << " ch)\n";
    return true;
}

void AudioManager::shutdown() {
    if (m_device != 0) {
        SDL_CloseAudioDevice(m_device);
        m_device = 0;
    }
    m_sounds.clear();
    m_ambientBuffer.clear();
    m_playing.clear();
    m_reverbBuffer.clear();
}

bool AudioManager::loadSound(const std::string& name, const std::string& path) {
    SDL_AudioSpec spec;
    Uint8* buf = nullptr;
    Uint32 len = 0;

    if (!SDL_LoadWAV(path.c_str(), &spec, &buf, &len)) {
        std::cerr << "AudioManager: failed to load " << path << ": " << SDL_GetError() << "\n";
        return false;
    }

    // Convert to our format if needed
    SDL_AudioCVT cvt;
    SDL_BuildAudioCVT(&cvt, spec.format, spec.channels, spec.freq,
                       m_spec.format, m_spec.channels, m_spec.freq);

    SoundData sound;
    if (cvt.needed) {
        cvt.len = len;
        sound.buffer.resize(len * cvt.len_mult);
        std::memcpy(sound.buffer.data(), buf, len);
        cvt.buf = sound.buffer.data();
        SDL_ConvertAudio(&cvt);
        sound.buffer.resize(cvt.len_cvt);
    } else {
        sound.buffer.assign(buf, buf + len);
    }
    sound.spec = m_spec;

    SDL_FreeWAV(buf);
    m_sounds[name] = std::move(sound);

    std::cout << "AudioManager: loaded '" << name << "' from " << path << "\n";
    return true;
}

void AudioManager::generateFootstepSound() {
    const int sampleRate = m_spec.freq;
    const int channels = m_spec.channels;
    const float duration = 0.1f; // 100ms
    const int numFrames = static_cast<int>(sampleRate * duration);

    // Random engine for noise
    std::mt19937 rng(std::random_device{}());
    std::uniform_real_distribution<float> noiseDist(-1.0f, 1.0f);

    // Generate mono samples first
    std::vector<float> mono(numFrames);
    for (int i = 0; i < numFrames; i++) {
        float t = static_cast<float>(i) / sampleRate;

        // Low-frequency thud (90 Hz sine burst with fast decay)
        float thud = std::sin(2.0f * static_cast<float>(M_PI) * 90.0f * t) * std::exp(-t * 40.0f);

        // Short noise burst for scrape/texture (decays faster)
        float noise = noiseDist(rng) * std::exp(-t * 60.0f) * 0.3f;

        // Combine with overall envelope
        mono[i] = (thud + noise) * 0.7f;
    }

    // Convert to S16 stereo buffer
    SoundData sound;
    sound.spec = m_spec;
    sound.buffer.resize(numFrames * channels * sizeof(Sint16));
    Sint16* out = reinterpret_cast<Sint16*>(sound.buffer.data());
    for (int i = 0; i < numFrames; i++) {
        Sint16 sample = static_cast<Sint16>(std::clamp(mono[i] * 32767.0f, -32768.0f, 32767.0f));
        for (int c = 0; c < channels; c++) {
            out[i * channels + c] = sample;
        }
    }

    m_sounds["footstep"] = std::move(sound);
    std::cout << "AudioManager: generated procedural footstep (" << numFrames << " frames)\n";
}

void AudioManager::generatePickupSound() {
    const int sampleRate = m_spec.freq;
    const int channels = m_spec.channels;
    const float duration = 0.3f; // 300ms chime
    const int numFrames = static_cast<int>(sampleRate * duration);

    std::vector<float> mono(numFrames);
    for (int i = 0; i < numFrames; i++) {
        float t = static_cast<float>(i) / sampleRate;

        // Two-tone ascending chime (C5 ~523Hz, E5 ~659Hz)
        float env = std::exp(-t * 8.0f);
        float tone1 = std::sin(2.0f * static_cast<float>(M_PI) * 523.0f * t) * env;
        float tone2 = std::sin(2.0f * static_cast<float>(M_PI) * 659.0f * t) * env * 0.7f;

        // Second tone fades in slightly after the first
        float blend = std::min(t * 10.0f, 1.0f);
        mono[i] = (tone1 * (1.0f - blend * 0.3f) + tone2 * blend) * 0.5f;
    }

    SoundData sound;
    sound.spec = m_spec;
    sound.buffer.resize(numFrames * channels * sizeof(Sint16));
    Sint16* out = reinterpret_cast<Sint16*>(sound.buffer.data());
    for (int i = 0; i < numFrames; i++) {
        Sint16 sample = static_cast<Sint16>(std::clamp(mono[i] * 32767.0f, -32768.0f, 32767.0f));
        for (int c = 0; c < channels; c++) {
            out[i * channels + c] = sample;
        }
    }

    m_sounds["pickup"] = std::move(sound);
    std::cout << "AudioManager: generated procedural pickup chime (" << numFrames << " frames)\n";
}

void AudioManager::generateFootstepSound2() {
    const int sampleRate = m_spec.freq;
    const int channels = m_spec.channels;
    const float duration = 0.1f;
    const int numFrames = static_cast<int>(sampleRate * duration);

    std::mt19937 rng(std::random_device{}());
    std::uniform_real_distribution<float> noiseDist(-1.0f, 1.0f);

    std::vector<float> mono(numFrames);
    for (int i = 0; i < numFrames; i++) {
        float t = static_cast<float>(i) / sampleRate;
        float thud = std::sin(2.0f * static_cast<float>(M_PI) * 80.0f * t) * std::exp(-t * 35.0f);
        float noise = noiseDist(rng) * std::exp(-t * 50.0f) * 0.45f;
        mono[i] = (thud + noise) * 0.7f;
    }

    SoundData sound;
    sound.spec = m_spec;
    sound.buffer.resize(numFrames * channels * sizeof(Sint16));
    Sint16* out = reinterpret_cast<Sint16*>(sound.buffer.data());
    for (int i = 0; i < numFrames; i++) {
        Sint16 sample = static_cast<Sint16>(std::clamp(mono[i] * 32767.0f, -32768.0f, 32767.0f));
        for (int c = 0; c < channels; c++) {
            out[i * channels + c] = sample;
        }
    }

    m_sounds["footstep2"] = std::move(sound);
    std::cout << "AudioManager: generated procedural footstep2 (" << numFrames << " frames)\n";
}

void AudioManager::generateDoorOpenSound() {
    const int sampleRate = m_spec.freq;
    const int channels = m_spec.channels;
    const float duration = 0.4f;
    const int numFrames = static_cast<int>(sampleRate * duration);

    std::mt19937 rng(std::random_device{}());
    std::uniform_real_distribution<float> noiseDist(-1.0f, 1.0f);

    std::vector<float> mono(numFrames);
    for (int i = 0; i < numFrames; i++) {
        float t = static_cast<float>(i) / sampleRate;
        // Descending frequency sweep 60Hz -> 40Hz
        float freq = 60.0f - t * 50.0f;
        float sweep = std::sin(2.0f * static_cast<float>(M_PI) * freq * t) * std::exp(-t * 6.0f);
        // Noise burst for texture
        float noise = noiseDist(rng) * std::exp(-t * 12.0f) * 0.3f;
        mono[i] = (sweep + noise) * 0.6f;
    }

    SoundData sound;
    sound.spec = m_spec;
    sound.buffer.resize(numFrames * channels * sizeof(Sint16));
    Sint16* out = reinterpret_cast<Sint16*>(sound.buffer.data());
    for (int i = 0; i < numFrames; i++) {
        Sint16 sample = static_cast<Sint16>(std::clamp(mono[i] * 32767.0f, -32768.0f, 32767.0f));
        for (int c = 0; c < channels; c++) {
            out[i * channels + c] = sample;
        }
    }

    m_sounds["door_open"] = std::move(sound);
    std::cout << "AudioManager: generated procedural door_open (" << numFrames << " frames)\n";
}

void AudioManager::generateLockedSound() {
    const int sampleRate = m_spec.freq;
    const int channels = m_spec.channels;
    const float duration = 0.25f;
    const int numFrames = static_cast<int>(sampleRate * duration);

    std::vector<float> mono(numFrames);
    for (int i = 0; i < numFrames; i++) {
        float t = static_cast<float>(i) / sampleRate;
        // Two quick low thuds
        float thud1 = std::sin(2.0f * static_cast<float>(M_PI) * 70.0f * t) * std::exp(-t * 30.0f);
        float thud2 = 0.0f;
        if (t > 0.1f) {
            float t2 = t - 0.1f;
            thud2 = std::sin(2.0f * static_cast<float>(M_PI) * 60.0f * t2) * std::exp(-t2 * 35.0f) * 0.8f;
        }
        mono[i] = (thud1 + thud2) * 0.7f;
    }

    SoundData sound;
    sound.spec = m_spec;
    sound.buffer.resize(numFrames * channels * sizeof(Sint16));
    Sint16* out = reinterpret_cast<Sint16*>(sound.buffer.data());
    for (int i = 0; i < numFrames; i++) {
        Sint16 sample = static_cast<Sint16>(std::clamp(mono[i] * 32767.0f, -32768.0f, 32767.0f));
        for (int c = 0; c < channels; c++) {
            out[i * channels + c] = sample;
        }
    }

    m_sounds["locked"] = std::move(sound);
    std::cout << "AudioManager: generated procedural locked (" << numFrames << " frames)\n";
}

void AudioManager::generateBookOpenSound() {
    const int sampleRate = m_spec.freq;
    const int channels = m_spec.channels;
    const float duration = 0.15f;
    const int numFrames = static_cast<int>(sampleRate * duration);

    std::mt19937 rng(std::random_device{}());
    std::uniform_real_distribution<float> noiseDist(-1.0f, 1.0f);

    std::vector<float> mono(numFrames);
    for (int i = 0; i < numFrames; i++) {
        float t = static_cast<float>(i) / sampleRate;
        // Soft filtered noise burst (paper rustle)
        float noise = noiseDist(rng);
        // Simple low-pass via exponential decay shaping
        float env = std::exp(-t * 25.0f);
        // Mix with gentle sine for body
        float body = std::sin(2.0f * static_cast<float>(M_PI) * 200.0f * t) * 0.15f * env;
        mono[i] = (noise * 0.4f * env + body) * 0.5f;
    }

    SoundData sound;
    sound.spec = m_spec;
    sound.buffer.resize(numFrames * channels * sizeof(Sint16));
    Sint16* out = reinterpret_cast<Sint16*>(sound.buffer.data());
    for (int i = 0; i < numFrames; i++) {
        Sint16 sample = static_cast<Sint16>(std::clamp(mono[i] * 32767.0f, -32768.0f, 32767.0f));
        for (int c = 0; c < channels; c++) {
            out[i * channels + c] = sample;
        }
    }

    m_sounds["book_open"] = std::move(sound);
    std::cout << "AudioManager: generated procedural book_open (" << numFrames << " frames)\n";
}

void AudioManager::generatePageTurnSound() {
    const int sampleRate = m_spec.freq;
    const int channels = m_spec.channels;
    const float duration = 0.1f;
    const int numFrames = static_cast<int>(sampleRate * duration);

    std::mt19937 rng(std::random_device{}());
    std::uniform_real_distribution<float> noiseDist(-1.0f, 1.0f);

    std::vector<float> mono(numFrames);
    for (int i = 0; i < numFrames; i++) {
        float t = static_cast<float>(i) / sampleRate;
        // Quick high-frequency rustle
        float noise = noiseDist(rng);
        float env = std::exp(-t * 40.0f);
        // Higher frequency content for crispness
        float hi = std::sin(2.0f * static_cast<float>(M_PI) * 3000.0f * t) * 0.1f * env;
        mono[i] = (noise * 0.3f * env + hi) * 0.4f;
    }

    SoundData sound;
    sound.spec = m_spec;
    sound.buffer.resize(numFrames * channels * sizeof(Sint16));
    Sint16* out = reinterpret_cast<Sint16*>(sound.buffer.data());
    for (int i = 0; i < numFrames; i++) {
        Sint16 sample = static_cast<Sint16>(std::clamp(mono[i] * 32767.0f, -32768.0f, 32767.0f));
        for (int c = 0; c < channels; c++) {
            out[i * channels + c] = sample;
        }
    }

    m_sounds["page_turn"] = std::move(sound);
    std::cout << "AudioManager: generated procedural page_turn (" << numFrames << " frames)\n";
}

void AudioManager::generateInventoryOpenSound() {
    const int sampleRate = m_spec.freq;
    const int channels = m_spec.channels;
    const float duration = 0.12f;
    const int numFrames = static_cast<int>(sampleRate * duration);

    std::vector<float> mono(numFrames);
    for (int i = 0; i < numFrames; i++) {
        float t = static_cast<float>(i) / sampleRate;
        // Soft 800Hz sine chime
        float env = std::exp(-t * 20.0f);
        float tone = std::sin(2.0f * static_cast<float>(M_PI) * 800.0f * t) * env;
        mono[i] = tone * 0.35f;
    }

    SoundData sound;
    sound.spec = m_spec;
    sound.buffer.resize(numFrames * channels * sizeof(Sint16));
    Sint16* out = reinterpret_cast<Sint16*>(sound.buffer.data());
    for (int i = 0; i < numFrames; i++) {
        Sint16 sample = static_cast<Sint16>(std::clamp(mono[i] * 32767.0f, -32768.0f, 32767.0f));
        for (int c = 0; c < channels; c++) {
            out[i * channels + c] = sample;
        }
    }

    m_sounds["inventory_open"] = std::move(sound);
    std::cout << "AudioManager: generated procedural inventory_open (" << numFrames << " frames)\n";
}

void AudioManager::playSound(const std::string& name, float volume, float pitch) {
    auto it = m_sounds.find(name);
    if (it == m_sounds.end()) return;

    SDL_LockAudioDevice(m_device);
    PlayingSound ps;
    ps.buffer = &it->second.buffer;
    ps.pos = 0;
    ps.floatPos = 0.0f;
    ps.volumeL = volume;
    ps.volumeR = volume;
    ps.playbackRate = pitch;
    m_playing.push_back(ps);
    SDL_UnlockAudioDevice(m_device);
}

void AudioManager::playSoundAt(const std::string& name, const glm::vec3& sourcePos) {
    auto it = m_sounds.find(name);
    if (it == m_sounds.end()) return;

    // Distance attenuation
    float dist = glm::distance(m_listenerPos, sourcePos);
    float maxDist = 30.0f;
    if (dist > maxDist) return; // too far, don't play
    float volume = std::clamp(1.0f - (dist / maxDist), 0.0f, 1.0f);
    volume *= volume; // quadratic falloff

    // Stereo panning based on listener orientation
    glm::vec3 toSource = sourcePos - m_listenerPos;
    float len = glm::length(toSource);
    float pan = 0.0f;
    if (len > 0.01f) {
        pan = glm::dot(glm::normalize(toSource), m_listenerRight);
        pan = std::clamp(pan, -1.0f, 1.0f);
    }

    float volL = volume * std::clamp(1.0f - pan * 0.5f, 0.2f, 1.0f);
    float volR = volume * std::clamp(1.0f + pan * 0.5f, 0.2f, 1.0f);

    SDL_LockAudioDevice(m_device);
    PlayingSound ps;
    ps.buffer = &it->second.buffer;
    ps.pos = 0;
    ps.floatPos = 0.0f;
    ps.volumeL = volL;
    ps.volumeR = volR;
    ps.playbackRate = 1.0f;
    m_playing.push_back(ps);
    SDL_UnlockAudioDevice(m_device);
}

void AudioManager::setListenerPos(const glm::vec3& pos, const glm::vec3& forward, const glm::vec3& right) {
    m_listenerPos = pos;
    m_listenerForward = forward;
    m_listenerRight = right;
}

bool AudioManager::loadAmbient(const std::string& path) {
    SDL_AudioSpec spec;
    Uint8* buf = nullptr;
    Uint32 len = 0;

    if (!SDL_LoadWAV(path.c_str(), &spec, &buf, &len)) {
        // Gracefully handle missing ambient files
        std::cout << "AudioManager: ambient not found: " << path << " (continuing without)\n";
        return false;
    }

    SDL_AudioCVT cvt;
    SDL_BuildAudioCVT(&cvt, spec.format, spec.channels, spec.freq,
                       m_spec.format, m_spec.channels, m_spec.freq);

    if (cvt.needed) {
        m_ambientBuffer.resize(len * cvt.len_mult);
        std::memcpy(m_ambientBuffer.data(), buf, len);
        cvt.buf = m_ambientBuffer.data();
        cvt.len = len;
        SDL_ConvertAudio(&cvt);
        m_ambientBuffer.resize(cvt.len_cvt);
    } else {
        m_ambientBuffer.assign(buf, buf + len);
    }

    SDL_FreeWAV(buf);
    m_ambientPos = 0;
    std::cout << "AudioManager: loaded ambient from " << path << "\n";
    return true;
}

void AudioManager::playAmbient() { m_ambientPlaying = true; }
void AudioManager::stopAmbient() { m_ambientPlaying = false; }
void AudioManager::setAmbientVolume(float vol) { m_ambientVolume = std::clamp(vol, 0.0f, 1.0f); }
void AudioManager::setMasterVolume(float vol) { m_masterVolume = std::clamp(vol, 0.0f, 1.0f); }
void AudioManager::setSfxVolume(float vol) { m_sfxVolume = std::clamp(vol, 0.0f, 1.0f); }

void AudioManager::playFootstep() {
    static std::mt19937 rng(std::random_device{}());
    static std::uniform_real_distribution<float> volDist(0.35f, 0.55f);
    static std::uniform_real_distribution<float> pitchDist(0.85f, 1.15f);

    float vol = volDist(rng);
    float pitch = pitchDist(rng);
    const std::string& name = m_footstepAlternate ? "footstep2" : "footstep";
    m_footstepAlternate = !m_footstepAlternate;
    playSound(name, vol, pitch);
}

void AudioManager::updateFootsteps(float dt, bool isMoving) {
    if (!isMoving) {
        m_footstepTimer = m_footstepInterval; // ready for next step
        return;
    }

    m_footstepTimer += dt;
    if (m_footstepTimer >= m_footstepInterval) {
        m_footstepTimer = 0.0f;
        playFootstep();
    }
}

void AudioManager::setReverb(bool enabled, float feedback, float delayMs) {
    // Early-return if nothing changed — avoids SDL lock overhead
    if (enabled == m_reverbEnabled && feedback == m_reverbFeedback && delayMs == m_reverbDelayMs) {
        return;
    }

    SDL_LockAudioDevice(m_device);
    m_reverbEnabled = enabled;
    m_reverbFeedback = std::clamp(feedback, 0.0f, 0.8f);
    m_reverbDelayMs = delayMs;
    size_t newDelay = static_cast<size_t>(m_spec.freq * (delayMs / 1000.0f)) * m_spec.channels;
    if (newDelay != m_reverbDelaySamples) {
        m_reverbDelaySamples = newDelay;
        m_reverbBuffer.assign(m_reverbDelaySamples, 0.0f);
        m_reverbPos = 0;
    }
    SDL_UnlockAudioDevice(m_device);
}

void AudioManager::audioCallback(void* userdata, Uint8* stream, int len) {
    auto* self = static_cast<AudioManager*>(userdata);
    self->mixAudio(stream, len);
}

void AudioManager::mixAudio(Uint8* stream, int len) {
    std::memset(stream, 0, len);

    // Mix ambient loop with crossfade at loop boundary
    if (m_ambientPlaying && !m_ambientBuffer.empty()) {
        const size_t bufSize = m_ambientBuffer.size();
        // Crossfade region: ~4096 stereo samples worth of bytes
        const size_t crossfadeBytes = std::min(static_cast<size_t>(4096 * m_spec.channels * sizeof(Sint16)), bufSize / 4);
        const size_t crossfadeStart = bufSize - crossfadeBytes;

        int remaining = len;
        int offset = 0;
        while (remaining > 0) {
            int available = static_cast<int>(bufSize - m_ambientPos);
            int toMix = std::min(remaining, available);

            // Check if we're in the crossfade region near the end
            if (m_ambientPos >= crossfadeStart) {
                // Manual mix with crossfade: blend end of buffer with beginning
                const Sint16* endSrc = reinterpret_cast<const Sint16*>(m_ambientBuffer.data() + m_ambientPos);
                const Sint16* startSrc = reinterpret_cast<const Sint16*>(m_ambientBuffer.data());
                Sint16* dst = reinterpret_cast<Sint16*>(stream + offset);
                int samplesToMix = toMix / static_cast<int>(sizeof(Sint16));

                for (int s = 0; s < samplesToMix; s++) {
                    size_t posInCrossfade = (m_ambientPos - crossfadeStart) + s * sizeof(Sint16);
                    float fade = static_cast<float>(posInCrossfade) / static_cast<float>(crossfadeBytes);
                    fade = std::clamp(fade, 0.0f, 1.0f);

                    size_t startIdx = s;
                    float endVal = static_cast<float>(endSrc[s]);
                    float startVal = (startIdx < bufSize / sizeof(Sint16)) ? static_cast<float>(startSrc[startIdx]) : 0.0f;
                    float blended = endVal * (1.0f - fade) + startVal * fade;
                    float vol = m_ambientVolume * m_masterVolume;
                    int mixed = static_cast<int>(dst[s]) + static_cast<int>(blended * vol);
                    dst[s] = static_cast<Sint16>(std::clamp(mixed, -32768, 32767));
                }
            } else {
                SDL_MixAudioFormat(stream + offset, m_ambientBuffer.data() + m_ambientPos,
                                   m_spec.format, toMix, static_cast<int>(m_ambientVolume * m_masterVolume * SDL_MIX_MAXVOLUME));
            }

            m_ambientPos += toMix;
            offset += toMix;
            remaining -= toMix;
            if (m_ambientPos >= bufSize) {
                m_ambientPos = 0; // loop (crossfade handled above)
            }
        }
    }

    // Mix one-shot sounds (with per-sound volume and pitch variation)
    const int outFrames = len / (m_spec.channels * sizeof(Sint16));
    Sint16* dst = reinterpret_cast<Sint16*>(stream);

    for (auto it = m_playing.begin(); it != m_playing.end();) {
        const Sint16* src = reinterpret_cast<const Sint16*>(it->buffer->data());
        const int srcTotalFrames = static_cast<int>(it->buffer->size()) / (m_spec.channels * sizeof(Sint16));
        bool done = false;

        for (int f = 0; f < outFrames && !done; f++) {
            int idx0 = static_cast<int>(it->floatPos);
            if (idx0 >= srcTotalFrames - 1) { done = true; break; }

            float frac = it->floatPos - static_cast<float>(idx0);
            int idx1 = std::min(idx0 + 1, srcTotalFrames - 1);

            for (int c = 0; c < m_spec.channels; c++) {
                // Linear interpolation between adjacent frames
                float s0 = static_cast<float>(src[idx0 * m_spec.channels + c]);
                float s1 = static_cast<float>(src[idx1 * m_spec.channels + c]);
                float sample = s0 + (s1 - s0) * frac;

                // Apply volume (L/R) scaled by SFX and master volume
                float vol = (c == 0) ? it->volumeL : it->volumeR;
                sample *= vol * m_sfxVolume * m_masterVolume;

                // Mix into output
                int mixed = static_cast<int>(dst[f * m_spec.channels + c]) + static_cast<int>(sample);
                dst[f * m_spec.channels + c] = static_cast<Sint16>(std::clamp(mixed, -32768, 32767));
            }

            it->floatPos += it->playbackRate;
        }

        if (done || it->floatPos >= static_cast<float>(srcTotalFrames - 1)) {
            it = m_playing.erase(it);
        } else {
            ++it;
        }
    }

    // Apply simple delay-line reverb (on the mixed output)
    if (m_reverbEnabled && !m_reverbBuffer.empty()) {
        int numSamples = len / 2; // S16 = 2 bytes per sample
        Sint16* samples = reinterpret_cast<Sint16*>(stream);
        for (int i = 0; i < numSamples; i++) {
            float dry = static_cast<float>(samples[i]);
            float delayed = m_reverbBuffer[m_reverbPos];
            float wet = dry + delayed * m_reverbFeedback;
            // Clamp to S16 range
            wet = std::clamp(wet, -32768.0f, 32767.0f);
            samples[i] = static_cast<Sint16>(wet);
            m_reverbBuffer[m_reverbPos] = dry;
            m_reverbPos = (m_reverbPos + 1) % m_reverbBuffer.size();
        }
    }
}

} // namespace dw
