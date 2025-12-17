from __future__ import annotations
from typing import List, Tuple

from .interpreter import ADD, MOVE, OUT, SET, LOOP, IN, COPY, MUL, Instructions

def to_int(binary: str) -> int:
    u = int(binary, 2)
    if (u % 2) == 0: return u // 2
    else:            return -((u + 1) // 2)


def decode_block(bits: str, block_len: int = 65536, start: int = 0) -> Tuple[List[Instructions], int]:
    block: List[Instructions] = []

    i = start
    num_cmds = 0
    while i < len(bits) and num_cmds < block_len:
        cmd = bits[i:i+3]
        i += 3
        num_cmds += 1

        match cmd:
            case "000":
                k = to_int(bits[i:i+8])
                i += 8 # skip over argument
                block.append(ADD(k))

            case "001":
                k = to_int(bits[i:i+8])
                i += 8 # skip over argument
                block.append(MOVE(k))

            case "010":
                k = to_int(bits[i:i+8])
                i += 8 # skip over argument
                block.append(SET(k))

            case "011": 
                body_len = int(bits[i:i+8], 2)
                i += 8

                loop_block, i = decode_block(bits, body_len, i)
                block.append(LOOP(loop_block))

            case "100":
                block.append(OUT())
            
            case "101":
                block.append(IN())

            case "110":
                k = to_int(bits[i:i+8])
                i += 8 # skip over argument
                block.append(COPY(k))

            case "111":
                k = to_int(bits[i:i+8])
                i += 8 # skip over argument
                block.append(MUL(k))

    return block, i

def decode(N: int) -> List[Instructions]:
    binary = bin(N)[3:]
    return decode_block(binary)[0]
