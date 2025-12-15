from __future__ import annotations

def encode(s: str) -> int:
    output = ""

    for c in s:
        match c:
            case ">": output += "0"
            case "<": output += "1"
            case "+": output += "2"
            case "-": output += "3"
            case ".": output += "4"
            case ",": output += "5"
            case "[": output += "6"
            case "]": output += "7"

    return int("1" + output, 8)