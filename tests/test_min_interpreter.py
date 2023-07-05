# pylint: skip-file
import pytest

from interpreter.min_interpreter import execute_line
from interpreter.utils.commons import END, PLUS, MINUS, MULTIPLY, DIVIDE, MODULO, ASSIGN, CREATE, BOOL, INT
from interpreter.utils.structures import Node, Token


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
    ...


def test_execute_line_complex_return_expr():
    ...
