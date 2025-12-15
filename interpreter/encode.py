from __future__ import annotations

def encode(s: str) -> int:
    output = ""

    for c in s:
        match c:
            case ">": output += "000"
            case "<": output += "001"
            case "+": output += "010"
            case "-": output += "011"
            case ".": output += "100"
            case ",": output += "101"
            case "[": output += "110"
            case "]": output += "111"

    return int("1" + output, 2)