#include "core/Engine.h"
#include <cstdlib>
#include <iostream>
#include <string>

int main(int argc, char* argv[]) {
    dw::Engine engine;

    for (int i = 1; i + 1 < argc; ++i) {
        if (std::string(argv[i]) == "--script") engine.setScriptPath(argv[i + 1]);
    }

    if (!engine.init("Digital Wounds", 1280, 720)) {
        std::cerr << "Failed to initialize engine\n";
        return EXIT_FAILURE;
    }

    engine.run();
    engine.shutdown();

    return EXIT_SUCCESS;
}
