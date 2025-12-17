from __future__ import annotations
from dataclasses import dataclass
from typing import List, Union

# ------------------------ Instructions ------------------------

@dataclass(frozen=True)
class ADD:
    k: int
@dataclass(frozen=True)
class MOVE:
    k: int
@dataclass(frozen=True)
class SET:
    k: int
@dataclass(frozen=True)
class LOOP:
    body: List["Instructions"]
@dataclass(frozen=True)
class OUT:
    pass
@dataclass(frozen=True)
class IN:
    pass
@dataclass(frozen=True)
class COPY:
    k: int
@dataclass(frozen=True)
class MUL:
    k: int

Instructions = Union[ADD, MOVE, SET, LOOP, OUT, IN, COPY, MUL]

# ------------------------ Interpret ------------------------

def interpret(program: List[Instructions], input: bytes = b"") -> bytes:
    tape = {}
    ptr = 0
    in_pos = 0
    out = bytearray()

    def set_cell(i: int, v: int) -> None:
        tape[i] = v & 0xFF
    def get_cell(i: int) -> int:
        return tape.get(i, 0)

    def exec_block(block: List[Instructions]) -> None:
        nonlocal ptr, in_pos
        for ins in block:

            if isinstance(ins, ADD):
                set_cell(ptr, get_cell(ptr) + ins.k)

            elif isinstance(ins, MOVE):
                ptr += ins.k

            elif isinstance(ins, SET):
                set_cell(ptr, ins.k)
            
            elif isinstance(ins, LOOP):
                while get_cell(ptr) != 0:
                    exec_block(ins.body)

            elif isinstance(ins, OUT):
                out.append(get_cell(ptr) & 0xFF)

            elif isinstance(ins, IN):
                # skip \n and \r
                while in_pos < len(input) and input[in_pos] in (10, 13):
                    in_pos += 1

                # read one byte, set current cell
                if in_pos < len(input):
                    set_cell(ptr, input[in_pos])
                    in_pos += 1
                else:
                    set_cell(ptr, 0)

            elif isinstance(ins, COPY):
                set_cell(ptr + ins.k, get_cell(ptr))

            elif isinstance(ins, MUL):
                set_cell(ptr, get_cell(ptr) * get_cell(ptr + ins.k))

            else:
                raise TypeError(f"Unknown instruction: {ins}")

    exec_block(program)
    return bytes(out)
