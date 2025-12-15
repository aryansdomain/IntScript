def interpret_bf(bfk: str, input: bytes = b"") -> str:
    tape = [0] * 30000
    ptr = 0
    input_ptr = 0
    output = bytearray()

    pc = 0
    code_len = len(bfk)
    while pc < code_len:
        cmd = bfk[pc]

        if cmd == ">":
            ptr += 1
            if ptr >= len(tape):
                tape.append(0)

        elif cmd == "<":
            ptr -= 1
            if ptr < 0: # change starting point
                tape.insert(0, 0)
                ptr = 0

        elif cmd == "+":
            tape[ptr] = (tape[ptr] + 1) & 0xFF # & to avoid overflow

        elif cmd == "-":
            tape[ptr] = (tape[ptr] - 1) & 0xFF # & to avoid underflow

        elif cmd == ".":
            output.append(tape[ptr])

        elif cmd == ",":
            if input_ptr < len(input):
                tape[ptr] = input[input_ptr]
                input_ptr += 1
            else:
                tape[ptr] = 0

        elif cmd == "[":
            if tape[ptr] == 0:
                depth = 1
                pc += 1
                # find matching ]
                while pc < code_len and depth > 0:
                    if   bfk[pc] == "[": depth += 1
                    elif bfk[pc] == "]": depth -= 1
                    pc += 1
                continue

        elif cmd == "]":
            if tape[ptr] != 0:
                depth = 1
                pc -= 1
                # go back to matching [
                while pc >= 0 and depth > 0:
                    if   bfk[pc] == "]": depth += 1
                    elif bfk[pc] == "[": depth -= 1
                    pc -= 1
                pc += 1
                continue

        pc += 1

    return output.decode("latin1")

def decode(n: int) -> str:
    b = bin(n)[3:]  # remove '0b' and leading 1
    bfk = ""

    for i in range(0, len(b), 3):
        chr = b[i:i+3]
        match chr:
            case "000": bfk += ">"
            case "001": bfk += "<"
            case "010": bfk += "+"
            case "011": bfk += "-"
            case "100": bfk += "."
            case "101": bfk += ","
            case "110": bfk += "["
            case "111": bfk += "]"

    return bfk

def run(n: int, input: bytes = b"") -> str:
    bfk = decode(n)
    return interpret_bf(bfk, input)
