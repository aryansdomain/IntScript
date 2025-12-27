from __future__ import annotations

from interpreter.encode      import encode
from interpreter.decode      import decode
from interpreter.interpreter import (
    interpret,
    MOVE, CADD, SET, ADD, SUB, COPY, SWAP, LOOP,
    IFZ, OUT, IN, MUL, CMUL, DIV, CDIV,
)

# ------------------------ Tests ------------------------

# output "Hello, World!"
HELLO_WORLD = [
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
FACTORIAL = [
    IN(),                       # cell0 = i = n
    MOVE(1), SET(1),            # cell1 = res = 1
    MOVE(-1),                   # -> c0
    LOOP([
        MOVE(1), MUL(-1),       # -> c1 *= c0
        MOVE(-1), CADD(-1),     # -> c0--
    ]),
    MOVE(1), OUT()              # <- c1
]

# sqrt(n)
# 1 + 3 + 5 + ... + (2n-1) = n^2
SQRT = [
    IN(),                       # c0 = n
    MOVE(1), CADD(1),           # -> c1 = 1
    MOVE(-1),                   # -> c0

    # subtract odd numbers from c0 until = 0
    LOOP([
        SUB(1),                 # c0 -= c1
        MOVE(1), CADD(2),       # -> c1 += 2 (next odd number)
        MOVE(1), CADD(1),       # -> c2++ (count)
        MOVE(-2),               # -> c0
    ]),

    MOVE(2), OUT()              # c2
]

# find the nth fibonacci number
FIBONACCI = [
    IN(),                       # c0 = n
    MOVE(2), SET(1),            # c2 = b = 1
    MOVE(-2),                   # -> c0

    LOOP([
        CADD(-1),               # c0--
        MOVE(1), ADD(1),        # -> c1 += c2
        SWAP(1),                # c1 <-> c2
        MOVE(-1),               # -> c0
    ]),

    MOVE(1), OUT()              # <- c1
]

# gcd of a and b (euclid)
GCD = [
    IN(),                       # c0 = a
    MOVE(1), IN(),              # c1 = b

    LOOP([
        MOVE(-1),               # -> c0

        # compute a mod b
        COPY(2),                # c2 = c0
        DIV(1), MUL(1),         # c0 = (a // b) * b
        SWAP(2),                # c0 <-> c2
        SUB(2),                 # c0 -= c2 (c0 = a mod b)

        SWAP(1),                # c0 <-> c1 (c0 = b, c1 = a mod b)
        MOVE(1),                # -> c1
    ]),

    MOVE(-1), OUT()             # c0 = gcd(a,b)
]

# a^b
POWER = [
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
TRIANGULAR = [
    IN(),                       # c0 = n
    COPY(1), MOVE(1), CADD(1),  # c1 = n+1
    MOVE(-1), MUL(1),           # c0 = n*(n+1)
    CDIV(2),                    # c0 /= 2

    OUT()                       # c0 = T(n)
]

# how many iterations it takes to stabilize to 1
COLLATZ = [
    IN(), CADD(-1),             # c0 = n-1

    # while (n-1) != 0
    LOOP([
        CADD(1),                # c0 = n

        # compute parity of n
        COPY(2), COPY(3),       # c2 = c3 = c0
        MOVE(2), CDIV(2),       # c2 = n/2
        MOVE(1),                # -> c3
        SUB(-1), SUB(-1),       # c3 -= 2 * c2 (1 if odd, 0 if even)

        # if even (c3 == 0): n = n / 2 = c2
        IFZ([
            MOVE(-1), COPY(-2), # c0 = c2
            MOVE(1),            # -> c3
        ]),

        # if odd (c3 != 0): n = 3n + 1
        LOOP([
            SET(0),             # so the loop only runs once
            MOVE(-3),           # -> c0
            CMUL(3), CADD(1),   # n = 3n + 1
            MOVE(3)             # -> c3
        ]),

        MOVE(-3), CADD(-1),     # -> c0 = n-1
        MOVE(1), CADD(1),       # -> c1++ (steps)
        MOVE(-1)                # -> c0
    ]),

    MOVE(1), OUT()              # c1 = steps
]

TRUTH_MACHINE = [
    IN(),
    IFZ([ OUT() ]),             # if 0, output 0
    LOOP([ OUT() ])             # if 1, infinitely output 1
]

def test_and_compute_compactness() -> int:
    total = 0
    programs = {
        "HELLO_WORLD": HELLO_WORLD,
        "FACTORIAL": FACTORIAL,
        "SQRT": SQRT,
        "FIBONACCI": FIBONACCI,
        "GCD": GCD,
        "POWER": POWER,
        "TRIANGULAR": TRIANGULAR,
        "COLLATZ": COLLATZ,
        "TRUTH_MACHINE": TRUTH_MACHINE,
    }

    print("-" * 80)
    for name, program in programs.items():
        encoded = encode(program)
        total += encoded
        print(name + ": " + " " * (14-len(name)) + str(encoded))

        # test if decoding works
        if program != decode(encoded):
            print(f"Error: {name} decoded incorrectly")

    print("AVERAGE:        " + str(total // len(programs))) # average
    print("-" * 80)


if __name__ == "__main__":
    # test_and_compute_compactness()

    TEST = HELLO_WORLD # change

    # encode
    TEST_INT = encode(TEST)
    print(TEST_INT)

    # read input
    # option 1: read from input.txt
    input_bytes = b""
    with open("input.txt", "rb") as f:
        input_bytes = f.read()

    # option 2: set directly
    # input_bytes = b"\x04"

    # decode
    program = decode(TEST_INT)

    # run
    out = interpret(program, input_bytes)
    print(out)
