from __future__ import annotations
from typing import List

from interpreter.interpreter import (
    MOVE, CADD, SET, ADD, SUB, COPY, SWAP, LOOP,
    IFZ, IFNZ, OUT, IN, MUL, CMUL, DIV, CDIV,
    Instructions
)

def int_to_binary(n: int) -> str:
    if not -128 <= n <= 127:
        raise ValueError(f"{n} out of supported range (-128..127)")

    # use ZigZag to convert signed int to unsigned binary
    if n >= 0: u =  2 * n
    else:      u = -2 * n - 1
    return format(u, "08b")


def encode_block(block: List[Instructions]) -> str:
    bits = ""
    for cmd in block:

        if isinstance(cmd, LOOP) or isinstance(cmd, IFZ) or isinstance(cmd, IFNZ):
            body_len = len(cmd.body)
            if body_len > 255:
                raise ValueError(f"{cmd.__class__.__name__} body too large ({body_len} instructions, max 255")

            k = format(body_len, "08b") + encode_block(cmd.body)

        elif not isinstance(cmd, OUT) and not isinstance(cmd, IN): # has arguments
            k = int_to_binary(cmd.k)


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
        elif isinstance(cmd, IFNZ): bits += "1101" + k
        elif isinstance(cmd, CMUL): bits += "1110" + k
        elif isinstance(cmd, CDIV): bits += "1111" + k
        else:
            raise TypeError(f"Unknown instruction: {cmd}")

    return bits

def encode2(program: List[Instructions]) -> int:
    # leading 1 to ensure all bits get counted
    return int("1" + encode_block(program), 2)
