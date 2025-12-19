from __future__ import annotations
from typing import List

from interpreter.encode      import encode
from interpreter.decode      import decode
from interpreter.interpreter import (
    interpret,
    MOVE, CADD, SET, ADD, SUB, COPY, SWAP, LOOP,
    IFZ, IFNZ, OUT, IN, MUL, CMUL, DIV, CDIV,
    Instructions,
)

# ------------------------ Tests ------------------------

# output "Hello, World!"
HELLO_WORLD: List[Instructions] = [
    CADD(72),  OUT(),  # H
    CADD(29),  OUT(),  # e
    CADD(7),   OUT(),  # l
               OUT(),  # l
    CADD(3),   OUT(),  # o
    CADD(-67), OUT(),  # ,
    CADD(-12), OUT(),  #
    CADD(55),  OUT(),  # W
    CADD(24),  OUT(),  # o
    CADD(3),   OUT(),  # r
    CADD(-6),  OUT(),  # l
    CADD(-8),  OUT(),  # d
    CADD(-67), OUT()   # !
]

# n!
FACTORIAL: List[Instructions] = [
    IN(),                    # cell0 = i = n
    MOVE(1), SET(1),         # cell1 = res = 1
    MOVE(-1),                # -> c0
    LOOP([
        MOVE(1), MUL(-1),    # -> c1 *= c0
        MOVE(-1), CADD(-1),  # -> c0--
    ]),
    MOVE(1), OUT()           # <- c1
]

# sqrt(n)
# 1 + 3 + 5 + ... + (2n-1) = n^2
SQRT: List[Instructions] = [
    IN(),                           # c0 = n
    MOVE(1), CADD(1),               # -> c1 = 1
    MOVE(-1),                       # -> c0

    # subtract odd numbers from c0 until = 0
    LOOP([
        MOVE(1),                    # -> c1
        COPY(2), MOVE(2),           # -> c3 = c1

        # c0 -= c3
        LOOP([
            CADD(-1),               # c3--
            MOVE(-3), CADD(-1),     # c0--
            MOVE(3),                # -> c3
        ]),

        MOVE(-2), CADD(2),          # -> c1 += 2 (next odd number)
        MOVE(1), CADD(1),           # -> c2++ (count)
        MOVE(-2),                   # -> c0
    ]),

    MOVE(2), OUT()                  # c2
]

# nth figonacci number
FIBONACCI: List[Instructions] = [
    IN(),                      # c0 = n
    MOVE(1), SET(0),           # c1 = a = 0
    MOVE(1), SET(1),           # c2 = b = 1
    MOVE(-2),                  # -> c0

    LOOP([
        CADD(-1),              # c0--
        MOVE(1), SWAP(1),      # c1 <-> c2
        MOVE(1), ADD(-1),      # c2 += c1
        MOVE(-2),              # -> c0
    ]),
    MOVE(1), OUT()             # <- c1
]

# gcd of a and b (euclid)
GCD: List[Instructions] = [
    IN(),                   # c0 = a
    MOVE(1), IN(),          # c1 = b

    LOOP([
        MOVE(-1),           # -> c0
        COPY(2), MOVE(2),   # -> c2 = c0
        DIV(-1), MUL(-1),   # c2 = (a/b)*b = a // b
        MOVE(-2), SUB(2),   # -> c0 -= c2 (= a mod b)
        SWAP(1),            # c0 <-> c1 (c0 = b, c1 = a mod b)
        MOVE(1),            # -> c1
    ]),

    MOVE(-1), OUT()         # c0 = gcd(a,b)
]

# a^b
POWER: List[Instructions] = [
    IN(),                       # c0 = a
    MOVE(1), IN(),              # c1 = b
    MOVE(1), SET(1),            # c2 = 1 (result)
    MOVE(-1),                   # -> c1

    LOOP([
        CADD(-1),               # c1--
        MOVE(1), MUL(-2),       # c2 *= c0 (result *= a)
        MOVE(-1),               # -> c1
    ]),

    MOVE(1), OUT()              # c2 = a^b
]

# nth triangular number
# T(n) = n*(n+1)/2
TRIANGULAR: List[Instructions] = [
    IN(),                       # c0 = n
    COPY(1), MOVE(1), CADD(1),  # c1 = n+1
    MOVE(-1), MUL(1),           # c0 = n*(n+1)
    MOVE(1), SET(2),            # c1 = 2
    MOVE(-1), DIV(1),           # c0 /= 2

    OUT()                       # T(n)
]

# how many iterations it takes to stabilize to 1
COLLATZ: List[Instructions] = [
    IN(), CADD(-1),             # c0 = n-1
    MOVE(1), SET(0),            # c1 = steps = 0
    MOVE(1), SET(2),            # c2 = 2
    MOVE(-2),                   # -> c0

    # while (n-1) != 0
    LOOP([
        CADD(1),                # c0 = n

        # compute parity of n
        COPY(3), COPY(4),       # c3 = c4 = c0
        MOVE(3), CDIV(2),       # c3 = n/2
        MOVE(1),                # -> c4
        SUB(-1), SUB(-1),       # c4 -= 2*c3 (1 if odd, 0 if even)

        # if even (c4 == 0): n = c3
        IFZ([
            MOVE(-1), COPY(-3), # c0 = c3
            MOVE(1),            # -> c4
        ]),

        # if odd (c4 != 0): execute once (because r==1) => n = 3n + 1
        LOOP([
            SET(0),             # c4 = 0 (loop only runs once)
            MOVE(-4),           # -> c0
            CMUL(3), CADD(1),   # n = 3n + 1
            MOVE(4),            # -> c4
        ]),

        MOVE(-4), CADD(-1),     # -> c0 = n-1
        MOVE(1), CADD(1),       # -> c1++
        MOVE(-1)                # -> c0
    ]),

    MOVE(1), OUT(),             # output steps
]

TRUTH_MACHINE: List[Instructions] = [
    IN(),
    IFZ([ OUT() ]),
    LOOP([ OUT() ])
]


if __name__ == "__main__":
    TEST = HELLO_WORLD # change

    # encode
    TEST_INT = encode(TEST)
    print(TEST_INT)

    # read input

    # option 1: read from input.txt
    input = b""
    if IN() in TEST:
        with open("input.txt", "rb") as f:
            input = f.read()

    # option 2: set directly
    # input = b"\x05"

    # decode and run
    program = decode(TEST_INT)
    out = interpret(program, input)
    print(out)
