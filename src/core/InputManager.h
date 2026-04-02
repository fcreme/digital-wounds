#pragma once

#include <SDL.h>
#include <unordered_set>

namespace dw {

class InputManager {
public:
    void preUpdate();

    void onKeyDown(SDL_Scancode key);
    void onKeyUp(SDL_Scancode key);
    void onMouseMove(int xrel, int yrel);
    void onMouseDown(Uint8 button);
    void onMouseUp(Uint8 button);

    bool isKeyDown(SDL_Scancode key) const;
    bool isKeyPressed(SDL_Scancode key) const;  // just this frame
    bool isMouseDown(Uint8 button) const;

    int getMouseDeltaX() const { return m_mouseDX; }
    int getMouseDeltaY() const { return m_mouseDY; }

private:
    std::unordered_set<SDL_Scancode> m_keysDown;
    std::unordered_set<SDL_Scancode> m_keysPressed;
    std::unordered_set<Uint8> m_mouseDown;

    int m_mouseDX = 0;
    int m_mouseDY = 0;
};

} // namespace dw
