// Released under the MIT licence. Decode the existing GBK translation safely.
#pragma once
#include <stddef.h>
#include <iconv.h>

inline unsigned long ChineseToUnicode(const unsigned char *text, size_t remaining, size_t *consumed)
{
    *consumed = remaining ? 1 : 0;
    if (!remaining) return 0xFFFD;
    if (text[0] < 0x80) return text[0];
    if (remaining < 2 || text[0] < 0x81 || text[0] > 0xFE ||
        text[1] < 0x40 || text[1] > 0xFE || text[1] == 0x7F) return 0xFFFD;
    struct Converter {
        iconv_t handle;
        Converter() : handle(iconv_open("UTF-32LE", "GBK")) {}
        ~Converter() { if (handle != (iconv_t)-1) iconv_close(handle); }
    };
    static Converter converter; // Rendering runs on the game's main thread.
    if (converter.handle == (iconv_t)-1) return 0xFFFD;
    char input[2] = { (char)text[0], (char)text[1] };
    unsigned char output[4] = {};
    char *in = input, *out = (char*)output;
    size_t in_left = 2, out_left = 4;
    iconv(converter.handle, NULL, NULL, NULL, NULL);
    *consumed = 2;
    if (iconv(converter.handle, &in, &in_left, &out, &out_left) == (size_t)-1 || out_left)
        return 0xFFFD;
    return output[0] | ((unsigned long)output[1] << 8) |
        ((unsigned long)output[2] << 16) | ((unsigned long)output[3] << 24);
}
