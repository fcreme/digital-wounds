#pragma once

#include <SDL.h>
#include <string>
#include <vector>
#include <unordered_map>

namespace dw {

class AudioManager {
public:
    AudioManager() = default;
    ~AudioManager() = default;

    bool init();
    void shutdown();

    // Load a WAV file and store it by name
    bool loadSound(const std::string& name, const std::string& path);

    // Play a sound (one-shot)
    void playSound(const std::string& name);

    // Ambient loop (only one ambient at a time)
    bool loadAmbient(const std::string& path);
    void playAmbient();
    void stopAmbient();
    void setAmbientVolume(float vol); // 0..1

    // Footsteps
    void playFootstep();
    void setFootstepInterval(float seconds) { m_footstepInterval = seconds; }
    void updateFootsteps(float dt, bool isMoving);

private:
    static void audioCallback(void* userdata, Uint8* stream, int len);
    void mixAudio(Uint8* stream, int len);

    SDL_AudioDeviceID m_device = 0;
    SDL_AudioSpec m_spec{};

    struct SoundData {
        std::vector<Uint8> buffer;
        SDL_AudioSpec spec;
    };

    std::unordered_map<std::string, SoundData> m_sounds;

    // Ambient
    std::vector<Uint8> m_ambientBuffer;
    size_t m_ambientPos = 0;
    bool m_ambientPlaying = false;
    float m_ambientVolume = 0.3f;

    // One-shot playback tracking
    struct PlayingSound {
        const std::vector<Uint8>* buffer;
        size_t pos;
    };
    std::vector<PlayingSound> m_playing;

    // Footsteps
    float m_footstepTimer = 0.0f;
    float m_footstepInterval = 0.4f;
};

} // namespace dw
