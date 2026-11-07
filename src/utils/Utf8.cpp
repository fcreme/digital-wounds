#include "utils/Utf8.h"

namespace dw {

namespace {

// Length of the sequence starting at s[i] and its code point, or 0 if malformed.
size_t decodeOne(const std::string& s, size_t i, uint32_t& cp) {
    const auto b = [&](size_t k) { return static_cast<unsigned char>(s[k]); };
    const unsigned char c = b(i);
    size_t len;
    uint32_t minCp;
    if (c < 0x80) { cp = c; return 1; }
    if ((c & 0xE0) == 0xC0) { len = 2; cp = c & 0x1F; minCp = 0x80; }
    else if ((c & 0xF0) == 0xE0) { len = 3; cp = c & 0x0F; minCp = 0x800; }
    else if ((c & 0xF8) == 0xF0) { len = 4; cp = c & 0x07; minCp = 0x10000; }
    else return 0;
    if (i + len > s.size()) return 0;
    for (size_t k = 1; k < len; k++) {
        if ((b(i + k) & 0xC0) != 0x80) return 0;
        cp = (cp << 6) | (b(i + k) & 0x3F);
    }
    if (cp < minCp || cp > 0x10FFFF || (cp >= 0xD800 && cp <= 0xDFFF)) return 0;
    return len;
}

} // anonymous namespace

std::vector<uint32_t> decodeUtf8(const std::string& s) {
    std::vector<uint32_t> out;
    out.reserve(s.size());
    for (size_t i = 0; i < s.size();) {
        uint32_t cp = 0;
        const size_t len = decodeOne(s, i, cp);
        if (len == 0) { out.push_back(UTF8_REPLACEMENT); i++; }
        else { out.push_back(cp); i += len; }
    }
    return out;
}

std::string encodeUtf8(uint32_t cp) {
    std::string out;
    if (cp < 0x80) {
        out += static_cast<char>(cp);
    } else if (cp < 0x800) {
        out += static_cast<char>(0xC0 | (cp >> 6));
        out += static_cast<char>(0x80 | (cp & 0x3F));
    } else if (cp < 0x10000) {
        out += static_cast<char>(0xE0 | (cp >> 12));
        out += static_cast<char>(0x80 | ((cp >> 6) & 0x3F));
        out += static_cast<char>(0x80 | (cp & 0x3F));
    } else {
        out += static_cast<char>(0xF0 | (cp >> 18));
        out += static_cast<char>(0x80 | ((cp >> 12) & 0x3F));
        out += static_cast<char>(0x80 | ((cp >> 6) & 0x3F));
        out += static_cast<char>(0x80 | (cp & 0x3F));
    }
    return out;
}

bool isValidUtf8(const std::string& s) {
    for (size_t i = 0; i < s.size();) {
        uint32_t cp = 0;
        const size_t len = decodeOne(s, i, cp);
        if (len == 0) return false;
        i += len;
    }
    return true;
}

std::string upperLatin1(const std::string& utf8) {
    std::string out;
    for (uint32_t cp : decodeUtf8(utf8)) {
        if (cp >= 'a' && cp <= 'z') cp -= 32;
        // à..þ except ÷. ß and ÿ stay: their capitals are outside the UI font.
        else if (cp >= 0xE0 && cp <= 0xFE && cp != 0xF7) cp -= 32;
        out += encodeUtf8(cp);
    }
    return out;
}

std::string truncateUtf8(const std::string& s, size_t maxBytes) {
    if (s.size() <= maxBytes) return s;
    size_t end = maxBytes;
    // s[end] is the first byte cut off. If it continues a character, step back to that
    // character's first byte so the whole character goes.
    while (end > 0 && (static_cast<unsigned char>(s[end]) & 0xC0) == 0x80) end--;
    return s.substr(0, end);
}

} // namespace dw
