from __future__ import annotations
from typing import List

from .interpreter import ADD, MOVE, OUT, SET, LOOP, IN, COPY, MUL, Instructions

def to_binary(n: int) -> str:
    if not -128 <= n <= 127:
        raise ValueError(f"Immediate {n} out of supported range (-128..127)")

    if n >= 0: u = n * 2
    else:      u = -2 * n - 1
    return format(u, "08b")


def encode_block(block: List[Instructions]) -> str:
    bits = ""
    for cmd in block:
        if isinstance(cmd, ADD):
            bits += "000" + to_binary(cmd.k)

        elif isinstance(cmd, MOVE):
            bits += "001" + to_binary(cmd.k)

        elif isinstance(cmd, SET):
            bits += "010" + to_binary(cmd.k)

        elif isinstance(cmd, LOOP):
            body_len = len(cmd.body)
            if not 0 <= body_len < 256:
                raise ValueError(f"Loop body too large ({body_len} instructions)")
            bits += "011" + format(body_len, "08b") + encode_block(cmd.body)

        elif isinstance(cmd, OUT):
            bits += "100"
        
        elif isinstance(cmd, IN):
            bits += "101"

        elif isinstance(cmd, COPY):
            bits += "110" + to_binary(cmd.k)

        elif isinstance(cmd, MUL):
            bits += "111" + to_binary(cmd.k)

        else:
            raise TypeError(f"Unknown instruction: {cmd}")

    return bits

def encode(program: List[Instructions]) -> int:
    return int("1" + encode_block(program), 2)
