from ply.lex import lex

# List of token names
tokens = (
    'ELSE', 'FLOAT', 'IF', 'INPUT', 'INT', 'OUTPUT', 'WHILE',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COMMA', 'COLON', 'SEMICOLON', 'ASSIGN',
    'EQUAL', 'NOTEQUAL', 'LESSER', 'GREATER', 'EQUALORLOWER', 'EQUALORGREATER',
    'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'OR', 'AND', 'NOT', 'STATIC_CAST_INT', 'STATIC_CAST_FLOAT',
    'ID', 'INT_NUM', 'FLOAT_NUM'
)

# Regular expression rules for simple tokens
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','
t_COLON = r':'
t_SEMICOLON = r';'
t_ASSIGN = r'='
t_EQUAL = r'=='
t_NOTEQUAL = r'!='
t_LESSER = r'<'
t_GREATER = r'>'
t_EQUALORLOWER = r'<='
t_EQUALORGREATER = r'>='
t_OR = r'\|\|'
t_AND = r'&&'
t_NOT = r'!'

# Count line number
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# Handle variable names
def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t


# Handle float numbers
def t_FLOAT_NUM(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t


# Handle numbers integers
def t_INT_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t


# Skip tabs and spaces
t_ignore = ' \t'


# Skip comments
def t_COMMENT(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')  # Count lines in comments that go over multiple lines
    pass


# Handle illegal characters
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Handle reserved keywords
reserved = {
    'else': 'ELSE',
    'float': 'FLOAT',
    'if': 'IF',
    'input': 'INPUT',
    'int': 'INT',
    'output': 'OUTPUT',
    'while': 'WHILE',
    'staticcastint': 'STATIC_CAST_INT',
    'staticcastfloat': 'STATIC_CAST_FLOAT'

}


# Build the lexer
lexer = lex()





