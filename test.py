from __future__ import annotations
from typing import List

from interpreter.encode      import encode
from interpreter.decode      import decode
from interpreter.interpreter import interpret, ADD, MOVE, SET, LOOP, OUT, IN, COPY, MUL, Instructions

# ------------------------ Tests ------------------------

HELLO_WORLD: List[Instructions] = [
    ADD(72),  OUT(),  # H
    ADD(29),  OUT(),  # e
    ADD(7),   OUT(),  # l
              OUT(),  # l
    ADD(3),   OUT(),  # o
    ADD(-67), OUT(),  # ,
    ADD(-12), OUT(),  #
    ADD(55),  OUT(),  # W
    ADD(24),  OUT(),  # o
    ADD(3),   OUT(),  # r
    ADD(-6),  OUT(),  # l
    ADD(-8),  OUT(),  # d
    ADD(-67), OUT()   # !
]

DIVIDE: List[Instructions] = [
    IN(),                      # c0 = a
    MOVE(1), IN(),             # c1 = b
    MOVE(-1),                  # -> c0

    LOOP([
        MOVE(1), COPY(1),      # c2 = c1
        MOVE(1),               # -> c2

        # c0 = c0 - c2
        LOOP([
            ADD(-1),           # c2--
            MOVE(-2), ADD(-1), # c0--
            MOVE(2),           # -> c2
        ]),
        
        MOVE(1), ADD(1),       # c3++
        MOVE(-3),              # -> c0
    ]),
    MOVE(3), OUT(),            # c3
]

FACTORIAL: List[Instructions] = [
    IN(),                   # cell0 = i = n
    MOVE(1), SET(1),        # cell1 = res = 1
    MOVE(-1),               # -> c0
    LOOP([
        MOVE(1), MUL(-1),   # -> c1 = c1 * c0
        MOVE(-1), ADD(-1),  # -> c0--
    ]),
    MOVE(1), OUT(),         # c1
]

# 1 + 3 + 5 + ... + (2n-1) = n^2
SQRT: List[Instructions] = [
    IN(),                       # c0 = n
    MOVE(1), ADD(1),            # -> c1 = 1
    MOVE(-1),                   # -> c0

    # subtract odd numbers from c0 until = 0
    LOOP([
        MOVE(1),                # -> c1
        COPY(2), MOVE(2),       # -> c3 = c1

        # c0 -= c3
        LOOP([
            ADD(-1),            # c3--
            MOVE(-3), ADD(-1),  # c0--
            MOVE(3),            # -> c3
        ]),

        MOVE(-2), ADD(2),       # -> c1 += 2 (next odd number)
        MOVE(1), ADD(1),        # -> c2++ (count)
        MOVE(-2),               # -> c0
    ]),
    MOVE(2), OUT(),             # c2
]


if __name__ == "__main__":
    TEST = HELLO_WORLD # change

    # encode
    TEST_INT = encode(TEST)
    print(TEST_INT)

    # read input
    input = b""
    if IN() in TEST:
        with open("input.txt", "rb") as f:
            input = f.read()

    # decode and run
    program = decode(TEST_INT)
    out = interpret(program, input)
    print(out)
