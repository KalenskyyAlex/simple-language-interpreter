# pylint: skip-file
import sys
import os

sys.path.insert(0, '../interpreter')

from lexer import * # noqa

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


