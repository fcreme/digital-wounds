#pragma once

#include <iostream>
#include <string>

namespace dw {
namespace Log {

inline void info(const std::string& msg) {
    std::cout << "[INFO] " << msg << "\n";
}

inline void warn(const std::string& msg) {
    std::cerr << "[WARN] " << msg << "\n";
}

inline void error(const std::string& msg) {
    std::cerr << "[ERROR] " << msg << "\n";
}

} // namespace Log
} // namespace dw
