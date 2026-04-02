#include "core/InputManager.h"

namespace dw {

void InputManager::preUpdate() {
    m_keysPressed.clear();
    m_mouseDX = 0;
    m_mouseDY = 0;
}

void InputManager::onKeyDown(SDL_Scancode key) {
    if (m_keysDown.find(key) == m_keysDown.end()) {
        m_keysPressed.insert(key);
    }
    m_keysDown.insert(key);
}

void InputManager::onKeyUp(SDL_Scancode key) {
    m_keysDown.erase(key);
}

void InputManager::onMouseMove(int xrel, int yrel) {
    m_mouseDX += xrel;
    m_mouseDY += yrel;
}

void InputManager::onMouseDown(Uint8 button) {
    m_mouseDown.insert(button);
}

void InputManager::onMouseUp(Uint8 button) {
    m_mouseDown.erase(button);
}

bool InputManager::isKeyDown(SDL_Scancode key) const {
    return m_keysDown.count(key) > 0;
}

bool InputManager::isKeyPressed(SDL_Scancode key) const {
    return m_keysPressed.count(key) > 0;
}

bool InputManager::isMouseDown(Uint8 button) const {
    return m_mouseDown.count(button) > 0;
}

} // namespace dw
