# CPQ
Compiler from the language CPL to the language QUAD

## Project Structure
- `cpq.py` - Main file for CPQ , calls the code gen function on the starting node of the input.
- `lexer.py` - Uses regex to convert the input into tokens.
- `parser.py` - Parses the input by using the tokens provided by the lexer , follows the rules of the language CPL to check if the input has any syntax errors, constructs the Abstract Syntax Tree if there aren't any.
- `ast_nodes.py` - Defines classes for every type of node according to the rules of the CPL language , every class has a code_gen method used to create the QUAD language output. 
- `header.py` - Contains helper methods used by the other files.


# Code Examples
<table>
    <tr>
        <th>CPL</th>
        <th>Quad</th>
    </tr>
    <tr>
<td>

```c
/* Finding minimum between two numbers */
a, b: float;
{
    input(a);
    input(b);
    if (a < b)
        output(a);
    else
        output(b);
}
```

</td>
<td>

```{assembly, attr.source='.numberLines'}
RINP a
RINP b
RLSS t1 a b
JMPZ L1 t1
RPRT a
JUMP L2
L1:
RPRT b
L2:
HALT
```

```c
/* Sum a list of integers */
N, num, sum : int;
{
    sum = 0;
    while (N > 0) {
        input(num);
        sum = sum + num;
        N = N - 1;
    }
    output(sum);
}
```

</td>
<td>

```{assembly, attr.source='.numberLines'}
IASN sum 0
L1:
IGRT t1 N 0
JMPZ L2 t1 
IINP num
IADD sum sum num
ISUB N N 1
JUMP L1
L2:
IPRT sum
HALT
```

</td>
    </tr>
    <tr>
<td>
