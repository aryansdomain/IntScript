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

    # read quotient
    i = 0
    q = 0
    while bits[i] == "0":
        q += 1
        i += 1
    i += 1  # read the '1'

    # read remainder
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

    # construct unsigned
    u = q * m + r
    return unsigned_to_signed(u), i


def decode_block(bits: str, m: int, use_normal_alphabet: bool, start: int = 0) -> tuple[List, int]:
    block = []
    i = start

    if use_normal_alphabet:
        while i < len(bits):
            # read command
            cmd = bits[i:i+4]
            i += 4

            # read argument
            if cmd not in {"0010", "0011", "1111"}: # exclude IN, OUT, end block
                if cmd in {"0100", "1100"}: # loop commands
                    body, i = decode_block(bits, m, use_normal_alphabet, i)
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

    else:
        while i < len(bits):
            # read command
            cmd = bits[i:i+5]
            i += 5

            if cmd == "11111":
                return block, i
            
            # read argument
            if cmd not in {"01010", "01011", "11111"}: # exclude IN, OUT, end block
                if cmd in {"01100", "11100"}: # loop commands
                    body, i = decode_block(bits, m, use_normal_alphabet, i)
                elif cmd in {
                    "00110", "01001", "10000", "10001", "10010", "10011",
                    "10110", "11001", "11011", "11101", "11110"
                }: # has argument
                    k, used = golomb_decode(bits[i:], m)
                    i += used

            if   cmd == "00000": block.append(MOVE(1))
            elif cmd == "00001": block.append(MOVE(-1))
            elif cmd == "00010": block.append(MOVE(2))
            elif cmd == "00011": block.append(MOVE(-2))
            elif cmd == "00100": block.append(MOVE(3))
            elif cmd == "00101": block.append(MOVE(-3))
            elif cmd == "00110": block.append(MOVE(k))
            elif cmd == "00111": block.append(CADD(-1))
            elif cmd == "01000": block.append(CADD(1))
            elif cmd == "01001": block.append(CADD(k))
            elif cmd == "01010": block.append(IN())
            elif cmd == "01011": block.append(OUT())
            elif cmd == "01100": block.append(LOOP(body))
            elif cmd == "01101": block.append(COPY(1))
            elif cmd == "01110": block.append(COPY(2))
            elif cmd == "01111": block.append(COPY(3))
            elif cmd == "10000": block.append(COPY(k))
            elif cmd == "10001": block.append(SET(k))
            elif cmd == "10010": block.append(MUL(k))
            elif cmd == "10011": block.append(DIV(k))
            elif cmd == "10100": block.append(ADD(-1))
            elif cmd == "10101": block.append(ADD(1))
            elif cmd == "10110": block.append(ADD(k))
            elif cmd == "10111": block.append(SUB(-1))
            elif cmd == "11000": block.append(SUB(1))
            elif cmd == "11001": block.append(SUB(k))
            elif cmd == "11010": block.append(SWAP(1))
            elif cmd == "11011": block.append(SWAP(k))
            elif cmd == "11100": block.append(IFZ(body))
            elif cmd == "11101": block.append(CMUL(k))
            elif cmd == "11110": block.append(CDIV(k))
            else:
                raise ValueError(f"Unknown command code: {cmd}")

    return block, i

def decode(n: int) -> List:
    binary = bin(n)[3:] # remove "0b" and leading 1

    use_normal_alphabet = int(binary[0]) # alphabet choice
    m = int(binary[1:5], 2) + 1          # golomb parameter

    return decode_block(binary[5:], m, use_normal_alphabet)[0]
