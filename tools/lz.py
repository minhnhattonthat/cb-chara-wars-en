"""The game's LZ codec (decompressor at $00:F7B4; see docs/re/README.md §LZ).

Stream: byte M (bit7 = extended-length flag, low 7 bits = min match length), word N = output size,
then groups: flag byte read LSB first; bit 1 = literal byte, bit 0 = 16-bit word W:
length = (W >> 12) + M (+ next byte if W >> 12 == 15 and extended), distance = (W & 0xFFF) + 1.
Copies are byte-by-byte (MVN), so overlapping matches repeat. Stops when N bytes are written.

    python -X utf8 tools/lz.py ROM OFFSET OUT.bin     # decompress one block (prints consumed bytes)
"""
import sys


def decompress(data, pos=0):
    """Returns (output bytes, bytes consumed)."""
    start = pos
    m = data[pos]
    ext = bool(m & 0x80)
    m &= 0x7F
    size = data[pos + 1] | data[pos + 2] << 8
    pos += 3
    out = bytearray()
    bits = 0
    nbits = 8
    while len(out) < size:
        if nbits == 8:
            bits, nbits = data[pos], 0
            pos += 1
        nbits += 1
        lit = bits & 1
        bits >>= 1
        if lit:
            out.append(data[pos])
            pos += 1
            continue
        w = data[pos] | data[pos + 1] << 8
        pos += 2
        n = w >> 12
        length = n + m
        if n == 15 and ext:
            length += data[pos]
            pos += 1
        src = len(out) - ((w & 0xFFF) + 1)
        length = min(length, size - len(out))
        for i in range(length):
            out.append(out[src + i])
    return bytes(out), pos - start


def compress(data, m=3):
    """Greedy LZ in the game's format (extended lengths on). Not optimal, always valid."""
    out = bytearray([0x80 | m, len(data) & 0xFF, len(data) >> 8])
    i = 0
    maxlen = m + 15 + 255
    while i < len(data):
        flag_pos = len(out)
        out.append(0)
        flag = 0
        for bit in range(8):
            if i >= len(data):
                break
            best_len, best_dist = 0, 0
            lo = max(0, i - 4096)
            for j in range(i - 1, lo - 1, -1):
                k = 0
                while k < maxlen and i + k < len(data) and data[j + k] == data[i + k]:
                    k += 1
                if k > best_len:
                    best_len, best_dist = k, i - j
                    if k == maxlen:
                        break
            if best_len >= m:
                n = min(best_len - m, 15)
                out += ((n << 12) | (best_dist - 1)).to_bytes(2, "little")
                if n == 15:
                    best_len = min(best_len, maxlen)
                    out.append(best_len - m - 15)
                i += best_len
            else:
                flag |= 1 << bit
                out.append(data[i])
                i += 1
        out[flag_pos] = flag
    return bytes(out)


if __name__ == "__main__":
    rom = open(sys.argv[1], "rb").read()
    dec, used = decompress(rom, int(sys.argv[2], 16))
    open(sys.argv[3], "wb").write(dec)
    print(f"{len(dec):#x} bytes out, {used:#x} consumed")
