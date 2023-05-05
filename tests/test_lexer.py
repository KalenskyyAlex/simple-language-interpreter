# pylint: skip-file
import sys
import io
import contextlib

sys.path.insert(0, '../interpreter')

from lexer import __is_keyword, __give_type, __give_types_for_tokens # noqa
from lexer import __in_string, __is_boolean, __is_float, __is_integer # noqa
from lexer import __is_operator, __is_separator, __is_string, __is_type # noqa
from lexer import __clear_lines, get_tokens, print_tokens # noqa
from structures import Token # noqa
import lexer # noqa

# region Testing is_...() methods

def test_is_keyword_wrong():
	assert not __is_keyword('typ')
	assert not __is_keyword('is')

def test_is_keyword_right():
	assert __is_keyword('start')
	assert __is_keyword('end')
	assert __is_keyword('use')
	assert __is_keyword('return')
	assert __is_keyword('break')
	assert __is_keyword('while')
	assert __is_keyword('if')
	assert __is_keyword('else')

def test_is_keyword_none():
	assert not __is_keyword(None)

def test_is_operator_wrong():
	assert not __is_operator('1')
	assert not __is_operator('name')

def test_is_operator_right():
	assert __is_operator('+')
	assert __is_operator('-')
	assert __is_operator('=')
	assert __is_operator('is')
	assert __is_operator('|')
	assert __is_operator('*')
	assert __is_operator('/')
	assert __is_operator('+')

def test_is_operator_none():
	assert not __is_operator(None)

def test_is_type_wrong():
	assert not __is_type('+')
	assert not __is_type('buul') # noqa

def test_is_type_right():
	assert __is_type('bool')
	assert __is_type('int')
	assert __is_type('float')
	assert __is_type('str')

def test_it_type_none():
	assert not __is_type(None)

def test_is_boolean_wrong():
	assert not __is_boolean('wrong')
	assert not __is_boolean('right')

def test_is_boolean_right():
	assert __is_boolean('true')
	assert __is_boolean('false')

def test_is_boolean_none():
	assert not __is_boolean(None)

def test_is_integer_wrong():
	assert not __is_integer('1a')
	assert not __is_integer('1.0')
	assert not __is_integer('-a')
	assert not __is_integer('12 - 34')

def test_is_integer_right():
	assert __is_integer('11')
	assert __is_integer('-2')
	assert __is_integer('1234')
	assert __is_integer('-223')

def test_is_integer_none():
	assert not __is_integer(None)

def test_is_float_wrong():
	assert not __is_float('1,1')
	assert not __is_float('1..1')
	assert not __is_float('-1,1')
	assert not __is_float('1.1a1')
	assert not __is_float('123')

def test_is_float_right():
	assert __is_float('1.1')
	assert __is_float('-1.1')

def test_is_float_none():
	assert not __is_float(None)

def test_is_string_wrong():
	assert not __is_string('"')
	assert not __is_string('\'a"')
	assert not __is_string('"a')
	assert not __is_string('string')

def test_is_string_right():
	assert __is_string('""')
	assert __is_string('"this is string"')
	assert __is_string('"this is also " string"')

def test_is_string_none():
	assert not __is_string(None)

def test_is_separator_wrong():
	assert not __is_separator('.')
	assert not __is_separator(';')
	assert not __is_separator('a')
	assert not __is_separator(',,')

def test_is_separator_right():
	assert __is_separator(',')

def test_is_separator_none():
	assert not __is_separator(None)

# endregion

# region Testing __in_string() methods

def test_in_string_dry_run_none():
	assert not __in_string(None, None)
	assert not __in_string(None, 0)
	assert not __in_string('string', None)

def test_in_string_dry_run_invalid():
	assert not __in_string('short', 100)
	assert not __in_string('string', -20)

def test_in_string_general():
	assert __in_string('out | "Hello"', 7)
	assert not __in_string('out | "Hello"', 6)
	assert not __in_string('out | "Hello"', 12)

def test_in_string_many_strings():
	assert not __in_string('out | "Hello" + "World"', 13)
	assert __in_string('out | "Hello" + "World"', 7)
	assert __in_string('out | "Hello" + "World"', 17)

def test_in_string_quotes_in_string():
	assert __in_string('out | "Hello\\"World\\""', 7)
	assert __in_string('out | "Hello\\"World\\""', 12)
	assert __in_string('out | "Hello\\"World\\""', 13)
	assert __in_string('out | "Hello\\"World\\""', 18)

# endregion

# region Testing __clear_lines() methods

def test_clear_lines_dry_run_none():
	lines, line_numbers = __clear_lines(None)
	assert lines is None
	assert line_numbers is None

def test_clear_lines_dry_run_empty():
	assert __clear_lines([]) == ([], [])

def test_clear_lines_dry_run_invalid():
	assert __clear_lines('string') == (None, None)
	assert __clear_lines(1) == (None, None)
	assert __clear_lines(['string', ['line']]) == (None, None)
	assert __clear_lines([[['string']]]) == (None, None)
	assert __clear_lines([[], ['string']]) == (None, None)
	assert __clear_lines([None, 'string']) == (None, None)
	assert __clear_lines(('string', 'string')) == (None, None)

def test_clear_lines_general():
	given = [
		'use io ',
		'',
		'~this is main function',
		'start main',
		'\tout | "Hello, World!" ~ printing hello world to console',
		'end'
	]

	expected = (
		[
			'use io',
			'start main',
			'out | "Hello, World!"',
			'end'
		],
		[
			1,
			4,
			5,
			6
		]
	)

	assert __clear_lines(given) == expected

def test_clear_lines_many_comments():
	given = [
		'use io ',
		'~ use math -- add later',
		' ~ offset comment',
		'~this is main function',
		'start main ~ the function name is main',
		'\tout | "~ some ~ tricky ~ text ~" ~ testing __clear_lines',
		'end ~ use end keyword to end block'
	]

	expected = (
		[
			'use io',
			'start main',
			'out | "~ some ~ tricky ~ text ~"',
			'end'
		],
		[
			1,
			5,
			6,
			7
		]
	)
	assert __clear_lines(given) == expected

def test_clear_lines_many_tabs():
	given = [
		'\tuse io',
		'\tstart main',
		'\t\t\t\tout | "I love writing code full of tabs"',
		'\t\t\t\tout | "This is tab symbol: \\t"',
		'\t\tend'
	]

	expected = (
		[
			'use io',
			'start main',
			'out | "I love writing code full of tabs"',
			'out | "This is tab symbol: \\t"',
			'end'
		],
		[
			1,
			2,
			3,
			4,
			5
		]
	)

	assert __clear_lines(given) == expected

def test_clear_lines_trailing_whitespace():
	given = [
		'\tuse io       ',
		'\tstart main       ',
		'\t\t\t\tout | "I love  writing code full of tabs"  ',
		'\t\t\t\tout | "This is tab symbol: \\t"            ~ some comment here',
		'\t\tend'
	]

	expected = (
		[
			'use io',
			'start main',
			'out | "I love  writing code full of tabs"',
			'out | "This is tab symbol: \\t"',
			'end'
		],
		[
			1,
			2,
			3,
			4,
			5
		]
	)

	assert __clear_lines(given) == expected

# endregion

# region Testing __give_types_for_tokens()

def test_give_types_for_tokens_dry_run_none():
	assert __give_types_for_tokens(None) is None

def test_give_types_for_tokens_dry_run_invalid():
	assert __give_types_for_tokens([['token'], 'token']) is None
	assert __give_types_for_tokens((['token'], ['token'])) is None
	assert __give_types_for_tokens({}) is None

def test_give_types_for_tokens_dry_run_empty():
	assert __give_types_for_tokens([]) == []
	assert __give_types_for_tokens([[], []]) == []

def test_give_types_for_tokens_general():
	given = [
		['use', 'io'],
		['start', 'main'],
		['out', '|', '"Hello, World!"'],
		['end']
	]

	expected = [
		[Token('kwd', 'use'), Token('lib', 'io')],
		[Token('kwd', 'start'), Token('fnc', 'main')],
		[Token('fnc', 'out'), Token('opr', '|'), Token('str', 'Hello, World!')],
		[Token('kwd', 'end')]
	]

	assert __give_types_for_tokens(given) == expected

def test_give_types_for_tokens_literals():
	given = [
		['1'],
		['1.0'],
		['-1'],
		['-1.0'],
		['true'],
		['false'],
		['""'],
		['"\""'],
		['"string"']
	]

	expected = [
		[Token('int', 1)],
		[Token('float', 1.0)],
		[Token('int', -1)],
		[Token('float', -1.0)],
		[Token('bool', True)],
		[Token('bool', False)],
		[Token('str', '')],
		[Token('str', '"')],
		[Token('str', 'string')]
	]

	assert __give_types_for_tokens(given) == expected

def test_give_types_for_tokens_keywords():
	given = [
		['start'],
		['end'],
		['if'],
		['else'],
		['while'],
		['use'],
		['return'],
		['break'],
	]

	expected = [
		[Token('kwd', 'start')],
		[Token('kwd', 'end')],
		[Token('kwd', 'if')],
		[Token('kwd', 'else')],
		[Token('kwd', 'while')],
		[Token('kwd', 'use')],
		[Token('kwd', 'return')],
		[Token('kwd', 'break')],
	]

	assert __give_types_for_tokens(given) == expected

def test_give_types_for_tokens_operators():
	given = [
		['+'],
		['-'],
		['='],
		['|'],
		['is'],
		['*'],
		['/'],
		['%'],
	]

	expected = [
		[Token('opr', '+')],
		[Token('opr', '-')],
		[Token('opr', '=')],
		[Token('opr', '|')],
		[Token('opr', 'is')],
		[Token('opr', '*')],
		[Token('opr', '/')],
		[Token('opr', '%')],
	]

	assert __give_types_for_tokens(given) == expected

# endregion

# region Testing test __give_type()

def test_give_type_dry_run_none():
	assert __give_type(None, None) is None
	assert __give_type(None, 'string') is None
	assert __give_type('string', None) is None

def test_give_type_dry_run_invalid():
	assert __give_type(1, 'string') is None
	assert __give_type('string', 1) is None

# endregion

# region Testing get_tokens()

def test_get_tokens_dry_run_none():
	try:
		get_tokens(None)
	except FileNotFoundError:
		...
	else:
		assert False

def test_get_tokens_dry_run_invalid():
	try:
		get_tokens('invalid.filename')
	except FileNotFoundError:
		...
	else:
		assert False

	try:
		get_tokens('./test_scripts/test_1.pin')
	except FileNotFoundError:
		...
	else:
		assert False

def test_get_tokens_general_1():
	expected = (
		[
			[Token('kwd', 'use'), Token('lib', 'io')],
			[
				Token('kwd', 'start'), Token('fnc', 'many_tabs'), Token('opr', '|'),
				Token('var', 'tabs'), Token('opr', 'is'), Token('typ', 'int'), Token('sep', ','),
				Token('var', 'spaces'), Token('opr', 'is'), Token('typ', 'float'),
			],
			[
				Token('kwd', 'return'), Token('var', 'tabs'), Token('opr', '+'),
				Token('var', 'spaces')
			],
			[Token('kwd', 'end')],
			[Token('kwd', 'start'), Token('fnc', 'main')],
			[
				Token('fnc', 'out'), Token('opr', '|'), Token('opr', '('), Token('fnc', 'many_tabs'),
				Token('opr', '|'), Token('int', 0), Token('sep', ','), Token('float', 1.0),
				Token('opr', ')')
			],
			[Token('kwd', 'end')]
		],
		[
			1, 3, 4, 5, 6, 7, 8
		]
	)

	assert get_tokens('./test_scripts/test_1.min') == expected

def test_get_tokens_general_2():
	expected = (
		[
			[Token('kwd', 'use'), Token('lib', 'io')],
			[Token('kwd', 'use'), Token('lib', 'math')],
			[Token('kwd', 'start'), Token('fnc', 'main')],
			[Token('fnc', 'out'), Token('opr', '|'), Token('str', 'Hello, world')],
			[Token('fnc', 'out'), Token('opr', '|'), Token('str', 'And tilda(~) can be inside this text')],
			[
				Token('fnc', 'out'), Token('opr', '|'),  Token('opr', '('),
				Token('fnc', 'sqrt'), Token('opr', '|'), Token('int', 9), Token('opr', ')'),
			],
			[Token('kwd', 'end')]
		],
		[
			1, 2, 9, 10, 11, 12, 16
		]
	)

	assert get_tokens('./test_scripts/test_2.min') == expected

def test_get_tokens_general_3():
	expected = (
		[
			[Token('kwd', 'use'), Token('lib', 'io')],
			[
				Token('kwd', 'start'), Token('fnc', 'factorial'), Token('opr', '|'),
				Token('var', 'num'), Token('opr', 'is'), Token('typ', 'int')
			],
			[Token('kwd', 'if'), Token('var', 'num'), Token('opr', '=='), Token('int', 0)],
			[Token('kwd', 'return'), Token('int', 1)],
			[Token('kwd', 'else')],
			[
				Token('kwd', 'return'), Token('var', 'num'), Token('opr', '*'), Token('opr', '('),
				Token('fnc', 'factorial'), Token('opr', '|'), Token('var', 'num'), Token('opr', '-'),
				Token('int', 1), Token('opr', ')')
			],
			[Token('kwd', 'end')],
			[Token('kwd', 'end')],
			[Token('kwd', 'start'), Token('fnc', 'main')],
			[
				Token('fnc', 'out'), Token('opr', '|'), Token('opr', '('),
				Token('fnc', 'factorial'), Token('opr', '|'), Token('int', 5),
				Token('opr', ')')
			],
			[Token('fnc', 'out'), Token('opr', '|'), Token('str', '\n')],
			[Token('kwd', 'end')]
		],
		[
			3, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16
		]
	)

	assert get_tokens('./test_scripts/test_3.min') == expected

# endregion

# region Testing print_tokens

def test_print_tokens_dry_run_none():
	buffer = io.StringIO()

	with contextlib.redirect_stdout(buffer):
		print_tokens(None)

	assert buffer.getvalue() == ''

	buffer.close()

def test_print_tokens_dry_run_invalid():
	try:
		print_tokens('invalid.filename')
	except FileNotFoundError:
		assert True
	else:
		assert False

	try:
		print_tokens('./test_scripts/test_1.pin')
	except FileNotFoundError:
		assert True
	else:
		assert False

def test_print_tokens_general_1():
	expected = \
		'Raw tokens:\n'                                                           \
		'{1: [kwd: use, lib: io],\n'                                              \
		' 3: [kwd: start,\n'                                                      \
		'     fnc: many_tabs,\n'                                                  \
		'     opr: |,\n'                                                          \
		'     var: tabs,\n'                                                       \
		'     opr: is,\n'                                                         \
		'     typ: int,\n'                                                        \
		'     sep: ,,\n'                                                          \
		'     var: spaces,\n'                                                     \
		'     opr: is,\n'                                                         \
		'     typ: float],\n'                                                     \
		' 4: [kwd: return, var: tabs, opr: +, var: spaces],\n'                    \
		' 5: [kwd: end],\n'                                                       \
		' 6: [kwd: start, fnc: main],\n'                                          \
		' 7: [fnc: out,\n'                                                        \
		'     opr: |,\n'                                                          \
		'     opr: (,\n'                                                          \
		'     fnc: many_tabs,\n'                                                  \
		'     opr: |,\n'                                                          \
		'     int: 0,\n'                                                          \
		'     sep: ,,\n'                                                          \
		'     float: 1.0,\n'                                                      \
		'     opr: )],\n'                                                         \
		' 8: [kwd: end]}\n'                                                       \
		'----------------------------------------------------------------------\n'

	buffer = io.StringIO()

	with contextlib.redirect_stdout(buffer):
		print_tokens('./test_scripts/test_1.min')

	assert buffer.getvalue() == expected

	buffer.close()

def test_print_tokens_general_2():
	expected = \
		'Raw tokens:\n'                                                           \
		'{1: [kwd: use, lib: io],\n'                                              \
		' 2: [kwd: use, lib: math],\n'                                            \
		' 9: [kwd: start, fnc: main],\n'                                          \
		' 10: [fnc: out, opr: |, str: Hello, world],\n'                           \
		' 11: [fnc: out, opr: |, str: And tilda(~) can be inside this text],\n'   \
		' 12: [fnc: out, opr: |, opr: (, fnc: sqrt, opr: |, int: 9, opr: )],\n'   \
		' 16: [kwd: end]}\n'                                                      \
		'----------------------------------------------------------------------\n'

	buffer = io.StringIO()

	with contextlib.redirect_stdout(buffer):
		print_tokens('./test_scripts/test_2.min')

	assert buffer.getvalue() == expected

	buffer.close()

def test_print_tokens_general_3():
	expected = \
		'Raw tokens:\n'                                                              \
		'{3: [kwd: use, lib: io],\n'                                                 \
		' 5: [kwd: start, fnc: factorial, opr: |, var: num, opr: is, typ: int],\n'   \
		' 6: [kwd: if, var: num, opr: ==, int: 0],\n'                                \
		' 7: [kwd: return, int: 1],\n'                                               \
		' 8: [kwd: else],\n'                                                         \
		' 9: [kwd: return,\n'                                                        \
		'     var: num,\n'                                                           \
		'     opr: *,\n'                                                             \
		'     opr: (,\n'                                                             \
		'     fnc: factorial,\n'                                                     \
		'     opr: |,\n'                                                             \
		'     var: num,\n'                                                           \
		'     opr: -,\n'                                                             \
		'     int: 1,\n'                                                             \
		'     opr: )],\n'                                                            \
		' 10: [kwd: end],\n'                                                         \
		' 11: [kwd: end],\n'                                                         \
		' 13: [kwd: start, fnc: main],\n'                                            \
		' 14: [fnc: out, opr: |, opr: (, fnc: factorial, opr: |, int: 5, opr: )],\n' \
		' 15: [fnc: out, opr: |, str: \n'                                            \
		'],\n'                                                                       \
		' 16: [kwd: end]}\n'                                                         \
		'----------------------------------------------------------------------\n'

	buffer = io.StringIO()

	with contextlib.redirect_stdout(buffer):
		print_tokens('./test_scripts/test_3.min')

	assert buffer.getvalue() == expected

	buffer.close()

# endregion