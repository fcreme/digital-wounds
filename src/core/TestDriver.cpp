#ifdef DW_TEST_DRIVER

#include "core/TestDriver.h"
#include "core/Engine.h"
#include "core/InputManager.h"
#include "scene/Scene.h"
#include "renderer/Camera.h"

#include <glad/gl.h>
#include <SDL.h>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>

namespace dw {

bool TestDriver::load(const std::string& path) {
    std::ifstream in(path);
    if (!in) {
        std::cerr << "DRIVER cannot open script " << path << "\n";
        return false;
    }
    std::string line;
    while (std::getline(in, line)) {
        auto hash = line.find('#');
        if (hash != std::string::npos) line.erase(hash);
        std::istringstream ss(line);
        Command cmd;
        if (!(ss >> cmd.name)) continue;
        std::string arg;
        while (ss >> arg) cmd.args.push_back(arg);
        m_commands.push_back(std::move(cmd));
    }
    g_testDriverActive = true;
    m_startTicks = SDL_GetTicks();
    std::cout << "DRIVER loaded " << m_commands.size() << " commands from " << path << "\n";
    return true;
}

bool TestDriver::isObservation(const std::string& name) {
    return name == "shot" || name == "pos" || name == "state" || name == "sizes" || name == "fps";
}

void TestDriver::quit() {
    SDL_Event e{};
    e.type = SDL_QUIT;
    SDL_PushEvent(&e);
    m_next = m_commands.size();
}

void TestDriver::beforeUpdate(InputManager& input) {
    for (SDL_Scancode sc : m_pendingUp) input.onKeyUp(sc);
    m_pendingUp.clear();

    while (m_next < m_commands.size()) {
        const Command& cmd = m_commands[m_next];
        if (isObservation(cmd.name)) return;
        if (cmd.name == "wait") {
            double secs = cmd.args.empty() ? 0.0 : std::atof(cmd.args[0].c_str());
            if (!m_waiting) {
                m_waiting = true;
                m_waitStart = SDL_GetTicks();
            }
            if ((SDL_GetTicks() - m_waitStart) / 1000.0 < secs) return;
            m_waiting = false;
            ++m_next;
            continue;
        }
        ++m_next;
        run(cmd, &input, nullptr);
        // Key and mouse commands each take a frame, so repeats are distinct events.
        if (cmd.name == "key" || cmd.name == "mouse") return;
    }
}

void TestDriver::afterRender(Engine& engine) {
    ++m_frames;
    while (m_next < m_commands.size() && isObservation(m_commands[m_next].name)) {
        run(m_commands[m_next], nullptr, &engine);
        ++m_next;
    }
}

void TestDriver::run(const Command& cmd, InputManager* input, Engine* engine) {
    const std::string& n = cmd.name;
    auto arg = [&](size_t i) { return i < cmd.args.size() ? cmd.args[i] : std::string(); };

    if (n == "quit") {
        quit();
    } else if (n == "key" && input) {
        SDL_Scancode sc = SDL_GetScancodeFromName(arg(1).c_str());
        if (sc == SDL_SCANCODE_UNKNOWN) {
            std::cerr << "DRIVER unknown scancode '" << arg(1) << "'\n";
            return;
        }
        const std::string mode = arg(0);
        if (mode == "down") {
            input->onKeyDown(sc);
        } else if (mode == "up") {
            input->onKeyUp(sc);
        } else if (mode == "tap") {
            input->onKeyDown(sc);
            m_pendingUp.push_back(sc);
        } else {
            std::cerr << "DRIVER bad key mode '" << mode << "'\n";
        }
    } else if (n == "mouse" && input) {
        input->onMouseMove(std::atoi(arg(0).c_str()), std::atoi(arg(1).c_str()));
    } else if (n == "sizes" && engine) {
        int dw = 0, dh = 0;
        SDL_GL_GetDrawableSize(engine->m_window, &dw, &dh);
        std::cout << "DRIVER sizes window=" << engine->m_windowWidth << "x" << engine->m_windowHeight
                  << " drawable=" << dw << "x" << dh
                  << " mouse_grab=" << (SDL_GetRelativeMouseMode() ? "on" : "off") << "\n";
    } else if (n == "fps" && engine) {
        double secs = (SDL_GetTicks() - m_startTicks) / 1000.0;
        std::cout << "DRIVER fps " << (secs > 0 ? m_frames / secs : 0.0) << " (" << m_frames
                  << " frames in " << secs << " s)\n";
    } else if (n == "pos" && engine) {
        const auto& p = engine->m_scene->getCamera().getPosition();
        std::cout << "DRIVER pos " << arg(0) << " x=" << p.x << " z=" << p.z << "\n";
    } else if (n == "state" && engine) {
        // Painting and artist state arrive with the discovery feature.
        std::cout << "DRIVER state " << arg(0) << " near=none view=closed artist=none page=0\n";
    } else if (n == "shot" && engine) {
        int w = 0, h = 0;
        SDL_GL_GetDrawableSize(engine->m_window, &w, &h);
        std::vector<unsigned char> px(static_cast<size_t>(w) * h * 4);
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        glReadBuffer(GL_BACK);
        glPixelStorei(GL_PACK_ALIGNMENT, 1);
        glReadPixels(0, 0, w, h, GL_RGBA, GL_UNSIGNED_BYTE, px.data());
        // OpenGL rows run bottom to top; flip them for the image.
        std::vector<unsigned char> flipped(px.size());
        for (int y = 0; y < h; ++y)
            std::copy_n(&px[static_cast<size_t>(h - 1 - y) * w * 4], static_cast<size_t>(w) * 4,
                        &flipped[static_cast<size_t>(y) * w * 4]);
        std::filesystem::create_directories("shots");
        std::string file = "shots/" + arg(0) + ".bmp";
        SDL_Surface* s = SDL_CreateRGBSurfaceWithFormatFrom(flipped.data(), w, h, 32, w * 4,
                                                            SDL_PIXELFORMAT_RGBA32);
        if (s && SDL_SaveBMP(s, file.c_str()) == 0)
            std::cout << "DRIVER shot " << file << " " << w << "x" << h << "\n";
        else
            std::cerr << "DRIVER shot failed: " << SDL_GetError() << "\n";
        if (s) SDL_FreeSurface(s);
    } else {
        std::cerr << "DRIVER unknown command '" << n << "'\n";
    }
}

} // namespace dw

#endif
