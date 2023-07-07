# pylint: skip-file
import pytest

from interpreter.min_interpreter import execute_line, execute
from interpreter.utils.commons import END, PLUS, MINUS, MULTIPLY, COMMA, EQUALS, NOT_EQUALS, MORE_THAN, LESS_THAN, \
    NO_MORE_THAN, NO_LESS_THAN
from interpreter.utils.commons import DIVIDE, MODULO, ASSIGN, CREATE
from interpreter.utils.commons import BOOL, INT, RETURN, PIPE
from interpreter.utils.structures import Node, Token, Function


def test_execute_line_dry_run():
    with pytest.raises(ValueError):
        execute_line(END, None, 0, 1, {})
    with pytest.raises(ValueError):
        execute_line(END, {}, None, 1, {})
    with pytest.raises(ValueError):
        execute_line(END, {}, 0, None, {})
    with pytest.raises(ValueError):
        execute_line(END, {}, 0, 1, None)
    with pytest.raises(ValueError):
        execute_line(None, {}, 0, 1, {})


def test_execute_line_simple_arithmetical_inputs():
    expected1 = Token('float', 3.5)
    line1 = Node(PLUS, 1, Token('int', 1), Token('float', 2.5))
    result1, _ = execute_line(line1, {}, 0, 1, {})
    assert result1 == expected1

    expected2 = Token('float', -1.5)
    line2 = Node(MINUS, 1, Token('float', 2.5), Token('int', 1))
    result2, _ = execute_line(line2, {}, 0, 1, {})
    assert result2 == expected2

    expected3 = Token('float', 6.25)
    line3 = Node(MULTIPLY, 1, Token('float', 2.5), Token('float', 2.5))
    result3, _ = execute_line(line3, {}, 0, 1, {})
    assert result3 == expected3

    expected4 = Token('float', 3.5)
    line4 = Node(DIVIDE, 1, Token('int', 2), Token('int', 7))
    result4, _ = execute_line(line4, {}, 0, 1, {})
    assert result4 == expected4

    expected5 = Token('float', 1.5)
    line5 = Node(MODULO, 1, Token('int', 2), Token('float', 7.5))
    result5, _ = execute_line(line5, {}, 0, 1, {})
    assert result5 == expected5


def test_execute_line_simple_logical_expr():
    expected1 = Token('bool', True)
    line1 = Node(EQUALS, 1, Token('int', 2), Token('float', 2.0))
    result1, _ = execute_line(line1, {}, 0, 1, {})
    assert result1 == expected1

    expected2 = Token('bool', False)
    line2 = Node(NOT_EQUALS, 1, Token('int', 3), Token('int', 3))
    result2, _ = execute_line(line2, {}, 0, 1, {})
    assert result2 == expected2

    expected3 = Token('bool', True)
    line3 = Node(MORE_THAN, 1, Token('int', -1), Token('int', 2))
    result3, _ = execute_line(line3, {}, 0, 1, {})
    assert result3 == expected3

    expected4 = Token('bool', False)
    line4 = Node(LESS_THAN, 1, Token('int', -1), Token('int', 2))
    result4, _ = execute_line(line4, {}, 0, 1, {})
    assert result4 == expected4

    expected5 = Token('bool', True)
    line5 = Node(NO_MORE_THAN, 1, Token('int', 3), Token('int', 2))
    result5, _ = execute_line(line5, {}, 0, 1, {})
    assert result5 == expected5

    expected6 = Token('bool', True)
    line6 = Node(NO_LESS_THAN, 1, Token('int', 3), Token('int', 2))
    result6, _ = execute_line(line6, {}, 0, 1, {})
    assert result5 == expected6


def test_execute_line_simple_invalid():
    with pytest.raises(ValueError):
        execute_line(END, {}, -1, 1, {})

    with pytest.raises(ValueError):
        execute_line(END, {}, 0, 0, {})


def test_execute_line_complex_variable_expr():
    visible_variables = {
        0: {'var1': Token('int', 4)},
    }

    expected1 = Token('int', 16)
    line1 = Node(MULTIPLY, 1, Token('int', 4), Token('var', 'var1'))
    result1, _ = execute_line(line1, {}, 0, 1, visible_variables)
    assert result1 == expected1

    expected2 = None
    line2 = Node(ASSIGN, 1, Token('int', 2), Token('var', 'var1'))
    result2, _ = execute_line(line2, {}, 0, 1, visible_variables)
    assert result2 == expected2
    assert visible_variables == {0: {'var1': Token('int', 2)}}

    expected3 = None
    line3 = Node(CREATE, 1, BOOL, Token('var', 'var2'))
    result3, _ = execute_line(line3, {}, 0, 1, visible_variables)
    assert result3 == expected3
    assert visible_variables == {
        0: {'var1': Token('int', 2), 'var2': Token('bool', False)}
    }

    expected4 = None
    line4 = Node(CREATE, 1, INT, Token('var', 'var3'))
    result4, _ = execute_line(line4, {}, 1, 1, visible_variables)
    assert result4 == expected4
    assert visible_variables == {
        0: {'var1': Token('int', 2), 'var2': Token('bool', False)},
        1: {'var3': Token('int', 0)}
    }


def test_execute_line_complex_function_expr():
    function = Function('add', [
            Node(CREATE, 1, INT, Token('var', 'a')),
            Node(CREATE, 1, INT, Token('var', 'b'))
        ],
        [
            Node(RETURN, 1, Node(PLUS, 1, Token('var', 'a'), Token('var', 'b')))
        ],
        1
    )

    callables = {
        'add': function
    }

    expected1 = Token('int', 10)
    line1 = Node(PIPE, 1, Node(COMMA, 1, Token('int', 4), Token('int', 6)), Token('fnc', 'add'))
    result1, _ = execute_line(line1, callables, 0, 1, {})
    assert expected1 == result1


def test_execute_general_1():
    execute('./tests/test_scripts/test_1.min')  # TODO


def test_execute_general_2():
    execute('./tests/test_scripts/test_2.min')  # TODO
    assert False


def test_execute_general_3():
    execute('./tests/test_scripts/test_3.min')  # TODO

def test_execute_general_4():
    execute('./tests/test_scripts/test_4.min')  # TODO
