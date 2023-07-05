# pylint: skip-file
import pytest

from interpreter.utils.structures import Block
from interpreter.utils.commons import *

# region Testing Token class

def test_token_init_valid():
    token = Token('int', 1.0)

    assert token.type == 'int'
    assert token.value == 1

def test_token_init_invalid():
    with pytest.raises(TypeError):
        Token('invalid type', True)

    with pytest.raises(TypeError):
        Token('int', None)

    with pytest.raises(TypeError):
        Token(None, 1)

def test_token_str():
    assert Token('int', 1).__repr__() == 'int: 1'
    assert Token('kwd', 'start').__repr__() == 'kwd: start'
    assert Token('str', 'Hello!').__repr__() == 'str: Hello!'
    assert Token('opr', '+').__repr__() == 'opr: +'

def test_token_eq_comparing_non_tokens():
    assert Token('int', 1) != 1

def test_token_eq():
    token1 = Token('int', 1)
    token2 = Token('int', 2)

    assert not token1 == token2

    token1 = Token('str', 'start')
    token2 = Token('kwd', 'start')

    assert not token1 == token2

    token1 = Token('opr', '+')
    token2 = Token('opr', '+')

    assert token1 == token2

# endregion

# region Testing Node class

def test_node_init_valid():
    node1 = Node(PIPE, 10, Token('int', 3), Token('fnc', 'out'))

    assert node1.left == Token('fnc', 'out')
    assert node1.right == Token('int', 3)
    assert node1.operator == PIPE
    assert node1.line_number == 10

    node2 = Node(PIPE, 11, node1, Token('fnc', 'main'))

    assert node2.left == Token('fnc', 'main')
    assert node2.right == node1
    assert node2.operator == PIPE
    assert node2.line_number == 11

def test_node_init_invalid():
    with pytest.raises(TypeError):
        Node(Node(PIPE, 10), 10, Token('int', 3), Token('fnc', 'out'))

    with pytest.raises(TypeError):
        Node(None, 10, Token('int', 3), Token('fnc', 'out'))

    with pytest.raises(TypeError):
        Node(PIPE, 0, Token('int', 3), Token('fnc', 'out'))

    with pytest.raises(TypeError):
        Node(PIPE, None, Token('int', 3), Token('fnc', 'out'))

    with pytest.raises(TypeError):
        Node(PIPE, 1.1, Token('int', 3), Token('fnc', 'out'))

def test_node_str():
    assert Node(PIPE, 1, RETURN, START).__repr__() == str({
        'line': 1,
        'left': START,
        'operator': PIPE.value,
        'right': RETURN
    })

def test_node_eq_comparing_non_nodes():
    assert Node(PIPE, 1, RETURN, START) != RETURN

def test_node_eq():
    node1 = Node(PIPE, 1, RETURN, START)
    node2 = Node(PIPE, 1, START, RETURN)

    assert not node1 == node2

    node1 = Node(PIPE, 1, START, RETURN)
    node2 = Node(PIPE, 2, START, RETURN)

    assert not node1 == node2

    node1 = Node(PIPE, 1, START, RETURN)
    node2 = Node(PLUS, 1, START, RETURN)

    assert not node1 == node2

    node1 = Node(PIPE, 1, START, RETURN)
    node2 = Node(PIPE, 1, START, RETURN)

    assert node1 == node2


# endregion

# region Testing Function class

def test_function_init_valid():
    args = [
        Node(CREATE, 10, INT, Token('var', 'var1')),
        Node(CREATE, 10, FLOAT, Token('var', 'var2'))
    ]

    body = [
        Node(PIPE, 11, Token('fnc', 'out'), Node(PLUS, 11, Token('var', 'var1'), Token('var', 'var1'))),
        Node(RETURN, 12, Token('var', 'var1'))
    ]

    function = Function('print_sum', args, body, 10)

    assert function.name == 'print_sum'
    assert function.args == args
    assert function.body == body
    assert function.line_number == 10

def test_function_init_invalid():
    args = [
        Node(CREATE, 10, INT, Token('var', 'var1')),
        Node(CREATE, 10, FLOAT, Token('var', 'var2'))
    ]

    body = [
        Node(PIPE, 11, Token('fnc', 'out'), Node(PLUS, 11, Token('var', 'var1'), Token('var', 'var1'))),
        Node(RETURN, 12, Token('var', 'var1'))
    ]

    with pytest.raises(TypeError):
        Function(None, args, body, 10)

    with pytest.raises(TypeError):
        Function(' ', args, body, 10)

    with pytest.raises(TypeError):
        Function('name', args, body, None)

    with pytest.raises(TypeError):
        Function('name', args, body, -1)

    with pytest.raises(TypeError):
        Function('name', args, body, 1.1)

    with pytest.raises(TypeError):
        Function('name', None, body, 10)

    with pytest.raises(TypeError):
        Function('name', args, None, 10)

def test_function_eq_comparing_non_functions():
    assert Function('name', [], [], 1) != RETURN

def test_function_eq():
    func1 = Function('write', [], [], 1)
    func2 = Function('write', [], [], 1)

    assert func1 == func2

    func1 = Function('write', [], [], 1)
    func2 = Function('write', [], [], 2)

    assert func1 != func2

    func1 = Function('write', [], [], 1)
    func2 = Function('bride', [], [], 1)

    assert func1 != func2

    func1 = Function('write', [], [Node(RETURN, 2)], 1)
    func2 = Function('write', [Node(RETURN, 2)], [], 2)

    assert func1 != func2

def test_function_str():
    assert Function('function', [], [], 10).__repr__() == str({
        'name': 'function',
        'args': [],
        'body': [],
        'line': 10
    })

# endregion

# region Testing Block class

def test_block_init_valid():
    next_block = Block(ELSE, None, [Node(PIPE, 13, Token('fnc', 'out'), Token('str', 'Yeah'))], 12, None)
    block = Block(IF, Node(EQUALS, 10, Token('int', 1), Token('int', 2)),
                  [Node(PIPE, 11, Token('fnc', 'out'), Token('str', 'Why?'))], 10, next_block)

    assert next_block.line_number == 12
    assert next_block.body == [Node(PIPE, 13, Token('fnc', 'out'), Token('str', 'Yeah'))]
    assert next_block.operator == ELSE
    assert next_block.next_block is None
    assert next_block.condition is None

    assert block.line_number == 10
    assert block.operator == IF
    assert block.condition == Node(EQUALS, 10, Token('int', 1), Token('int', 2))
    assert block.next_block == next_block
    assert block.body == [Node(PIPE, 11, Token('fnc', 'out'), Token('str', 'Why?'))]

def test_block_init_invalid():
    with pytest.raises(TypeError):
        Block(None, None, [], 10, None)

    with pytest.raises(TypeError):
        Block(IF, RETURN, [], 10, None)

    with pytest.raises(TypeError):
        Block(1, None, [], 10, None)

    with pytest.raises(TypeError):
        Block(IF, None, None, 10, None)

    with pytest.raises(TypeError):
        Block(IF, None, {}, 10, None)

    with pytest.raises(TypeError):
        Block(IF, None, [], -1, None)

    with pytest.raises(TypeError):
        Block(IF, None, [], None, None)

    with pytest.raises(TypeError):
        Block(IF, None, [], 1.1, None)

def test_block_str():
    next_block = Block(ELSE, None, [Node(PIPE, 13, Token('fnc', 'out'), Token('str', 'Yeah'))], 12, None)
    block = Block(IF, Node(EQUALS, 10, Token('int', 1), Token('int', 2)),
                  [Node(PIPE, 11, Token('fnc', 'out'), Token('str', 'Why?'))], 10, next_block)

    assert block.__repr__() == str({
        'operator': IF.value,
        'condition': Node(EQUALS, 10, Token('int', 1), Token('int', 2)),
        'body': [Node(PIPE, 11, Token('fnc', 'out'), Token('str', 'Why?'))],
        'next': next_block,
        'line': 10
    })

def test_block_eq_comparing_non_blocks():
    block = Block(ELSE, None, [Node(PIPE, 13, Token('fnc', 'out'), Token('str', 'Yeah'))], 12, None)
    assert block != ELSE

# endregion
