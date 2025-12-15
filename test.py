from __future__ import annotations

from interpreter.encode import encode
from interpreter.decode import run

# ------------------------ Tests ------------------------
# Credit to https://esolangs.org/wiki/Brainfuck

HELLO_WORLD = "+[-->-[>>+>-----<<]<--<---]>-.>>>+.>>..+++[.>]<<<<.+++.------.<<-.>>>>+."

MOVE = ",[->+<]>."

# ------------------------ Run Tests ------------------------

if __name__ == "__main__":
    TEST = HELLO_WORLD

    TEST_INT = encode(TEST)
    print(TEST_INT)

    # read input
    input = b""
    if "," in TEST:
        with open("input.txt", "rb") as f:
            input = f.read()

    out = run(TEST_INT, input)
    print(repr(out))