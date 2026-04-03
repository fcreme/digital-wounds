#include "audio/AudioManager.h"

#include <cstring>
#include <iostream>
#include <algorithm>
#include <cmath>

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

void AudioManager::playSound(const std::string& name) {
    auto it = m_sounds.find(name);
    if (it == m_sounds.end()) return;

    SDL_LockAudioDevice(m_device);
    m_playing.push_back({&it->second.buffer, 0, 1.0f, 1.0f});
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
    m_playing.push_back({&it->second.buffer, 0, volL, volR});
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

void AudioManager::playFootstep() {
    playSound("footstep");
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
    SDL_LockAudioDevice(m_device);
    m_reverbEnabled = enabled;
    m_reverbFeedback = std::clamp(feedback, 0.0f, 0.8f);
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

    // Mix ambient loop
    if (m_ambientPlaying && !m_ambientBuffer.empty()) {
        int remaining = len;
        int offset = 0;
        while (remaining > 0) {
            int available = static_cast<int>(m_ambientBuffer.size() - m_ambientPos);
            int toMix = std::min(remaining, available);
            SDL_MixAudioFormat(stream + offset, m_ambientBuffer.data() + m_ambientPos,
                               m_spec.format, toMix, static_cast<int>(m_ambientVolume * SDL_MIX_MAXVOLUME));
            m_ambientPos += toMix;
            offset += toMix;
            remaining -= toMix;
            if (m_ambientPos >= m_ambientBuffer.size()) {
                m_ambientPos = 0; // loop
            }
        }
    }

    // Mix one-shot sounds (with per-sound spatial volume)
    for (auto it = m_playing.begin(); it != m_playing.end();) {
        int remaining = static_cast<int>(it->buffer->size() - it->pos);
        int toMix = std::min(len, remaining);

        // Apply spatial volume per-sample (stereo interleaved: L R L R ...)
        if (m_spec.channels == 2 && (it->volumeL < 0.99f || it->volumeR < 0.99f)) {
            // Mix with spatial panning
            int numFrames = toMix / (2 * sizeof(Sint16));
            const Sint16* src = reinterpret_cast<const Sint16*>(it->buffer->data() + it->pos);
            Sint16* dst = reinterpret_cast<Sint16*>(stream);
            for (int f = 0; f < numFrames; f++) {
                dst[f * 2] = static_cast<Sint16>(std::clamp(
                    static_cast<int>(dst[f * 2]) + static_cast<int>(src[f * 2] * it->volumeL * 0.5f),
                    -32768, 32767));
                dst[f * 2 + 1] = static_cast<Sint16>(std::clamp(
                    static_cast<int>(dst[f * 2 + 1]) + static_cast<int>(src[f * 2 + 1] * it->volumeR * 0.5f),
                    -32768, 32767));
            }
        } else {
            SDL_MixAudioFormat(stream, it->buffer->data() + it->pos,
                               m_spec.format, toMix, SDL_MIX_MAXVOLUME / 2);
        }

        it->pos += toMix;
        if (it->pos >= it->buffer->size()) {
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
