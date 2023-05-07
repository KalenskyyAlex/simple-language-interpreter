"""
This module processes raw text given in .min file,
and divide it on tokens, with recognized types

Run '$python lexer.py' to only create tokens from raw
text in .min file or use as module 'from lexer import get_tokens'
"""

# region Imported modules

from pprint import pprint
from typing import TextIO

from structures import Token, Token
from commons import INNER_TYPES, KEYWORDS, SPECIAL_SYMBOLS, OPERATORS, NUMERALS, BOOLEANS
from commons import PIPE
from commons import TokenList

# endregion

# region Private functions

def __give_type(token: str, prev_token: str) -> Token:
    """
    for given token return token with evaluated type (sometimes depends on previous token)

    :param token: token to give it a type
    :param prev_token: previous token
    :return: typed token
    """
    if not isinstance(token, str) or not isinstance(prev_token, str):
        return None

    if __is_keyword(token):
        typed_token = Token('kwd', token)
    elif __is_operator(token):
        typed_token = Token('opr', token)
    elif __is_separator(token):
        typed_token = Token('sep', token)
    elif __is_type(token):
        typed_token = Token('typ', token)
    elif __is_boolean(token):
        typed_token = Token('bool', token == 'true')
    elif __is_integer(token):
        typed_token = Token('int', int(token))
    elif __is_float(token):
        typed_token = Token('float', float(token))
    elif __is_string(token):
        typed_token = Token('str', token[1:-1])
    else:
        match prev_token:
            case 'start':
                typed_token = Token('fnc', token)
            case 'use':
                typed_token = Token('lib', token)
            case _:
                typed_token = Token('var', token)

    return typed_token

def __give_types_for_tokens(tokens_raw: list[list[str]]) -> list[TokenList]:
    """
    gives each given token a type
    :param tokens_raw: nested array of tokens without type;
    :return: array of tokens with added types
    """
    if not isinstance(tokens_raw, list):
        return None

    for line in tokens_raw:
        if not isinstance(line, list):
            return None

    prev_token: str = ''

    tokens: list[TokenList] = []

    for line in tokens_raw:
        line_with_types: list = []

        for token in line:
            typed_token: Token = __give_type(token, prev_token)

            if typed_token == PIPE and line_with_types:
                old_value = line_with_types[-1].value
                line_with_types[-1] = Token('fnc', old_value)

            line_with_types.append(typed_token)
            prev_token = token

        if line_with_types:
            tokens.append(line_with_types)

    return tokens


def __in_string(line: str, index_needed: int) -> bool:
    """
    :param line: line to check in
    :param index_needed: check symbol at index_needed
    :return: True if symbol in index_needed is inside string, otherwise False
    """
    if line is None or index_needed is None:
        return False

    previous: str = ''

    in_string_flag: bool = False
    symbols_count = len(line)
    for index in range(symbols_count):
        current = line[index]

        if current == '"' and previous != '\\':
            in_string_flag = not in_string_flag
            continue

        if index == index_needed:
            return in_string_flag

        previous = current

    return False

def __clear_lines(lines_raw: list[str]) -> tuple[list[str], list[int]]:
    """
    deletes whitespace, eol, comments
    :param lines_raw: unprocessed lines of text from .min file
    :return: array of 'cleared' lines with parallel array of line numbers for each line
    """
    if not isinstance(lines_raw, list):
        return None, None

    for line in lines_raw:
        if not isinstance(line, str):
            return None, None

    lines: list[str] = []
    line_numbers: list[int] = []

    # removing comments, tabs, eol symbols
    lines_count = len(lines_raw)
    for index in range(lines_count):
        line = lines_raw[index]

        symbols_count = len(line)
        for symbol_index in range(symbols_count):
            symbol = line[symbol_index]
            if not __in_string(line, symbol_index) and symbol == '~':
                line = line[:symbol_index]
                break
        line = line.strip()

        if line == '':
            continue

        line_numbers.append(index + 1)  # line count starts from 1
        lines.append(line)

    return lines, line_numbers


def __is_keyword(token: str) -> bool:
    """
    :param token: token as string
    :return: True if token is a keyword, otherwise False
    """
    return token in KEYWORDS


def __is_operator(token: str) -> bool:
    """
    :param token: token as string
    :return: True if token is an operator, otherwise False
    """
    return token in OPERATORS


def __is_type(token: str) -> bool:
    """
    :param token: token as string
    :return: True if token is a type, otherwise False
    """
    return token in INNER_TYPES


def __is_boolean(token: str) -> bool:
    """
    :param token: token as string
    :return: True if token is a boolean, otherwise False
    """
    return token in BOOLEANS


def __is_integer(token: str) -> bool:
    """
    :param token: token as string
    :return: True if token is a integer, otherwise False
    """
    if token is None:
        return False

    if token[0] == '-':
        token = token[1:]

    for numeral in token:
        if numeral not in NUMERALS:
            return False

    return True


def __is_float(token: str) -> bool:
    """
    :param token: token as string
    :return: True if token is a float, otherwise False
    """
    if token is None:
        return False

    parts: list[str] = token.split('.')

    # if string has NO point '.', it isn't a floating point number
    if len(parts) != 2:
        return False

    return __is_integer(parts[0]) and __is_integer(parts[1])


def __is_string(token: str) -> bool:
    """
    :param token: token as string
    :return: True if token is a string, otherwise False
    """
    if token is None:
        return False

    return token[0] == '"' and token[-1] == '"' and len(token) > 1


def __is_separator(token: str) -> bool:
    """
    :param token: token as string
    :return: True if token is a separator, otherwise False
    """
    return token == ','

# endregion

# region Public functions

def get_tokens(file_name: str) -> tuple[list[TokenList], list[int]]:
    """
    separate lines into tokens, with types
    :param file_name: path to .min file to be processed
    :return: nested array of tokens and line numbers to each line
    """
    try:
        file: TextIO = open(file_name, 'r')
    except (FileNotFoundError, TypeError) as file_e:
        raise FileNotFoundError('FILE NOT FOUND, MAKE SURE YOUR ' +
                                'PATH TO FILE IS CORRECT') from file_e

    raw_lines: list[str] = file.readlines()
    lines, line_numbers = __clear_lines(raw_lines)

    tokens_raw: list[list[str]] = []  # separated, but no types

    for line in lines:
        line_of_tokens: list[str] = []

        length: int = len(line)
        token: str = ''

        skip_next: bool = False

        for index in range(length):
            # next 3 if's cares about special symbols (\', \\, \", \n)
            # and how to add them, properly, cause in string it doesn't
            # recognize '\ + symbol' as special symbol, but as '\\ + \ +
            # symbol'

            # we added special symbol in the previous iteration, so we must skip it
            if skip_next:
                skip_next = False
                continue

            # when we are in string we don't care about any operators, spaces, but care about '\'
            if __in_string(line, index) and line[index] == '\\' and index + 1 < length:
                match line[index + 1]:
                    case 'n':
                        token += '\n'
                    case '\'':
                        token += '\''
                    case '\"':
                        token += '\"'
                    case '\\':
                        token += '\\'

                skip_next = True
                continue  # we've already added token

            # when we're not in string things are easier
            if line[index] in SPECIAL_SYMBOLS and not __in_string(line, index):
                # several special symbols in raw creates '' tokens
                if token != '':
                    line_of_tokens.append(token)

                token = ''
                if line[index] != ' ':
                    # we count operators as tokens as well, except spaces
                    line_of_tokens.append(line[index])

                    # for 2-symbol operators, like '++', '--', '>=', '<=' or '=='
                    if index + 1 < length and line[index + 1] == '=' \
                            and line[index] in ['>', '<', '=']:
                        line_of_tokens[-1] += '='
                        skip_next = True

            else:
                token += line[index]

        # using previous method we don't add last token, so we add it manually
        if token != '':
            line_of_tokens.append(token)

        if line_of_tokens:
            tokens_raw.append(line_of_tokens)

    tokens: list[TokenList] = __give_types_for_tokens(tokens_raw)  # differentiate tokens

    return tokens, line_numbers


def print_tokens(file_name: str) -> None:
    """
    Used for outputting processed tokens from .min file
    :param file_name: path to the file to be checked
    """
    if not isinstance(file_name, str):
        return

    tokens, line_numbers = get_tokens(file_name)
    combined = zip(line_numbers, tokens)

    print('Raw tokens:')
    pprint(dict(combined))

    print('-' * 70)

# endregion


if __name__ == '__main__':
    filename = input('Enter path to .min file you want to convert to tokens of: ')
    print_tokens(filename)
