#include "core/Engine.h"
#include <cstdlib>
#include <iostream>

int main(int argc, char* argv[]) {
    (void)argc;
    (void)argv;

    dw::Engine engine;

    if (!engine.init("Digital Wounds", 1280, 720)) {
        std::cerr << "Failed to initialize engine\n";
        return EXIT_FAILURE;
    }

    engine.run();
    engine.shutdown();

    return EXIT_SUCCESS;
}
