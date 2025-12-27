# IntScript

IntScript is an esoteric programming language where the source code consists of only one nonnegative integer.

The integer shall not be written in different forms, such as with leading zeros or in another base.  
One can think of the integer as a real-world quantity, such as a count of objects. Writing the same value with leading zeros or in another base does not change that quantity, so **those representations are considered equivalent**.

## Execution

The memory is in the form of an infinite tape of cells indexed by integers (...-2, -1, 0, 1, 2...):
* All cell values are initialized to 0.
* The pointer is initialized to point to cell 0.
* Cells hold arbitrary-precision integers (can be as big as possible)

Input and output:
- Input reads bytes until a newline.
- Output is in the form of bytes (many bytes can be output in one go)

See [brainfuck](https://esolangs.org/wiki/Brainfuck) for more on this implementation.

## Commands

IntScript has 15 **commands** that dictate how cells are changed.
* There is a **normal alphabet** consisting of 15 4-bit binary codes representing each command.
* There is also an **extended alphabet** that has 31 5-bit codes, where some of them encode the command and a specific parameter in one code.

### Normal Alphabet

*The value of the pointer (the cell number that the pointer is pointing to) is `ptr`, and the tape is `tape`.*  
*The argument, `k`, is an integer that may be negative, and in some obvious cases, nonzero.*

| Code | Command          | Description                                                                           | Pseudocode                          | Needs Argument?  |
|------|------------------|---------------------------------------------------------------------------------------|-------------------------------------|------------------|
| 0000 | `MOVE k`         | Move the pointer                                                                      | `ptr += k`                          | ✓                |
| 0001 | `CADD k`         | Add a constant to the value of the current cell                                       | `tape[ptr] += k`                    | ✓                |
| 0010 | `IN`             | Set the value of the current cell to the input                                        | `tape[ptr]` = input                 |                  |
| 0011 | `OUT`            | Output the value of the current cell                                                  | output `tape[ptr]`                  |                  |
| 0100 | `LOOP { block }` | While the value of the current cell is nonzero, execute the commands inside the block | while `tape[ptr] != 0`, run `block` | ✓                |
| 0101 | `COPY k`         | Copy the value of the current cell to another cell                                    | `tape[ptr+k] = tape[ptr]`           | ✓                |
| 0110 | `SET k`          | Set the value of the current cell                                                     | `tape[ptr] = k`                     | ✓                |
| 0111 | `MUL k`          | Multiply the value of the current cell by the value of another cell                   | `tape[ptr] *= tape[ptr+k]`          | ✓                |
| 1000 | `DIV k`          | Divide the value of the current cell by the nonzero value of another cell             | `tape[ptr] //= tape[ptr+k]`         | ✓                |
| 1001 | `ADD k`          | Add the value of the current cell by the value of another cell                        | `tape[ptr] += tape[ptr+k]`          | ✓                |
| 1010 | `SUB k`          | Subtract the value of the current cell by the value of another cell                   | `tape[ptr] -= tape[ptr+k]`          | ✓                |
| 1011 | `SWAP k`         | Swap the values of two cells                                                          | swap `tape[ptr]` and `tape[ptr+k]`  | ✓                |
| 1100 | `IFZ { block }`  | If the value of the current cell is 0, execute the commands inside the block          | if `tape[ptr] == 0`, run `block`    | ✓                |
| 1101 | `CMUL k`         | Multiply the value of the current cell by a constant                                  | `tape[ptr] *= k`                    | ✓                |
| 1110 | `CDIV k`         | Divide the value of the current cell by a nonzero constant                            | `tape[ptr] //= k`                   | ✓                |

### Extended Alphabet

*Commands like `MOVE 1` include the argument for the command and do not require an argument.*  
*Commands like `MOVE k` are generic; they require an argument.*

| Code  | Command          | Needs Argument? | 
|-------|------------------|------------------|
| 00000 | `MOVE 1`         |                  |
| 00001 | `MOVE -1`        |                  |
| 00010 | `MOVE 2`         |                  |
| 00011 | `MOVE -2`        |                  |
| 00100 | `MOVE 3`         |                  |
| 00101 | `MOVE -3`        |                  | 
| 00110 | `MOVE k`         | ✓                |
| 00111 | `CADD -1`        |                  |
| 01000 | `CADD 1`         |                  |
| 01001 | `CADD k`         | ✓                |
| 01010 | `IN`             |                  |
| 01011 | `OUT`            |                  |
| 01100 | `LOOP { block }` | ✓                |
| 01101 | `COPY 1`         |                  |
| 01110 | `COPY 2`         |                  |
| 01111 | `COPY 3`         |                  |
| 10000 | `COPY k`         | ✓                |
| 10001 | `SET k`          | ✓                |
| 10010 | `MUL k`          | ✓                |
| 10011 | `DIV k`          | ✓                |
| 10100 | `ADD -1`         |                  |
| 10101 | `ADD 1`          |                  |
| 10110 | `ADD k`          | ✓                |
| 10111 | `SUB -1`         |                  |
| 11000 | `SUB 1`          |                  |
| 11001 | `SUB k`          | ✓                |
| 11010 | `SWAP 1`         |                  |
| 11011 | `SWAP k`         | ✓                |
| 11100 | `IFZ { block }`  | ✓                |
| 11101 | `CMUL k`         | ✓                |
| 11110 | `CDIV k`         | ✓                |

Notes:
* Floor division is used for the `DIV` and `CDIV` commands.
* Input reads bytes until a newline.

The reader may notice that there is no command whose code is `1111` (normal) or `11111` (extended). These are used as markers for the end of the blocks in `LOOP` and `IFZ` *(explained further below)*.

## Encoding

The encoder first creates a binary string, then converts that string to a decimal integer as the very last step.

**The encoding process is repeated** with different variables and choices the encoder can make. These variables are:
* The Golomb parameter used in the [Golomb coding](https://en.wikipedia.org/wiki/Golomb_coding) of command arguments (more below).
* Whether to use the normal alphabet or the extended one.
* Whether to use a special encoding method, reserved for programs that use few distinct commands (only in the normal alphabet). This method is called the **short alphabet** method.

### The Normal Method

#### Header

The binary string representing the source code has a header of 7 bits:  
`1/M/A/GGGG`

* `1` - The first bit is **always a 1**, to ensure that all 0s after it are counted.
* `M` - The second bit gives **the method**, the normal method (0) or the short alphabet method (1). In this case, it is a 0.
* `A` - The third bit gives **the alphabet**, whether to use the normal alphabet (1) or the extended alphabet (0).
* `GGGG` - The next four bits convey **the optimal Golomb parameter** for the program.
    * Ranges from 1 to 16
    * Shifted down by 1 (so 6 -> `0101`)

#### Body

**For each command**, the corresponding binary code for the command is appended to the string. Then, the argument is appended in one of two ways (if it is needed):

* **For a single-number argument *(e.g. `MOVE`, `ADD`)*:**
    * [ZigZag encoding](https://gist.github.com/mfuerstenau/ba870a29e16536fdbaba) is applied to the signed argument to make it unsigned.
    * The resulting integer is encoded using [Golomb coding](https://en.wikipedia.org/wiki/Golomb_coding), with its parameter differing for each encoding run, and then added to the string.

* **For an argument that has a block of code *(e.g. `LOOP`, `IFZ`)*:**
    * The binary encoding of the body of the command (the commands inside the `LOOP` or `IFZ` block) is appended.
    * The code `1111`/`11111` (normal/extended) is appended to show the end of the block. *(This is why there is no command with binary code `1111`/`11111`, as it is reserved for this.)*
        * This code is not appended at the end of the whole program, as it is unnecessary.

#### Example

To illustrate how encoding works, consider a simple program that computes the factorial of a number. *We will only go through one encoding run, with a Golomb parameter of 1 and using the extended alphabet (the most optimal choices).*


    # computes n!
    IN(),                    # c0 = n
    MOVE(1), SET(1),         # c1 = 1 (result)
    MOVE(-1),                # -> c0
    LOOP([
        MOVE(1), MUL(-1),    # -> c1 *= c0
        MOVE(-1), CADD(-1),  # -> c0--
    ]),
    MOVE(1), OUT(),          # c1 = n!


The code for `IN()` is `01010`, so that is the start of our string. Next, the code for `MOVE(1)`, which is `00000`, is added. This results in the string `0101000000`.  

Then the code for `SET()`, which is `10001`, is added (as there is no code for `SET(1)`). Then ZigZag is applied to the argument, `1`, which makes it `2`. The resulting Golomb coding for this (with a parameter of 1) is `001`. So we add `10001001` to the string.

This continues for `MOVE(-1)`, then we reach the `LOOP` command. After the code for `LOOP`, which is `01100`, its commands follow. Finally, a `11111` is added to mark the end of the block.

Finally, the resulting binary string is `01010000001000100100001011000000010010010000100111111110000001011`.  

To form the header, we:
* `1` - first add the leading `1`,
* `M` - then a `0` to show we are using the normal method,
* `A` - then a `0` to show we are using the extended alphabet,
* `GGGG` - and then the Golomb parameter, which is `0000` (conveying the number 1).

This makes the header `1000000`.

Finally, the binary string (with the header prepended) is converted to an integer, which in this case is `2372731743566560492555`. This number represents the operation of computing a factorial.

### The Short Alphabet Method

#### Header

Here, the header is 21 bits:  
`1/M/GGGG/C(15)`

* `1` - The first bit is **the leading 1**.
* `M` - The second bit gives **the method**, which, when the short alphabet method is being used, is a 1.
* `GGGG` - The next four bits are **the Golomb parameter**.
* `C(15)` - Next, there are 15 bits which describe which commands are used in the program:
    * Bit `0` corresponds to code `1110` (`CDIV`)
    * Bit `1` corresponds to code `1101` (`CMUL`)
    * ...
    * Bit `14` corresponds to code `0000` (`MOVE`)

*Note that the bit conveying the choice between the normal and extended alphabet is not added, since this method only works for the normal alphabet.*

#### Body

We assign a binary code to each command used in the program.  
If `LOOP` or `IFZ` is used, an explicit "end block" command is added to the short alphabet. This is used to mark the end of blocks in the body (replacing `1111`/`11111`).

The number of bits in the binary code used to represent each command is given by the formula `max(1, ceil(log2(num_cmds)))`, where `num_cmds` is the number of commands used in the program, including the end block command (if `LOOP` or `IFZ` is used).  

After this, each command is given a code with that number of bits, based on its position in the [normal alphabet table](#normal-alphabet). Commands that are higher in the table (i.e., generally used more frequently) get lesser-valued codes (`010 < 110`).

Next, we can finally encode the program. The logic is essentially the same as [the normal method](#body), just that the commands are the ones we calculated above, and the end block command may not be all 1s.

#### Example

Here, the example is a program that outputs "Hello, World!". *This time, the Golomb parameter is 16.*

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


There is no need for an end block command, because `LOOP` and `IFZ` are not used. This means that we can assign just one bit to each command. The highest command on the [normal alphabet table](#normal-alphabet) is `CADD`, so it is assigned a `0`, and `OUT` is assigned a 1.

The encoding of the first command, `CADD(72)`, is `000000000010000`, as the Golomb encoding of 72 is `00000000010000`, and we add another 0 before it to represent the `CADD` command. Then we add a `1` for the `OUT`, then another `0` for the `CADD`, and this continues.  
The final string representing the program is `000000000010000100001101010111101101011010000000001010110010111100000001111010000100001010110101101110111111000000000101011`.

To form the header, we:
* first add the leading `1`,
* then a `1` to show we are using the short alphabet method,
* then the Golomb parameter, which is `1111` (conveying the number 16),
* and then the command usage string. The only two commands used are `CADD` and `OUT`, so it is `000000000001010`.  

This makes the header `111111000000000001010`.

Finally, the program with the header prepended is converted to an integer, which in this case is `21952402398406275619735044350341700902682667`. This number represents outputting `"Hello, World!"`