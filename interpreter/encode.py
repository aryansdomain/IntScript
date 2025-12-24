from __future__ import annotations
from typing import List

from interpreter.interpreter import (
    MOVE, CADD, SET, ADD, SUB, COPY, SWAP, LOOP,
    IFZ, OUT, IN, MUL, CMUL, DIV, CDIV
)

def signed_to_unsigned(s: int) -> int:
    # ZigZag
    if s >= 0: return 2 * s
    else:      return -2 * s - 1

def golomb_encode(n: int, m: int) -> str:
    u = signed_to_unsigned(n)
    q, r = divmod(u, m)

    # quotient encoded through unary
    bits = "0" * q + "1"

    # remainder encoded through truncated binary
    k = (m - 1).bit_length()
    if k == 0: return bits
    
    t = (1 << k) - m
    if r < t: bits += format(r,     f"0{k-1}b")
    else:     bits += format(r + t, f"0{k}b")
    return bits


def encode_block(block: List, m: int, use_normal_alphabet: bool) -> str:
    bits = ""

    if use_normal_alphabet:
        for cmd in block:
            if isinstance(cmd, LOOP) or isinstance(cmd, IFZ):
                k = encode_block(cmd.body, m, use_normal_alphabet) + "1111"
            elif not isinstance(cmd, OUT) and not isinstance(cmd, IN): # has arguments
                k = golomb_encode(cmd.k, m)

            if   isinstance(cmd, MOVE): bits += "0000" + k
            elif isinstance(cmd, CADD): bits += "0001" + k
            elif isinstance(cmd, IN):   bits += "0010"
            elif isinstance(cmd, OUT):  bits += "0011"
            elif isinstance(cmd, LOOP): bits += "0100" + k
            elif isinstance(cmd, COPY): bits += "0101" + k
            elif isinstance(cmd, SET):  bits += "0110" + k
            elif isinstance(cmd, MUL):  bits += "0111" + k
            elif isinstance(cmd, DIV):  bits += "1000" + k
            elif isinstance(cmd, ADD):  bits += "1001" + k
            elif isinstance(cmd, SUB):  bits += "1010" + k
            elif isinstance(cmd, SWAP): bits += "1011" + k
            elif isinstance(cmd, IFZ):  bits += "1100" + k
            elif isinstance(cmd, CMUL): bits += "1101" + k
            elif isinstance(cmd, CDIV): bits += "1110" + k
            else:
                raise TypeError(f"Unknown instruction: {cmd}")

    else:
        for cmd in block:
            if isinstance(cmd, MOVE):
                if   cmd.k == 1:    bits += "00000"
                elif cmd.k == -1:   bits += "00001"
                elif cmd.k == 2:    bits += "00010"
                elif cmd.k == -2:   bits += "00011"
                elif cmd.k == 3:    bits += "00100"
                elif cmd.k == -3:   bits += "00101"
                else:               bits += "00110" + golomb_encode(cmd.k, m)

            elif isinstance(cmd, CADD):
                if   cmd.k == -1:   bits += "00111"
                elif cmd.k == 1:    bits += "01000"
                else:               bits += "01001" + golomb_encode(cmd.k, m)

            elif isinstance(cmd, IN):
                                    bits += "01010"

            elif isinstance(cmd, OUT):
                                    bits += "01011"

            elif isinstance(cmd, LOOP):
                                    bits += "01100" + encode_block(cmd.body, m, use_normal_alphabet) + "11111"

            elif isinstance(cmd, COPY):
                if cmd.k == 1:      bits += "01101"
                elif cmd.k == 2:    bits += "01110"
                elif cmd.k == 3:    bits += "01111"
                else:               bits += "10000" + golomb_encode(cmd.k, m)

            elif isinstance(cmd, SET):
                                    bits += "10001" + golomb_encode(cmd.k, m)
            elif isinstance(cmd, MUL):
                                    bits += "10010" + golomb_encode(cmd.k, m)
            elif isinstance(cmd, DIV):
                                    bits += "10011" + golomb_encode(cmd.k, m)

            elif isinstance(cmd, ADD):
                if   cmd.k == -1: bits += "10100"
                elif cmd.k == 1:  bits += "10101"
                else:             bits += "10110" + golomb_encode(cmd.k, m)

            elif isinstance(cmd, SUB):
                if   cmd.k == -1:   bits += "10111"
                elif cmd.k == 1:    bits += "11000"
                else:               bits += "11001" + golomb_encode(cmd.k, m)

            elif isinstance(cmd, SWAP):
                if cmd.k == 1:      bits += "11010"
                else:               bits += "11011" + golomb_encode(cmd.k, m)

            elif isinstance(cmd, IFZ):
                                    bits += "11100" + encode_block(cmd.body, m, use_normal_alphabet) + "11111"
            elif isinstance(cmd, CMUL):
                                    bits += "11101" + golomb_encode(cmd.k, m)
            elif isinstance(cmd, CDIV):
                                    bits += "11110" + golomb_encode(cmd.k, m)
            else:
                raise TypeError(f"Unknown instruction: {cmd}")

    return bits

def encode(program: List) -> int:

    # compute optimal golomb parameter
    def optimal_golomb(program: List, use_normal_alphabet: bool) -> int:
        m_list = []
        for m in range(1, 17):
            header = str(int(use_normal_alphabet)) + format(m - 1, "04b")
            m_list.append(int("1" + header + encode_block(program, m, use_normal_alphabet), 2))
        return min(m_list)

    
    # return the smallest program
    return min(optimal_golomb(program, False), optimal_golomb(program, True))
