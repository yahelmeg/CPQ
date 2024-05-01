from lexer import *
from ply.yacc import yacc
from ast_nodes import *
from header import symbol_table
from sys import stderr

# Define Grammar rules and build the AST
def p_program(p):
    '''program :  declarations  stmt_block'''
    p[0] = ProgramNode(p[1],p[2])


def p_declarations(p):
    '''declarations : declarations declaration
                    |'''
    if len(p) > 1:
        if p[1] is None:
            p[0] = DeclarationsNode()
        else:
            p[1].add_declaration(p[2])
            p[0] = p[1]
    else:
        p[0] = None


def p_declaration(p):
    '''declaration : idlist COLON type SEMICOLON'''
    p[0] = DeclarationNode(p[1], p[3])
    # Build symbol_table
    for variable in p[1].ids:
        if variable in symbol_table:
            stderr.write(f"Semantic Error: Identifier {variable} was already declared.")
        symbol_table[variable] = p[3].idtype


def p_type(p):
    '''type : INT
            | FLOAT'''
    p[0] = TypeNode(p[1])


def p_idlist(p):
    '''idlist : idlist COMMA ID
              | ID'''
    if len(p) > 2:
        if p[1] is None:
            p[0] = IdListNode()
        else:
            p[1].add_id(p[3])
            p[0] = p[1]
    else:
        p[0] = IdListNode()
        p[0].add_id(p[1])


def p_stmt(p):
    '''stmt : assignment_stmt
            | input_stmt
            | output_stmt
            | if_stmt
            | while_stmt
            | stmt_block'''
    p[0] = StmtNode(p[1])


def p_assignment_stmt(p):
    '''assignment_stmt : ID ASSIGN expression SEMICOLON '''
    p[0] = AssignmentStmtNode(p[1],p[3])


def p_input_stmt(p):
    '''input_stmt : INPUT LPAREN ID RPAREN SEMICOLON '''
    p[0] = InputStmtNode(p[3])


def p_output_stmt(p):
    '''output_stmt : OUTPUT LPAREN expression RPAREN SEMICOLON '''
    p[0] = OutputStmtNode(p[3])


def p_if_stmt(p):
    '''if_stmt : IF LPAREN boolexpr RPAREN stmt ELSE stmt'''
    p[0] = IfStmtNode(p[3], p[5], p[7])


def p_while_stmt(p):
    '''while_stmt : WHILE LPAREN boolexpr RPAREN stmt'''
    p[0] = WhileStmtNode(p[3], p[5])


def p_stmt_block(p):
    '''stmt_block : LBRACE stmtlist RBRACE '''
    p[0] = StmtBlockNode(p[2])


def p_stmtlist(p):
    '''stmtlist : stmtlist stmt
                |'''
    if len(p) > 1:
        if p[1] is None:
            p[0] = StmtListNode()
            p[0].add_stmt(p[2])
        else:
            p[1].add_stmt(p[2])
            p[0] = p[1]
    else:
        p[0] = None


def p_boolexpr_or(p):
    '''boolexpr : boolexpr OR boolterm
                | boolterm'''
    if len(p) > 2:
        p[0] = OrExprNode(p[1], p[3])
    else:
        p[0] = p[1]


def p_boolterm_and(p):
    '''boolterm : boolterm AND boolfactor
                | boolfactor'''
    if len(p) > 2:
        p[0] = AndExprNode(p[1], p[3])
    else:
        p[0] = p[1]


def p_boolfactor_not(p):
    '''boolfactor : NOT LPAREN boolexpr RPAREN
                  | expression relop expression'''
    if len(p) > 4:
        p[0] = NotExprNode(p[3])
    else:
        p[0] = RelExprNode(p[1],p[2],p[3])


def p_relop(p):
    '''relop : EQUAL
             | NOTEQUAL
             | LESSER
             | GREATER
             | EQUALORLOWER
             | EQUALORGREATER'''
    p[0] = p[1]


def p_expression_addop(p):
    '''expression : expression addop term
                  | term'''
    if len(p) > 2:
        p[0] = ExpressionNode(p[1],p[2],p[3])
    else:
        p[0] = ExpressionNode(p[1])


def p_addop(p):
    '''addop : PLUS
             | MINUS'''
    p[0] = p[1]


def p_term_mulop(p):
    '''term : term mulop factor
            | factor'''
    if len(p) > 2:
        p[0] = TermNode(p[1], p[2], p[3])
    else:
        p[0] = TermNode(p[1])


def p_mulop(p):
    '''mulop : MULTIPLY
             | DIVIDE'''
    p[0] = p[1]


def p_factor_expression(p):
    '''factor : LPAREN expression RPAREN '''
    p[0] = p[2]


def p_factor_id(p):
    '''factor : ID '''
    p[0] = FactorNode(p[1])


def p_factor_int_num(p):
    '''factor : INT_NUM '''
    p[0] = FactorNode(p[1])


def p_factor_float_num(p):
    '''factor : FLOAT_NUM '''
    p[0] = FactorNode(p[1])


def p_cast_int(p):
    '''factor : STATIC_CAST_INT LPAREN expression RPAREN '''
    p[0] = CastIntExpressionNode(p[3])


def p_cast_float(p):
    '''factor : STATIC_CAST_FLOAT LPAREN expression RPAREN '''
    p[0] = CastFloatExpressionNode(p[3])


# Error rule for syntax errors
def p_error(p):
    if p:
        print(f"Syntax error at token {p.value}, line {p.lineno} ")
    else:
        print("Syntax error: Unexpected end of input")


# Build the parser
parser = yacc()


# Function to parse input
def parse_input(data):
    # Tokenize and parse the input
    lexer.input(data)
    ast = parser.parse(lexer=lexer)
    return ast
