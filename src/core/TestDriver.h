#pragma once

#ifdef DW_TEST_DRIVER

#include <SDL.h>
#include <string>
#include <vector>

namespace dw {

// True once a script is loaded; lets Scene skip the mouse grab.
inline bool g_testDriverActive = false;

class Engine;
class InputManager;

// Runs a script of input and capture commands against the live game.
// Only compiled when the build option DW_TEST_DRIVER is on.
class TestDriver {
public:
    bool load(const std::string& path);

    // Called right after processEvents: injects keys and mouse motion.
    void beforeUpdate(InputManager& input);
    // Called right before SDL_GL_SwapWindow: captures and logs.
    void afterRender(Engine& engine);

private:
    struct Command {
        std::string name;
        std::vector<std::string> args;
    };

    static bool isObservation(const std::string& name);
    void run(const Command& cmd, InputManager* input, Engine* engine);
    void quit();

    std::vector<Command> m_commands;
    size_t m_next = 0;

    bool m_waiting = false;
    Uint32 m_waitStart = 0;
    std::vector<SDL_Scancode> m_pendingUp;

    Uint32 m_startTicks = 0;
    unsigned m_frames = 0;
};

} // namespace dw

#endif
