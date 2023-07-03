# pylint: skip-file
import pytest

from interpreter.min_parser import *  # noqa
from interpreter.utils.commons import *  # noqa


# region Testing parse_line

def test_parse_line_dry_run_invalid():
    assert parse_line(None, 1) is None
    assert parse_line([], 0) is None
    assert parse_line([], -1) is None
    assert True


def test_parse_line_simple_inputs():
    line1 = [Token('int', 1), PLUS, Token('int', 2)]
    expected1 = Node(PLUS, 1, [Token('int', 2)], [Token('int', 1)])
    assert parse_line(line1, 1) == expected1

    line2 = [Token('int', 2), MULTIPLY, Token('float', 3.3)]
    expected2 = Node(MULTIPLY, 1, [Token('float', 3.3)], [Token('int', 2)])
    assert parse_line(line2, 1) == expected2

    line3 = [Token('float', 3.5), DIVIDE, Token('int', 2)]
    expected3 = Node(DIVIDE, 1, [Token('int', 2)], [Token('float', 3.5)])
    assert parse_line(line3, 1) == expected3

    line4 = [Token('float', 3.5), MINUS, Token('int', 2)]
    expected4 = Node(MINUS, 1, [Token('int', 2)], [Token('float', 3.5)])
    assert parse_line(line4, 1) == expected4

    line5 = [Token('float', 3.5), MODULO, Token('int', 2)]
    expected5 = Node(MODULO, 1, [Token('int', 2)], [Token('float', 3.5)])
    assert parse_line(line5, 1) == expected5

    line6 = [Token('fnc', 'out'), PIPE, Token('var', 'num2')]
    expected6 = Node(PIPE, 1, [Token('var', 'num2')], [Token('fnc', 'out')])
    assert parse_line(line6, 1) == expected6

    line7 = [Token('fnc', 'add'), PIPE, Token('var', 'num1'), COMMA, Token('var', 'num2')]
    expected7 = Node(PIPE, 1, Node(COMMA, 1, [Token('var', 'num2')], [Token('var', 'num1')]), [Token('fnc', 'add')])
    assert parse_line(line7, 1) == expected7

    line8 = [Token('var', 'num1'), CREATE, INT]
    expected8 = Node(CREATE, 1, INT, Token('var', 'num1'))
    assert parse_line(line8, 1) == expected8

    line9 = [Token('var', 'num1'), ASSIGN, Token('int', 2)]
    expected9 = Node(ASSIGN, 1, [Token('int', 2)], [Token('var', 'num1')])
    assert parse_line(line9, 1) == expected9

    line10 = [BREAK]
    expected10 = Node(BREAK, 1)
    assert parse_line(line10, 1) == expected10

    line11 = [RETURN]
    expected11 = Node(RETURN, 1)
    assert parse_line(line11, 1) == expected11

    line12 = [RETURN, Token('var', 'num')]
    expected12 = Node(RETURN, 1, [Token('var', 'num')])
    assert parse_line(line12, 1) == expected12

def test_parse_line_simple_invalid():
    line = [Token('var', 1), CREATE, INT]
    with pytest.raises(SyntaxError):
        parse_line(line, 1)

def test_parse_line_complex_variable_expr():
    line = [Token('var', 'num'),
            ASSIGN,
            LEFT_BRACKET, Token('int', 1), PLUS, Token('var', 'num2'), MULTIPLY, Token('float', 3.5), RIGHT_BRACKET,
            DIVIDE,
            LEFT_BRACKET, Token('int', 3), MODULO, Token('int', 4), RIGHT_BRACKET
            ]

    expected = Node(ASSIGN, 1, Node(
        DIVIDE, 1,
        Node(MODULO, 1, [Token('int', 4)], [Token('int', 3)]),
        Node(PLUS, 1, Node(
            MULTIPLY, 1, [Token('float', 3.5)], [Token('var', 'num2')]
        ), [Token('int', 1)])
    ), [Token('var', 'num')])

    assert parse_line(line, 1) == expected

def test_parse_line_complex_function_expr():
    line = [Token('fnc', 'out'),
            PIPE,
            LEFT_BRACKET, Token('int', 1), MULTIPLY, Token('var', 'num'), RIGHT_BRACKET]

    expected = Node(PIPE, 1, Node(
        MULTIPLY, 1,
        [Token('var', 'num')],
        [Token('int', 1)]
    ), [Token('fnc', 'out')])

    assert parse_line(line, 1) == expected

def test_parse_line_complex_return_expr():
    line = [RETURN,
            LEFT_BRACKET, Token('int', 1), MULTIPLY, Token('var', 'num'), RIGHT_BRACKET,
            MINUS, Token('int', 5)]

    expected = Node(RETURN, 1, Node(
        MINUS, 1,
        [Token('int', 5)],
        Node(
            MULTIPLY, 1,
            [Token('var', 'num')],
            [Token('int', 1)]
        )
    ))

    assert parse_line(line, 1) == expected

# endregion

# TODO test parse_line
# TODO test __has_nesting
# TODO test __nest
# TODO test __operate_separators
# TODO test __parse_calls
# TODO test __parse_helper
# TODO test operate_...
# TODO test parse
# TODO test print_tree
