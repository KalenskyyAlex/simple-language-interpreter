# pylint: skip-file
import sys
import os

sys.path.insert(0, os.path.abspath(__file__)[:-19] + '/interpreter')

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


