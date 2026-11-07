#pragma once

#include <functional>
#include <iostream>
#include <string>
#include <vector>

namespace dwtest {

struct Case {
    std::string name;
    std::function<void()> fn;
};

inline std::vector<Case>& registry() {
    static std::vector<Case> cases;
    return cases;
}

inline int& failures() {
    static int n = 0;
    return n;
}

struct Registrar {
    Registrar(const char* name, std::function<void()> fn) { registry().push_back({name, std::move(fn)}); }
};

} // namespace dwtest

#define TEST(name)                                                              \
    static void test_##name();                                                  \
    static dwtest::Registrar registrar_##name(#name, test_##name);              \
    static void test_##name()

#define CHECK(cond)                                                             \
    do {                                                                        \
        if (!(cond)) {                                                          \
            ++dwtest::failures();                                               \
            std::cerr << __FILE__ << ":" << __LINE__ << ": CHECK failed: "      \
                      << #cond << "\n";                                         \
        }                                                                       \
    } while (0)
