# pylint: skip-file
import sys

sys.path.insert(0, '../interpreter')

from structures import *  # noqa
from commons import *  # noqa

# region Testing Token class

def test_token_init_valid():
	token = Token('int', 1.0)

	assert token.type == 'int'
	assert token.value == 1


def test_token_init_invalid():
	try:
		token = Token('invalid type', True)
	except TypeError:
		...
	else:
		assert False

	try:
		token = Token('int', None)
	except TypeError:
		...
	else:
		assert False

	try:
		token = Token(None, 1)
	except TypeError:
		...
	else:
		assert False


def test_token_str():
	assert str(Token('int', 1)) == 'int: 1'
	assert str(Token('kwd', 'start')) == 'kwd: start'
	assert str(Token('str', 'Hello!')) == 'str: Hello!'
	assert str(Token('opr', '+')) == 'opr: +'


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
	try:
		node = Node(Node(PIPE, 10), 10, Token('int', 3), Token('fnc', 'out'))
	except TypeError:
		...
	else:
		assert False

	try:
		node = Node(None, 10, Token('int', 3), Token('fnc', 'out'))
	except TypeError:
		...
	else:
		assert False

	try:
		node = Node(PIPE, 0, Token('int', 3), Token('fnc', 'out'))
	except TypeError:
		...
	else:
		assert False

	try:
		node = Node(PIPE, None, Token('int', 3), Token('fnc', 'out'))
	except TypeError:
		...
	else:
		assert False

	try:
		node = Node(PIPE, 1.1, Token('int', 3), Token('fnc', 'out'))
	except TypeError:
		...
	else:
		assert False


def test_node_str():
	assert str(Node(PIPE, 1, RETURN, START)) == str({
		'line': 1,
		'left': START,
		'operator': PIPE.value,
		'right': RETURN
	})


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
		Node(PIPE, 11, Token('fnc', 'out'),
			Node(PLUS, 11, Token('var', 'var1'), Token('var', 'var1'))
		),
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
		Node(PIPE, 11, Token('fnc', 'out'),
		     Node(PLUS, 11, Token('var', 'var1'), Token('var', 'var1'))
		     ),
		Node(RETURN, 12, Token('var', 'var1'))
	]

	try:
		function = Function(None, args, body, 10)
	except TypeError:
		...
	else:
		assert False

	try:
		function = Function('name', args, body, -1)
	except TypeError:
		...
	else:
		assert False

	try:
		function = Function('name', args, body, 1.1)
	except TypeError:
		...
	else:
		assert False

	try:
		function = Function('name', None, body, 10)
	except TypeError:
		...
	else:
		assert False

	try:
		function = Function('name', args, None, 10)
	except TypeError:
		...
	else:
		assert False

# endregion

# TODO test block
