"""
This module contains constants and declared types used in interpreter 
"""

from typing import Callable, Optional

from .structures import Token, Node, Function

KEYWORDS = ['start', 'end', 'use', 'return', 'break',
            'while', 'if', 'else', 'elif']
OPERATORS = ['+', '-', '*', '/', '%', '(', ')', 'is', 'and',
             'or', 'not', '>', '<', '<=', '>=', '==', '!=', '|', '=']
BOOLEANS = ['true', 'false']
NUMERALS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
INNER_TYPES = ['int', 'float', 'str', 'bool']
TOKEN_TYPES = ['kwd', 'int', 'float', 'str', 'bool', 'opr', 'fnc',
               'var', 'sep', 'lib', 'typ']

SPECIAL_SYMBOLS = ['=', '|', ' ', '+', '-', '/', '*', '%', '(', ')', '>', '<', ',', '!']

PIPE = Token('opr', '|')
CREATE = Token('opr', 'is')
ASSIGN = Token('opr', '=')
PLUS = Token('opr', '+')
MINUS = Token('opr', '-')
MULTIPLY = Token('opr', '*')
DIVIDE = Token('opr', '/')
MODULO = Token('opr', '%')
MORE_THAN = Token('opr', '>')
LESS_THAN = Token('opr', '<')
NO_LESS_THAN = Token('opr', '>=')
NO_MORE_THAN = Token('opr', '<=')
EQUALS = Token('opr', '==')
NOT_EQUALS = Token('opr', '!=')

USE = Token('kwd', 'use')
RETURN = Token('kwd', 'return')
BREAK = Token('kwd', 'break')
IF = Token('kwd', 'if')
ELSE = Token('kwd', 'else')
WHILE = Token('kwd', 'while')
START = Token('kwd', 'start')
END = Token('kwd', 'end')

LEFT_BRACKET = Token('opr', '(')
RIGHT_BRACKET = Token('opr', ')')

COMMA = Token('sep', ',')

INT = Token('typ', 'int')
FLOAT = Token('typ', 'float')
BOOL = Token('typ', 'bool')
STR = Token('typ', 'str')

TRUE = Token('bool', True)
FALSE = Token('bool', False)

TokenList = list[Token | Node | list]

OPERATOR_TOKENS: TokenList = [PIPE, CREATE, ASSIGN, PLUS, MINUS, MULTIPLY, DIVIDE,
                              MODULO, MORE_THAN, LESS_THAN, EQUALS]
KEYWORD_TOKENS: TokenList = [RETURN, BREAK, IF, ELSE, WHILE, START, END]

PyFunction = list[Callable | list[str]]
CallablesList = dict[str, PyFunction | Function]
VariablesList = dict[int, dict]
ExecutionResult = tuple[Optional[Token], bool]
