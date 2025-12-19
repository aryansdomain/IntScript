from __future__ import annotations
from typing import List, Tuple

from .interpreter import (
    MOVE, CADD, SET, ADD, SUB, COPY, SWAP, LOOP,
    IFZ, IFNZ, OUT, IN, MUL, CMUL, DIV, CDIV,
    Instructions
)

def to_int(binary: str) -> int:
    u = int(binary, 2)

    # use ZigZag to convert unsigned binary to signed int
    if (u % 2) == 0: return u // 2
    else:            return -((u+1) // 2)


def decode_block(bits: str, block_len: int = 65536, start: int = 0) -> Tuple[List[Instructions], int]:
    block: List[Instructions] = []

    i = start
    num_cmds = 0
    while i < len(bits) and num_cmds < block_len:
        cmd = bits[i:i+4]
        i += 4
        num_cmds += 1

        match cmd:
            case "0000":
                k = to_int(bits[i:i+8])
                i += 8
                block.append(MOVE(k))

            case "0001":
                k = to_int(bits[i:i+8])
                i += 8 # skip over argument
                block.append(CADD(k))

            case "0010":
                k = to_int(bits[i:i+8])
                i += 8 # skip over argument
                block.append(SET(k))

            case "0011":
                k = to_int(bits[i:i+8])
                i += 8 # skip over argument
                block.append(ADD(k))

            case "0100":
                k = to_int(bits[i:i+8])
                i += 8
                block.append(SUB(k))

            case "0101":
                k = to_int(bits[i:i+8])
                i += 8
                block.append(COPY(k))

            case "0110":
                k = to_int(bits[i:i+8])
                i += 8
                block.append(SWAP(k))

            case "0111": 
                body_len = int(bits[i:i+8], 2)
                i += 8

                loop_block, i = decode_block(bits, body_len, i)
                block.append(LOOP(loop_block))

            case "1000":
                body_len = int(bits[i:i+8], 2)
                i += 8

                ifz_block, i = decode_block(bits, body_len, i)
                block.append(IFZ(ifz_block))

            case "1001":
                body_len = int(bits[i:i+8], 2)
                i += 8
                ifnz_block, i = decode_block(bits, body_len, i)
                block.append(IFNZ(ifnz_block))

            case "1010":
                block.append(OUT())
            
            case "1011":
                block.append(IN())

            case "1100":
                k = to_int(bits[i:i+8])
                i += 8
                block.append(MUL(k))

            case "1101":
                k = to_int(bits[i:i+8])
                i += 8
                block.append(CMUL(k))

            case "1110":
                k = to_int(bits[i:i+8])
                i += 8 # skip over argument
                block.append(DIV(k))

            case "1111":
                k = to_int(bits[i:i+8])
                i += 8
                block.append(CDIV(k))

    return block, i

def decode(n: int) -> List[Instructions]:
    if n <= 0:
        raise ValueError("the input number must be positive.")
    binary = bin(n)[3:] # remove "0b" and leading 1
    return decode_block(binary)[0]
