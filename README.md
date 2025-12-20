# IntScript

IntScript is an esoteric programming language where the source code consists of only one integer.

“Cheating” is not allowed; the integer must be written as a normal base-10 number in its simplest form, with no leading zeros or alternative representations (such as writing it in a higher base to reduce the number of characters). One can think of the integer as a real-world quantity, such as a count of objects. Writing the same value with leading zeros or in another base does not change that quantity, so those representations are considered equivalent and invalid.

## How It Works

For the inspiration behind this implementation, see [brainfuck](https://esolangs.org/wiki/Brainfuck).  

Imagine an array (representing memory) with cells. There is also pointer that can move to different cells. The pointer can edit and read the values of each cell.

The language has 16 commands that dictate how cells are changed.
*(here, the cell that the pointer is pointing to is labelled as `ptr` and the array is labelled as `array`)*

| Binary code | #  | Command          | Description                          |
|---:         |---:|---               |---                                   |
| 0000        | 0  | `MOVE k`         | `ptr += k`                           |
| 0001        | 1  | `CADD k`         | `array[ptr] += k`                    |
| 0010        | 2  | `SET k`          | `array[ptr] = k`                     |
| 0011        | 3  | `ADD k`          | `array[ptr] += array[ptr+k]`         |
| 0100        | 4  | `SUB k`          | `array[ptr] -= array[ptr+k]`         |
| 0101        | 5  | `COPY k`         | `array[ptr+k] = array[ptr]`          |
| 0110        | 6  | `SWAP k`         | swap `array[ptr]` and `array[ptr+k]` |
| 0111        | 7  | `LOOP { block }` | while `array[ptr] != 0`, run `block` |
| 1000        | 8  | `IFZ { block }`  | if `array[ptr] == 0`, run `block`    |
| 1001        | 9  | `IFNZ { block }` | if `array[ptr] != 0`, run `block`    |
| 1010        | 10 | `OUT`            | output `array[ptr]`                  |
| 1011        | 11 | `IN`             | input into `array[ptr]`              |
| 1100        | 12 | `MUL k`          | `array[ptr] *= array[ptr+k]`         |
| 1101        | 13 | `CMUL k`         | `array[ptr] *= k`                    |
| 1110        | 14 | `DIV k`          | `array[ptr] //= array[ptr+k]`        |
| 1111        | 15 | `CDIV k`         | `array[ptr] //= k`                   |

Notes:
* All writes to cells are taken mod 256.
* Integer division is used for the `DIV` and `CDIV` commands.

### Encoding

The encoding for a program outputs a single ternary (base-3) number, which is then converted to an integer. Each encoding starts with a blank ternary string.

**For each command:**
* The corresponding *binary* code for the command (see the table above) is appended to the *ternary* string. *(the mismatch between the two bases may seem confusing, but it will be explained later.)*

* **For a single-number argument *(e.g. MOVE, ADD)*:**
    * [ZigZag encoding](https://gist.github.com/mfuerstenau/ba870a29e16536fdbaba) is applied to the signed integer to make it unsigned.
    * It is appended after the binary code.

* **For an argument that is a block of code *(e.g. LOOP, IFZ)*:**
    * The number of commands (the length of the block) is appended as an unsigned number.  
    Note that **ZigZag is not applied here**, as the number of commands is always positive.
    * The binary representing the block of code is appended.

* Finally, a 2 is appended to the ternary string to signify the end of the command. This 2 is what makes the otherwise-binary string ternary.

#### Example

To show how encoding works, let us take example of a simple program, which computes the factorial of a number.


    # computes n!
    IN(),                    # c0 = n
    MOVE(1), SET(1),         # c1 = 1 (result)
    MOVE(-1),                # -> c0
    LOOP([
        MOVE(1), MUL(-1),    # -> c1 *= c0
        MOVE(-1), CADD(-1),  # -> c0--
    ]),
    MOVE(1), OUT(),          # c1 = n!


The code for `IN()` is `1011`, so that is the start of our string.  
Next, the code for `MOVE()`, which is `0000`, is added.  
Then ZigZag is applied on the argument, `1`, which makes it `2`, which has a binary representation of `10`. Then the `2` is added to mark the end of the command.   
This results in the string `10110000102`. This continues for `SET(1)` and `MOVE(-1)`, until we reach the `LOOP` command.  

The `LOOP` block has four commands, so the start of the command will be `0111` (the code for `LOOP`) followed by `100` (4) and `2`. Then, the encoding of the commands in the `LOOP` block follow.

Continuing with this, the resulting ternary string is `101100001020010102000012011110020000102110012000012000112200001021010`.  
Then a leading 1 is added to ensure that, if the string were to start with a 0, all bits are still counted.

Finally, the final string is converted to an integer, which in this case is `1153769773189057279566187875308922`. This number represents the program of computing a factorial.
