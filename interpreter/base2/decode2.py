from __future__ import annotations
from typing import List, Tuple

from interpreter.interpreter import (
    MOVE, CADD, SET, ADD, SUB, COPY, SWAP, LOOP,
    IFZ, IFNZ, OUT, IN, MUL, CMUL, DIV, CDIV,
    Instructions
)

def binary_to_int(binary: str) -> int:
    u = int(binary, 2)

    # use ZigZag to convert unsigned binary to signed int
    if (u % 2) == 0: return u // 2
    else:            return -((u+1) // 2)


def decode_block(bits: str, block_len: int = 65536, start: int = 0) -> Tuple[List[Instructions], int]:
    block: List[Instructions] = []
    i = start
    num_cmds = 0

    while i < len(bits) and num_cmds < block_len:
        # read command
        cmd = bits[i:i+4]
        i += 4
        num_cmds += 1

        # read arguments
        if cmd not in {"0010", "0011"}: # exclude IN and OUT
            if cmd in {"0100", "1100", "1101"}: # loop commands
                body_len = int(bits[i:i+8], 2)
                i += 8
                body, i = decode_block(bits, body_len, i)
            else:
                k = binary_to_int(bits[i:i+8])
                i += 8

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
            case "1101": block.append(IFNZ(body))
            case "1110": block.append(CMUL(k))
            case "1111": block.append(CDIV(k))

    return block, i

def decode2(n: int) -> List[Instructions]:
    binary = bin(n)[3:] # remove "0b" and leading 1

    return decode_block(binary)[0]