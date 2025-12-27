from __future__ import annotations
import math
from interpreter.interpreter import (
    MOVE, CADD, SET, ADD, SUB, COPY, SWAP, LOOP,
    IFZ, OUT, IN, MUL, CMUL, DIV, CDIV, Commands
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
    if r < t: bits += format(r,     f"0{k-1}b")
    else:     bits += format(r + t, f"0{k}b")
    return bits


def encode_block(block: list, m: int, normal_alphabet: bool) -> str:
    bits = ""

    if normal_alphabet:
        for cmd in block:
            if isinstance(cmd, LOOP) or isinstance(cmd, IFZ):
                k = encode_block(cmd.body, m, normal_alphabet) + "1111"
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

    else:
        for cmd in block:
            if isinstance(cmd, MOVE):
                if   cmd.k == 1:    bits += "00000"
                elif cmd.k == -1:   bits += "00001"
                elif cmd.k == 2:    bits += "00010"
                elif cmd.k == -2:   bits += "00011"
                elif cmd.k == 3:    bits += "00100"
                elif cmd.k == -3:   bits += "00101"
                else:               bits += "00110" + golomb_encode(cmd.k, m)

            elif isinstance(cmd, CADD):
                if   cmd.k == -1:   bits += "00111"
                elif cmd.k == 1:    bits += "01000"
                else:               bits += "01001" + golomb_encode(cmd.k, m)

            elif isinstance(cmd, IN):
                                    bits += "01010"

            elif isinstance(cmd, OUT):
                                    bits += "01011"

            elif isinstance(cmd, LOOP):
                                    bits += "01100" + encode_block(cmd.body, m, normal_alphabet) + "11111"

            elif isinstance(cmd, COPY):
                if cmd.k == 1:      bits += "01101"
                elif cmd.k == 2:    bits += "01110"
                elif cmd.k == 3:    bits += "01111"
                else:               bits += "10000" + golomb_encode(cmd.k, m)

            elif isinstance(cmd, SET):
                                    bits += "10001" + golomb_encode(cmd.k, m)
            elif isinstance(cmd, MUL):
                                    bits += "10010" + golomb_encode(cmd.k, m)
            elif isinstance(cmd, DIV):
                                    bits += "10011" + golomb_encode(cmd.k, m)

            elif isinstance(cmd, ADD):
                if   cmd.k == -1: bits += "10100"
                elif cmd.k == 1:  bits += "10101"
                else:             bits += "10110" + golomb_encode(cmd.k, m)

            elif isinstance(cmd, SUB):
                if   cmd.k == -1:   bits += "10111"
                elif cmd.k == 1:    bits += "11000"
                else:               bits += "11001" + golomb_encode(cmd.k, m)

            elif isinstance(cmd, SWAP):
                if cmd.k == 1:      bits += "11010"
                else:               bits += "11011" + golomb_encode(cmd.k, m)

            elif isinstance(cmd, IFZ):
                                    bits += "11100" + encode_block(cmd.body, m, normal_alphabet) + "11111"
            elif isinstance(cmd, CMUL):
                                    bits += "11101" + golomb_encode(cmd.k, m)
            elif isinstance(cmd, CDIV):
                                    bits += "11110" + golomb_encode(cmd.k, m)
            else:
                raise TypeError(f"Unknown instruction: {cmd}")

    return bits

def encode_block_short_alphabet(block: list, m: int) -> str:
    bits = ""

    # names/types of the commands in block
    block_types = set()
    for cmd in block:
        block_types.add(type(cmd))

    # encode what commands are in block
    cmds = []
    for cmd in Commands[::-1]: # less frequent to more frequent
        if cmd in block_types:
            bits += "1"
            cmds.append(cmd)
        else:
            bits += "0"
    cmds.reverse() 

    # number of bits used to represent each command
    if IFZ in cmds or LOOP in cmds: num_cmds = len(cmds) + 1 # +1 for end block
    else:                           num_cmds = len(cmds)
    num_bits = max(1, math.ceil(math.log2(num_cmds)))

    # encode the list of commands
    for cmd in block:
        bits += format(cmds.index(type(cmd)), f"0{num_bits}b") # individual code for each command

        # arguments
        if isinstance(cmd, LOOP) or isinstance(cmd, IFZ):
            bits += encode_block_short_alphabet(cmd.body, m) + "1" * num_bits
        elif not isinstance(cmd, OUT) and not isinstance(cmd, IN): # has arguments
            bits += golomb_encode(cmd.k, m)

    return bits


def encode(program: list) -> int:

    # compute optimal golomb parameter
    def optimal_golomb(program: list, normal_alphabet: bool, short_alphabet: bool) -> int:
        m_list = []
        for m in range(1, 17):
            if short_alphabet:
                header = "1" + format(m - 1, "04b")
                m_list.append(int("1" + header + encode_block_short_alphabet(program, m), 2))
            else:
                header = "0" + str(int(normal_alphabet)) + format(m - 1, "04b")
                m_list.append(int("1" + header + encode_block(program, m, normal_alphabet), 2))

        return min(m_list)

    # return the smallest program
    candidates = []
    pair = [[True, True], [True, False], [False, True], [False, False]]
    for normal_alphabet, short_alphabet in pair:
        candidates.append(optimal_golomb(program, normal_alphabet, short_alphabet))
    return min(candidates)

    # MOST OPTIMAL FOR HELLO WORLD
    # int("1110000" + encode_block_short_alphabet(program, 17), 2)
