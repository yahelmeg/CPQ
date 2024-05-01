# CPQ
Compiler from the language CPL to the language QUAD

## Project Structure
- `cpq.py` - Main file for CPQ , calls the code gen function on the starting node of the input.
- `lexer.py` - Uses regex to convert the input into tokens.
- `parser.py` - Parses the input by using the tokens provided by the lexer , follows the rules of the language CPL to check if the input has any syntax errors, constructs the Abstract Syntax Tree if there aren't any.
- `ast_nodes.py` - Defines classes for every type of node according to the rules of the CPL language , every class has a code_gen method used to create the QUAD language output. 
- `header.py` - Contains helper methods used by the other files.



