from __future__ import annotations
from dataclasses import dataclass

# ------------------------ Instructions ------------------------

@dataclass(frozen=True)
class MOVE:
    k: int
@dataclass(frozen=True)
class CADD:
    k: int
@dataclass(frozen=True)
class IN:
    pass
@dataclass(frozen=True)
class OUT:
    pass
@dataclass(frozen=True)
class LOOP:
    body: list
@dataclass(frozen=True)
class COPY:
    k: int
@dataclass(frozen=True)
class SET:
    k: int
@dataclass(frozen=True)
class MUL:
    k: int
@dataclass(frozen=True)
class DIV:
    k: int
@dataclass(frozen=True)
class ADD:
    k: int
@dataclass(frozen=True)
class SUB:
    k: int
@dataclass(frozen=True)
class SWAP:
    k: int
@dataclass(frozen=True)
class IFZ:
    body: list
@dataclass(frozen=True)
class CMUL:
    k: int
@dataclass(frozen=True)
class CDIV:
    k: int

Commands = [MOVE, CADD, IN, OUT, LOOP, COPY, SET, MUL, DIV, ADD, SUB, SWAP, IFZ, CMUL, CDIV]

# ------------------------ Interpret ------------------------

def interpret(program: list, input: bytes = b"") -> bytes:
    tape = {}
    ptr = 0
    in_pos = 0
    out = bytearray()

    def set_cell(i: int, v: int) -> None:
        tape[i] = v
    def get_cell(i: int) -> int:
        return tape.get(i, 0)

    def exec_block(block: list) -> None:
        nonlocal ptr, in_pos
        for ins in block:

            if isinstance(ins, MOVE):
                ptr += ins.k

            elif isinstance(ins, CADD):
                set_cell(ptr, get_cell(ptr) + ins.k)

            elif isinstance(ins, SET):
                set_cell(ptr, ins.k)

            elif isinstance(ins, ADD):
                set_cell(ptr, get_cell(ptr) + get_cell(ptr + ins.k))

            elif isinstance(ins, SUB):
                set_cell(ptr, get_cell(ptr) - get_cell(ptr + ins.k))

            elif isinstance(ins, COPY):
                set_cell(ptr + ins.k, get_cell(ptr))

            elif isinstance(ins, SWAP):
                a = get_cell(ptr)
                b = get_cell(ptr + ins.k)
                set_cell(ptr, b)
                set_cell(ptr + ins.k, a)
            
            elif isinstance(ins, LOOP):
                while get_cell(ptr) != 0:
                    exec_block(ins.body)

            elif isinstance(ins, IFZ):
                if get_cell(ptr) == 0:
                    exec_block(ins.body)
        
            elif isinstance(ins, OUT):
                v = get_cell(ptr)
                nbytes = max(1, (v.bit_length() + 8) // 8)
                out.extend(v.to_bytes(nbytes, byteorder="big", signed=True))

            elif isinstance(ins, IN):
                # read bytes up to newline (or EOF)
                if in_pos >= len(input):
                    set_cell(ptr, 0)
                else:
                    newline_pos = input.find(b"\n", in_pos)
                    if newline_pos == -1:
                        chunk = input[in_pos:]
                        in_pos = len(input)
                    else:
                        chunk = input[in_pos:newline_pos]
                        in_pos = newline_pos + 1
                    if len(chunk) == 0:
                        set_cell(ptr, 0)
                    else:
                        set_cell(ptr, int.from_bytes(chunk, byteorder="big", signed=True))

            elif isinstance(ins, MUL):
                set_cell(ptr, get_cell(ptr) * get_cell(ptr + ins.k))

            elif isinstance(ins, CMUL):
                set_cell(ptr, get_cell(ptr) * ins.k)

            elif isinstance(ins, DIV):
                divisor = get_cell(ptr + ins.k)
                if divisor == 0:
                    raise ZeroDivisionError("DIV with divisor 0")
                set_cell(ptr, get_cell(ptr) // divisor)

            elif isinstance(ins, CDIV):
                if ins.k == 0:
                    raise ZeroDivisionError("CDIV with divisor 0")
                set_cell(ptr, get_cell(ptr) // ins.k)

            else:
                raise TypeError(f"Unknown instruction: {ins}")

    exec_block(program)
    return bytes(out)
