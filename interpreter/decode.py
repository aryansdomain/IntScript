from __future__ import annotations
from typing import List

from interpreter.interpreter import (
    MOVE, CADD, SET, ADD, SUB, COPY, SWAP, LOOP,
    IFZ, OUT, IN, MUL, CMUL, DIV, CDIV
)

def unsigned_to_signed(u: int) -> int:
    # ZigZag
    if (u % 2) == 0: return u // 2
    else:            return -(u + 1) // 2

def golomb_decode(bits: str, m: int) -> tuple[int, int]:
    i = 0
    q = 0
    while bits[i] == "0":
        q += 1
        i += 1
    i += 1  # read the '1'

    k = (m - 1).bit_length()
    t = (1 << k) - m

    if k == 0:
        r = 0
    else:
        x_bits = k - 1
        x = int(bits[i:i + x_bits], 2) if x_bits > 0 else 0
        if x < t:
            r = x
            i += x_bits
        else:
            x = int(bits[i:i + k], 2)
            r = x - t
            i += k

    u = q * m + r
    return unsigned_to_signed(u), i


def decode_block(bits: str, m: int, start: int = 0) -> tuple[List, int]:
    block = []
    i = start

    while i < len(bits):
        # read command
        cmd = bits[i:i+4]
        i += 4

        # read arguments
        if cmd not in {"0010", "0011"}: # exclude IN and OUT
            if cmd in {"0100", "1100"}: # loop commands
                body, i = decode_block(bits, m, i)
            else:
                k, used = golomb_decode(bits[i:], m)
                i += used

        match cmd:
            case "0000": block.append(MOVE(k))
            case "0001": block.append(CADD(k))
            case "0010": block.append(IN())
            case "0011": block.append(OUT())
            case "0100": block.append(LOOP(body))
            case "0101": block.append(COPY(k))
            case "0110": block.append(SET(k))
            case "0111": block.append(MUL(k))
            case "1000": block.append(DIV(k))
            case "1001": block.append(ADD(k))
            case "1010": block.append(SUB(k))
            case "1011": block.append(SWAP(k))
            case "1100": block.append(IFZ(body))
            case "1101": block.append(CMUL(k))
            case "1110": block.append(CDIV(k))
            case "1111": return block, i

    return block, i

def decode(n: int) -> List:
    binary = bin(n)[3:] # remove "0b" and leading 1
    m = int(binary[0:4], 2) + 1 # get golomb parameter

    return decode_block(binary[4:], m)[0]
