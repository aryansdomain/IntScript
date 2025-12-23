# IntScript

IntScript is an esoteric programming language where the source code consists of only one nonnegative integer.

“Cheating” is not allowed; the integer must be written as a normal base-10 number in its simplest form, with no leading zeros or alternative representations (such as writing it in a higher base to reduce the number of characters). One can think of the integer as a real-world quantity, such as a count of objects. Writing the same value with leading zeros or in another base does not change that quantity, so those representations are considered equivalent and invalid. Additionally, a count of something cannot be negative, so negative integers are also rejected.

## How It Works

For the inspiration behind this implementation, see [brainfuck](https://esolangs.org/wiki/Brainfuck).  

Imagine an array (representing memory) with cells. There is also pointer that can move to different cells. The pointer can edit and read the values of each cell.

The language has 15 commands that dictate how cells are changed.
*(here, the cell that the pointer is pointing to is labelled as `ptr` and the array is labelled as `array`)*

| Binary code | #  | Command          | Description                              |
|---:         |---:|---               |---                                       |
| 0000        | 0  | `MOVE k`         | `ptr += k`                               |
| 0001        | 1  | `CADD k`         | `array[ptr] += k`                        |
| 0010        | 2  | `IN`             | input into `array[ptr]`                  |
| 0011        | 3  | `OUT`            | output `array[ptr]`                      |
| 0100        | 4  | `LOOP { block }` | while `array[ptr] != 0`, run `block`     |
| 0101        | 5  | `COPY k`         | `array[ptr+k] = array[ptr]`              |
| 0110        | 6  | `SET k`          | `array[ptr] = k`                         |
| 0111        | 7  | `MUL k`          | `array[ptr] *= array[ptr+k]`             |
| 1000        | 8  | `DIV k`          | `array[ptr] //= array[ptr+k]`            |
| 1001        | 9  | `ADD k`          | `array[ptr] += array[ptr+k]`             |
| 1010        | 10 | `SUB k`          | `array[ptr] -= array[ptr+k]`             |
| 1011        | 11 | `SWAP k`         | swap `array[ptr]` and `array[ptr+k]`     |
| 1100        | 12 | `IFZ { block }`  | if `array[ptr] == 0`, run `block`        |
| 1101        | 13 | `CMUL k`         | `array[ptr] *= k`                        |
| 1110        | 14 | `CDIV k`         | `array[ptr] //= k`                       |

Notes:
* Integer division is used for the `DIV` and `CDIV` commands.

The reader may notice that there is no command whose code is `1111`. This is done intentionally, and will be explained later.

### Encoding

The program is encoded multiple times, each time with a different Golomb parameter M (the parameter for the [Golomb coding](https://en.wikipedia.org/wiki/Golomb_coding) used). M ranges from 1 and 16 inclusive.

**For each command:**
* The corresponding binary code for the command (see the table above) is appended to the string.

* **For a single-number argument *(e.g. `MOVE`, `ADD`)*:**
    * [ZigZag encoding](https://gist.github.com/mfuerstenau/ba870a29e16536fdbaba) is applied to the signed argument to make it unsigned.
    * The resulting integer is encoded using Golomb coding, with the M-value differing for each encoding run, and then added to the string.

* **For an argument that has a block of code *(e.g. `LOOP`, `IFZ`)*:**
    * The binary encoding of the body of the command (the commands inside the `LOOP` or `IFZ` block) is appended.
    * The code `1111` is appended to show the end of the block. *(This is why there is no command with binary code `1111`, as it is reserved for this.)*

Then, a header of 5 bits is attached to the front of the block:
* One bit is a leading 1 (to ensure all bits are counted)
* Four bits convey the Golomb parameter, but shifted down by 1.
    * For example, a parameter of 1 would be encoded as 1 - 1 = `0000` and a parameter of 14 becomes 14 - 1 = `1101`. This ensures the range fits into four bits.


#### Example

To show how encoding works, let us take example of a simple program, which computes the factorial of a number. *We will only go through one encoding run, with a Golomb parameter of 1 (which turns out to be the most optimal one).*


    # computes n!
    IN(),                    # c0 = n
    MOVE(1), SET(1),         # c1 = 1 (result)
    MOVE(-1),                # -> c0
    LOOP([
        MOVE(1), MUL(-1),    # -> c1 *= c0
        MOVE(-1), CADD(-1),  # -> c0--
    ]),
    MOVE(1), OUT(),          # c1 = n!


The code for `IN()` is `0010`, so that is the start of our string.  
Next, the code for `MOVE()`, which is `0000`, is added.  
Then ZigZag is applied on the argument, `1`, which makes it `2`. The resulting Golomb coding for this (with a parameter of 1) is `001`.  
This results in the string `00100000001`. This continues for `SET(1)` and `MOVE(-1)`, until we reach the `LOOP` command.  
After the code for `LOOP`, which is `0100`, its commands follow, and finally a `1111` is added to show the end of the block.

Continuing with this, the resulting binary string is `00100000001011000100000101000000001011101000001000101111100000010011`.  
Then, the Golomb parameter, which is `0000` (conveying the number 1), is attached to the front, and the leading 1 is prepended before it.

Finally, the binary string is converted to an integer, which in this case is `4759459277303292557331`. This number represents the operation of computing a factorial.
