# IntScript

IntScript is an esoteric programming language where the source code consists of only one nonnegative integer.

“Cheating” is not allowed; the integer must be written as a normal base-10 number in its simplest form, with  no leading zeros or alternative representations (such as writing it in a higher base to reduce the number of characters). One can think of the integer as a real-world quantity, such as a count of objects. Writing the same value with leading zeros or in another base does not change that quantity, so those representations are considered equivalent and invalid. Additionally, a count of something cannot be negative, so negative integers are also rejected.

## How It Works

For the inspiration behind this implementation, see [brainfuck](https://esolangs.org/wiki/Brainfuck).  

Imagine an array (representing memory) with cells. There is also pointer that can move to different cells. The pointer can edit and read the values of each cell.

The language has 15 commands that dictate how cells are changed. There is a **normal alphabet** consisting of 15 4-digit codes representing each command, and an **extended alphabet** that has 31 5-digit codes that represent a command and its parameter. In the below tables, the cell that the pointer is pointing to is labelled as `ptr` and the array is labelled as `array`.

### Normal Alphabet:

| Code | #  | Command          | Description                          |
|------|----|------------------|--------------------------------------|
| 0000 | 0  | `MOVE k`         | `ptr += k`                           |
| 0001 | 1  | `CADD k`         | `array[ptr] += k`                    |
| 0010 | 2  | `IN`             | input into `array[ptr]`             |
| 0011 | 3  | `OUT`            | output `array[ptr]`                  |
| 0100 | 4  | `LOOP { block }` | while `array[ptr] != 0`, run `block` |
| 0101 | 5  | `COPY k`         | `array[ptr+k] = array[ptr]`          |
| 0110 | 6  | `SET k`          | `array[ptr] = k`                     |
| 0111 | 7  | `MUL k`          | `array[ptr] *= array[ptr+k]`         |
| 1000 | 8  | `DIV k`          | `array[ptr] //= array[ptr+k]`        |
| 1001 | 9  | `ADD k`          | `array[ptr] += array[ptr+k]`         |
| 1010 | 10 | `SUB k`          | `array[ptr] -= array[ptr+k]`         |
| 1011 | 11 | `SWAP k`         | swap `array[ptr]` and `array[ptr+k]` |
| 1100 | 12 | `IFZ { block }`  | if `array[ptr] == 0`, run `block`    |
| 1101 | 13 | `CMUL k`         | `array[ptr] *= k`                    |
| 1110 | 14 | `CDIV k`         | `array[ptr] //= k`                   |

### Extended Alphabet:

| Code  | #  | Command   |
|-------|----|-----------|
| 00000 | 0  | `MOVE 1`  |
| 00001 | 1  | `MOVE -1` |
| 00010 | 2  | `MOVE 2`  |
| 00011 | 3  | `MOVE -2` |
| 00100 | 4  | `MOVE 3`  |
| 00101 | 5  | `MOVE -3` | 
| 00110 | 6  | `MOVE`    |
| 00111 | 7  | `CADD -1` |
| 01000 | 8  | `CADD 1`  |
| 01001 | 9  | `CADD`    |
| 01010 | 10 | `IN`      |
| 01011 | 11 | `OUT`     |
| 01100 | 12 | `LOOP`    |
| 01101 | 13 | `COPY 1`  |
| 01110 | 14 | `COPY 2`  |
| 01111 | 15 | `COPY 3`  |
| 10000 | 16 | `COPY`    |
| 10001 | 17 | `SET`     |
| 10010 | 18 | `MUL`     |
| 10011 | 19 | `DIV`     |
| 10100 | 20 | `ADD -1`  |
| 10101 | 21 | `ADD 1`   |
| 10110 | 22 | `ADD`     |
| 10111 | 23 | `SUB -1`  |
| 11000 | 24 | `SUB 1`   |
| 11001 | 25 | `SUB`     |
| 11010 | 26 | `SWAP 1`  |
| 11011 | 27 | `SWAP`    |
| 11100 | 28 | `IFZ`     |
| 11101 | 29 | `CMUL`    |
| 11110 | 30 | `CDIV`    |

Notes:
* Integer division is used for the `DIV` and `CDIV` commands.
* Input reads bytes until a newline.
* Cells have arbitrarily large memory size, meaning the program may output many bytes in one command

The reader may notice that there is no command whose code is `1111` (normal) or `11111` (extended). This is done intentionally, and will be explained later.

### Encoding

The encoding process is repeated with different parameters and choices the encoder can make. These variables are the Golomb parameter used in the [Golomb coding](https://en.wikipedia.org/wiki/Golomb_coding) of values (more below), and the decision of whether to use the normal alphabet or the extended one.

#### Header

The binary string representing the source code has a header of 6 bits.
* The first bit is always a 1, to ensure that all 0s after it are counted.
* The second bit determines whether to use the normal alphabet (1) or the extended alphabet (0).
* Bits 3-6 convey the optimal Golomb parameter, shifted down by 1 (so 6 becomes `0101`)

#### Body

**For each command**, the corresponding binary code for the command is appended to the string. Then, the argument is appended in one of two ways (if it is needed):

* **For a single-number argument *(e.g. `MOVE`, `ADD`)*:**
    * [ZigZag encoding](https://gist.github.com/mfuerstenau/ba870a29e16536fdbaba) is applied to the signed argument to make it unsigned.
    * The resulting integer is encoded using [Golomb coding](https://en.wikipedia.org/wiki/Golomb_coding), with the parameter differing for each encoding run, and then added to the string.

* **For an argument that has a block of code *(e.g. `LOOP`, `IFZ`)*:**
    * The binary encoding of the body of the command (the commands inside the `LOOP` or `IFZ` block) is appended.
    * The code `1111`/`11111` is appended to show the end of the block. *(This is why there is no command with binary code `1111`/`11111`, as it is reserved for this.)*


#### Example

To show how encoding works, let us take example of a simple program, which computes the factorial of a number. *We will only go through one encoding run, with a Golomb parameter of 1 and using the extended alphabet (the most optimal choices).*


    # computes n!
    IN(),                    # c0 = n
    MOVE(1), SET(1),         # c1 = 1 (result)
    MOVE(-1),                # -> c0
    LOOP([
        MOVE(1), MUL(-1),    # -> c1 *= c0
        MOVE(-1), CADD(-1),  # -> c0--
    ]),
    MOVE(1), OUT(),          # c1 = n!


The code for `IN()` is `01010`, so that is the start of our string.  
Next, the code for `MOVE(1)`, which is `00000`, is added. This results in the string `0101000000`.  
Then the code for `SET()`, which is `10001`, is added (as there is no code for `SET(1)`.) Then ZigZag is applied on the argument, `1`, which makes it `2`. The resulting Golomb coding for this (with a parameter of 1) is `001`. This results in the string `10001001`.

This continues for `MOVE(-1)`, then we reach the `LOOP` command.  
After the code for `LOOP`, which is `01100`, its commands follow, and finally a `11111` is added to show the end of the block.

Continuing with this, the resulting binary string is `01010000001000100100001011000000010010010000100111111110000001011`.  
To form the header, we:
* first add the leading 1,
* then the 0 to show we are using the extended alphabet,
* and then the Golomb parameter, which is `0000` (conveying the number 1).

This makes the header `100000`.

Finally, the binary string is converted to an integer, which in this case is `1192140122849149189131`. This number represents the operation of computing a factorial.
