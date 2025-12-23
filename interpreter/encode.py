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
    if r < t: bits += format(r, f"0{k-1}b")
    else:     bits += format(r + t, f"0{k}b")
    return bits


def encode_block(block: List, m: int) -> str:
    bits = ""
    for cmd in block:

        if isinstance(cmd, LOOP) or isinstance(cmd, IFZ):
            k = encode_block(cmd.body, m) + "1111"
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

    return bits

def encode(program: List) -> int:

    # compute optimal golomb parameter
    m_list = []
    for m in range(1, 17):
        header = format(m - 1, "04b")
        m_list.append(int("1" + header + encode_block(program, m), 2))

    return min(m_list) # smallest program
