from __future__ import annotations
from typing import List

from interpreter.interpreter import (
    MOVE, CADD, SET, ADD, SUB, COPY, SWAP, LOOP,
    IFZ, OUT, IN, MUL, CMUL, DIV, CDIV,
    Instructions
)

def signed_to_unsigned(s: int) -> int:
    # ZigZag
    if s >= 0: return 2 * s
    else:      return -2 * s - 1

def rice_encode(n: int, p: int) -> str:
    u = signed_to_unsigned(n)

    q = u >> p
    r = u & ((1 << p) - 1) # u & (2p-1)

    bits = ("0" * q) + "1"
    bits += format(r, f"0{p}b")
    return bits


def encode_block(block: List[Instructions], p: int) -> str:
    bits = ""
    for cmd in block:

        if isinstance(cmd, LOOP) or isinstance(cmd, IFZ):
            k = encode_block(cmd.body, p) + "1111"
        elif not isinstance(cmd, OUT) and not isinstance(cmd, IN): # has arguments
            k = rice_encode(cmd.k, p)


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

def encode(program: List[Instructions]) -> int:

    # compute optimal p-value
    p_list = []
    for p in range(2, 6):
        header = format(p-2, "02b")
        p_list.append(int("1" + header + encode_block(program, p), 2))

    return min(p_list)
