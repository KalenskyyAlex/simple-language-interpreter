# pylint: skip-file
import sys

sys.path.insert(0, '../interpreter')

from lexer import * # noqa
from structures import Token # noqa

# region Testing is_...() methods

def test_is_keyword_wrong():
	assert not is_keyword('typ')
	assert not is_keyword('is')

def test_is_keyword_right():
	assert is_keyword('start')
	assert is_keyword('end')
	assert is_keyword('use')
	assert is_keyword('return')
	assert is_keyword('break')
	assert is_keyword('while')
	assert is_keyword('if')
	assert is_keyword('else')

def test_is_keyword_none():
	assert not is_keyword(None)

def test_is_operator_wrong():
	assert not is_operator('1')
	assert not is_operator('name')

def test_is_operator_right():
	assert is_operator('+')
	assert is_operator('-')
	assert is_operator('=')
	assert is_operator('is')
	assert is_operator('|')
	assert is_operator('*')
	assert is_operator('/')
	assert is_operator('+')

def test_is_operator_none():
	assert not is_operator(None)

def test_is_type_wrong():
	assert not is_type('+')
	assert not is_type('buul')

def test_is_type_right():
	assert is_type('bool')
	assert is_type('int')
	assert is_type('float')
	assert is_type('str')

def test_it_type_none():
	assert not is_type(None)

def test_is_boolean_wrong():
	assert not is_boolean('wrong')
	assert not is_boolean('right')

def test_is_boolean_right():
	assert is_boolean('true')
	assert is_boolean('false')

def test_is_boolean_none():
	assert not is_boolean(None)

def test_is_integer_wrong():
	assert not is_integer('1a')
	assert not is_integer('1.0')
	assert not is_integer('-a')
	assert not is_integer('12 - 34')

def test_is_integer_right():
	assert is_integer('11')
	assert is_integer('-2')
	assert is_integer('1234')
	assert is_integer('-223')

def test_is_integer_none():
	assert not is_integer(None)

def test_is_float_wrong():
	assert not is_float('1,1')
	assert not is_float('1..1')
	assert not is_float('-1,1')
	assert not is_float('1.1a1')
	assert not is_float('123')

def test_is_float_right():
	assert is_float('1.1')
	assert is_float('-1.1')

def test_is_float_none():
	assert not is_float(None)

def test_is_string_wrong():
	assert not is_string('"')
	assert not is_string('\'a"')
	assert not is_string('"a')
	assert not is_string('string')

def test_is_string_right():
	assert is_string('""')
	assert is_string('"this is string"')
	assert is_string('"this is also " string"')

def test_is_string_none():
	assert not is_string(None)

def test_is_separator_wrong():
	assert not is_separator('.')
	assert not is_separator(';')
	assert not is_separator('a')
	assert not is_separator(',,')

def test_is_separator_right():
	assert is_separator(',')

def test_is_separator_none():
	assert not is_separator(None)

# endregion

# region Testing in_string() methods

def test_in_string_dry_run_none():
	assert not in_string(None, None)
	assert not in_string(None, 0)
	assert not in_string('string', None)

def test_in_string_dry_run_invalid():
	assert not in_string('short', 100)
	assert not in_string('string', -20)

def test_in_string_general():
	assert in_string('out | "Hello"', 7)
	assert not in_string('out | "Hello"', 6)
	assert not in_string('out | "Hello"', 12)

def test_in_string_many_strings():
	assert not in_string('out | "Hello" + "World"', 13)
	assert in_string('out | "Hello" + "World"', 7)
	assert in_string('out | "Hello" + "World"', 17)

def test_in_string_quotes_in_string():
	assert in_string('out | "Hello\\"World\\""', 7)
	assert in_string('out | "Hello\\"World\\""', 12)
	assert in_string('out | "Hello\\"World\\""', 13)
	assert in_string('out | "Hello\\"World\\""', 18)

# endregion

# region Testing clear_lines() methods

def test_clear_lines_dry_run_none():
	lines, line_numbers = clear_lines(None)
	assert lines is None
	assert line_numbers is None

def test_clear_lines_dry_run_empty():
	assert clear_lines([]) == ([], [])

def test_clear_lines_dry_run_invalid():
	assert clear_lines('string') == (None, None)
	assert clear_lines(1) == (None, None)
	assert clear_lines(['string', ['line']]) == (None, None)
	assert clear_lines([[['string']]]) == (None, None)
	assert clear_lines([[], ['string']]) == (None, None)
	assert clear_lines([None, 'string']) == (None, None)
	assert clear_lines(('string', 'string')) == (None, None)

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

	assert clear_lines(given) == expected

def test_clear_lines_many_comments():
	given = [
		'use io ',
		'~ use math -- add later',
		' ~ offset comment',
		'~this is main function',
		'start main ~ the function name is main',
		'\tout | "~ some ~ tricky ~ text ~" ~ testing clear_lines',
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
	assert clear_lines(given) == expected

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

	assert clear_lines(given) == expected

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

	assert clear_lines(given) == expected


# endregion

# region Testing give_types_for_tokens()

def test_give_types_for_tokens_dry_run_none():
	assert give_types_for_tokens(None) is None

def test_give_types_for_tokens_dry_run_invalid():
	assert give_types_for_tokens([['token'], 'token']) is None
	assert give_types_for_tokens((['token'], ['token'])) is None
	assert give_types_for_tokens({}) is None

def test_give_types_for_tokens_dry_run_empty():
	assert give_types_for_tokens([]) == []
	assert give_types_for_tokens([[], []]) == []

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

	assert give_types_for_tokens(given) == expected

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

	assert give_types_for_tokens(given) == expected

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

	assert give_types_for_tokens(given) == expected

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

	assert give_types_for_tokens(given) == expected

# endregion
