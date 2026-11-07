#include "test_util.h"

TEST(harness_runs) {
    CHECK(1 + 1 == 2);
}

int main() {
    for (auto& c : dwtest::registry()) {
        int before = dwtest::failures();
        c.fn();
        std::cout << (dwtest::failures() == before ? "PASS " : "FAIL ") << c.name << "\n";
    }
    return dwtest::failures() == 0 ? 0 : 1;
}
