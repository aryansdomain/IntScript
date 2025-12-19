from __future__ import annotations
from typing import List

from .interpreter import (
    MOVE, CADD, SET, ADD, SUB, COPY, SWAP, LOOP,
    IFZ, IFNZ, OUT, IN, MUL, CMUL, DIV, CDIV,
    Instructions
)

def to_binary(n: int) -> str:
    if not -128 <= n <= 127:
        raise ValueError(f"{n} out of supported range (-128..127)")

    # use ZigZag to convert signed int to unsigned binary
    if n >= 0: u =  2 * n
    else:      u = -2 * n - 1
    return format(u, "08b")


def encode_block(block: List[Instructions]) -> str:
    bits = ""
    for cmd in block:
        if isinstance(cmd, MOVE):
            bits += "0000" + to_binary(cmd.k)

        elif isinstance(cmd, CADD):
            bits += "0001" + to_binary(cmd.k)

        elif isinstance(cmd, SET):
            bits += "0010" + to_binary(cmd.k)

        elif isinstance(cmd, ADD):
            bits += "0011" + to_binary(cmd.k)

        elif isinstance(cmd, SUB):
            bits += "0100" + to_binary(cmd.k)

        elif isinstance(cmd, COPY):
            bits += "0101" + to_binary(cmd.k)

        elif isinstance(cmd, SWAP):
            bits += "0110" + to_binary(cmd.k)

        elif isinstance(cmd, LOOP):
            body_len = len(cmd.body)
            if body_len > 255:
                raise ValueError(f"LOOP body too large ({body_len} instructions)")

            bits += "0111" + format(body_len, "08b") + encode_block(cmd.body)

        elif isinstance(cmd, IFZ):
            body_len = len(cmd.body)
            if body_len > 255:
                raise ValueError(f"IFZ body too large ({body_len} instructions)")

            bits += "1000" + format(body_len, "08b") + encode_block(cmd.body)

        elif isinstance(cmd, IFNZ):
            body_len = len(cmd.body)
            if body_len > 255:
                raise ValueError(f"IFNZ body too large ({body_len} instructions)")

            bits += "1001" + format(body_len, "08b") + encode_block(cmd.body)

        elif isinstance(cmd, OUT):
            bits += "1010"
        
        elif isinstance(cmd, IN):
            bits += "1011"

        elif isinstance(cmd, MUL):
            bits += "1100" + to_binary(cmd.k)

        elif isinstance(cmd, CMUL):
            bits += "1101" + to_binary(cmd.k)

        elif isinstance(cmd, DIV):
            bits += "1110" + to_binary(cmd.k)

        elif isinstance(cmd, CDIV):
            bits += "1111" + to_binary(cmd.k)

        else:
            raise TypeError(f"Unknown instruction: {cmd}")

    return bits

def encode(program: List[Instructions]) -> int:
    # leading 1 to ensure all bits get counted
    return int("1" + encode_block(program), 2)
