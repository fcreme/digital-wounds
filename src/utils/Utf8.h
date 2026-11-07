#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace dw {

constexpr uint32_t UTF8_REPLACEMENT = 0xFFFD;

// Decodes UTF-8. Each malformed byte becomes one UTF8_REPLACEMENT.
std::vector<uint32_t> decodeUtf8(const std::string& s);
std::string encodeUtf8(uint32_t cp);
bool isValidUtf8(const std::string& s);

// The characters the UI font draws: printable ASCII and the Latin-1 letters and signs
// (accents such as é, ñ, ü, plus ¡ ¿ « » and the like).
inline bool isUiDrawable(uint32_t cp) { return (cp >= 32 && cp <= 126) || (cp >= 160 && cp <= 255); }

// Upper case for ASCII and Latin-1 letters; everything else is kept as it is.
std::string upperLatin1(const std::string& utf8);

// The longest prefix of s that is at most maxBytes long and does not end inside a
// multi-byte character.
std::string truncateUtf8(const std::string& s, size_t maxBytes);

} // namespace dw
