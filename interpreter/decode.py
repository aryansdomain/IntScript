from __future__ import annotations
import math
from interpreter.interpreter import (
    MOVE, CADD, SET, ADD, SUB, COPY, SWAP, LOOP,
    IFZ, OUT, IN, MUL, CMUL, DIV, CDIV, Commands
)

def unsigned_to_signed(u: int) -> int:
    # ZigZag
    if (u % 2) == 0: return u // 2
    else:            return -(u + 1) // 2

def golomb_decode(bits: str, m: int) -> tuple[int, int]:

    # read quotient
    i = 0
    q = 0
    while bits[i] == "0":
        q += 1
        i += 1
    i += 1  # read the '1'

    # read remainder
    k = (m - 1).bit_length()
    t = (1 << k) - m

    if k == 0:
        r = 0
    else:
        x_bits = k - 1
        x = int(bits[i:i + x_bits], 2) if x_bits > 0 else 0
        if x < t:
            r = x
            i += x_bits
        else:
            x = int(bits[i:i + k], 2)
            r = x - t
            i += k

    # construct unsigned
    u = q * m + r
    return unsigned_to_signed(u), i


def decode_block(bits: str, m: int, normal_alphabet: bool, start: int = 0) -> tuple[list, int]:
    block = []
    i = start

    if normal_alphabet:
        while i < len(bits):
            # read command
            cmd = bits[i:i+4]
            i += 4

            # read argument
            if cmd not in {"0010", "0011", "1111"}: # exclude IN, OUT, end block
                if cmd in {"0100", "1100"}: # loop commands
                    body, i = decode_block(bits, m, normal_alphabet, i)
                else:
                    k, used = golomb_decode(bits[i:], m)
                    i += used

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
                case "1101": block.append(CMUL(k))
                case "1110": block.append(CDIV(k))
                case "1111": return block, i

    else:
        while i < len(bits):
            # read command
            cmd = bits[i:i+5]
            i += 5

            # read argument
            if cmd not in {"01010", "01011", "11111"}: # exclude IN, OUT, end block
                if cmd in {"01100", "11100"}: # loop commands
                    body, i = decode_block(bits, m, normal_alphabet, i)
                elif cmd in {
                    "00110", "01001", "10000", "10001", "10010", "10011",
                    "10110", "11001", "11011", "11101", "11110"
                }: # has argument
                    k, used = golomb_decode(bits[i:], m)
                    i += used

            match cmd:
                case "00000": block.append(MOVE(1))
                case "00001": block.append(MOVE(-1))
                case "00010": block.append(MOVE(2))
                case "00011": block.append(MOVE(-2))
                case "00100": block.append(MOVE(3))
                case "00101": block.append(MOVE(-3))
                case "00110": block.append(MOVE(k))
                case "00111": block.append(CADD(-1))
                case "01000": block.append(CADD(1))
                case "01001": block.append(CADD(k))
                case "01010": block.append(IN())
                case "01011": block.append(OUT())
                case "01100": block.append(LOOP(body))
                case "01101": block.append(COPY(1))
                case "01110": block.append(COPY(2))
                case "01111": block.append(COPY(3))
                case "10000": block.append(COPY(k))
                case "10001": block.append(SET(k))
                case "10010": block.append(MUL(k))
                case "10011": block.append(DIV(k))
                case "10100": block.append(ADD(-1))
                case "10101": block.append(ADD(1))
                case "10110": block.append(ADD(k))
                case "10111": block.append(SUB(-1))
                case "11000": block.append(SUB(1))
                case "11001": block.append(SUB(k))
                case "11010": block.append(SWAP(1))
                case "11011": block.append(SWAP(k))
                case "11100": block.append(IFZ(body))
                case "11101": block.append(CMUL(k))
                case "11110": block.append(CDIV(k))
                case "11111": return block, i

    return block, i

def decode_block_short_alphabet(bits: str, m: int, cmds_bits: str, start: int = 0) -> tuple[list, int]:

    has_block_cmd = False
    cmds_used = []
    for j in range(15):
        if cmds_bits[14 - j] == "1":
            if Commands[j] is LOOP or Commands[j] is IFZ: has_block_cmd = True
            cmds_used.append(Commands[j])

    # number of bits used to represent each command
    if has_block_cmd: num_cmds = len(cmds_used) + 1 # +1 for end block
    else:             num_cmds = len(cmds_used)
    num_bits = max(1, math.ceil(math.log2(num_cmds)))

    # decode list of commands
    i = start
    block = []
    while i < len(bits):

        # read command
        cmd_bits = bits[i:i+num_bits]
        i += num_bits
        if has_block_cmd and cmd_bits == ("1" * num_bits): return block, i # end-of-block marker
        cmd = cmds_used[int(cmd_bits, 2)]

        # read argument
        if cmd is not OUT and cmd is not IN:
            if cmd is LOOP or cmd is IFZ:
                body, i = decode_block_short_alphabet(bits, m, cmds_bits, i)
            else:
                k, used = golomb_decode(bits[i:], m)
                i += used

        if   cmd is MOVE: block.append(MOVE(k))
        elif cmd is CADD: block.append(CADD(k))
        elif cmd is IN:   block.append(IN())
        elif cmd is OUT:  block.append(OUT())
        elif cmd is LOOP: block.append(LOOP(body))
        elif cmd is COPY: block.append(COPY(k))
        elif cmd is SET:  block.append(SET(k))
        elif cmd is MUL:  block.append(MUL(k))
        elif cmd is DIV:  block.append(DIV(k))
        elif cmd is ADD:  block.append(ADD(k))
        elif cmd is SUB:  block.append(SUB(k))
        elif cmd is SWAP: block.append(SWAP(k))
        elif cmd is IFZ:  block.append(IFZ(body))
        elif cmd is CMUL: block.append(CMUL(k))
        elif cmd is CDIV: block.append(CDIV(k))

    return block, i


def decode(n: int) -> list:
    binary = bin(n)[2:] # remove "0b"

    if binary[1] == "1":
        m = int(binary[2:6], 2) + 1          # golomb parameter
        return decode_block_short_alphabet(binary[21:], m, binary[6:21])[0]
    else:
        normal_alphabet = int(binary[2])     # alphabet choice
        m = int(binary[3:7], 2) + 1          # golomb parameter
        return decode_block(binary[7:], m, normal_alphabet)[0]
