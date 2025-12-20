from __future__ import annotations
from typing import Any, List, Tuple

from .interpreter import (
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
        cmd = bits[i:i+4]
        i += 4
        num_cmds += 1

        body = None
        if cmd not in {"1010", "1011"}: # exclude OUT and IN

            # read until 2
            start = i
            while i < len(bits) and bits[i] != '2': i += 1
            k = bits[start:i]
            i += 1

            if int(cmd, 2) < 7 or int(cmd, 2) > 9: # non-loop commands (signed)
                k = binary_to_int(k) # argument
            else:                                  # loop commands (unsigned)
                k = int(k, 2) # block length
                body, i = decode_block(bits, k, i)
                if i < len(bits) and bits[i] == '2': # read 2 at end of loop
                    i += 1

        match cmd:
            case "0000": block.append(MOVE(k))
            case "0001": block.append(CADD(k))
            case "0010": block.append(SET(k))
            case "0011": block.append(ADD(k))
            case "0100": block.append(SUB(k))
            case "0101": block.append(COPY(k))
            case "0110": block.append(SWAP(k))
            case "0111": block.append(LOOP(body))
            case "1000": block.append(IFZ(body))
            case "1001": block.append(IFNZ(body))
            case "1010": block.append(OUT())
            case "1011": block.append(IN())
            case "1100": block.append(MUL(k))
            case "1101": block.append(CMUL(k))
            case "1110": block.append(DIV(k))
            case "1111": block.append(CDIV(k))

    return block, i

def decode(n: int) -> List[Instructions]:

    # convert integer to ternary
    digits = []
    while n > 0:
        digits.append(str(n % 3))
        n //= 3
    ternary = ''.join(reversed(digits))

    return decode_block(ternary[1:])[0] # remove leading 1
