"""
This module processes raw text given in .min file,
and divide it on tokens, with recognized types

Run '$python lexer.py' to only create tokens from raw
text in .min file or use as module 'from lexer import get_tokens'
"""

# region Imported modules

from pprint import pprint
from typing import TextIO

from structures import Token
from commons import INNER_TYPES, KEYWORDS, SPECIAL_SYMBOLS, OPERATORS, NUMERALS, BOOLEANS
from commons import TokenList

# endregion

# region Private functions

def give_types_for_tokens(tokens_raw: list[list[str]]) -> list[TokenList]:
    """
    gives each given token a type
    :param tokens_raw: nested array of tokens without type;
    :return: array of tokens with added types
    """
    if tokens_raw is None:
        return None

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
            typed_token: Token
            if is_keyword(token):
                typed_token = Token('kwd', token)
            elif is_operator(token):
                if token == '|':
                    if line_with_types:
                        old_value = line_with_types[-1].value
                        line_with_types[-1] = Token('fnc', old_value)

                typed_token = Token('opr', token)
            elif is_separator(token):
                typed_token = Token('sep', token)
            elif is_type(token):
                typed_token = Token('typ', token)
            elif is_boolean(token):
                typed_token = Token('bool', True if token == 'true' else False)
            elif is_integer(token):
                typed_token = Token('int', int(token))
            elif is_float(token):
                typed_token = Token('float', float(token))
            elif is_string(token):
                typed_token = Token('str', token[1:-1])
            else:
                match prev_token:
                    case 'start':
                        typed_token = Token('fnc', token)
                    case 'use':
                        typed_token = Token('lib', token)
                    case _:
                        typed_token = Token('var', token)

            line_with_types.append(typed_token)
            prev_token = token

        if line_with_types:
            tokens.append(line_with_types)

    return tokens


def in_string(line: str, index_needed: int) -> bool:
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

def clear_lines(lines_raw: list[str]) -> tuple[list[str], list[int]]:
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
            if not in_string(line, symbol_index) and symbol == '~':
                line = line[:symbol_index]
                break
        line = line.strip()

        if line == '':
            continue

        line_numbers.append(index + 1)  # line count starts from 1
        lines.append(line)

    return lines, line_numbers


def is_keyword(token: str) -> bool:
    """
    :param token: token as string
    :return: True if token is a keyword, otherwise False
    """
    return token in KEYWORDS


def is_operator(token: str) -> bool:
    """
    :param token: token as string
    :return: True if token is an operator, otherwise False
    """
    return token in OPERATORS


def is_type(token: str) -> bool:
    """
    :param token: token as string
    :return: True if token is a type, otherwise False
    """
    return token in INNER_TYPES


def is_boolean(token: str) -> bool:
    """
    :param token: token as string
    :return: True if token is a boolean, otherwise False
    """
    return token in BOOLEANS


def is_integer(token: str) -> bool:
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


def is_float(token: str) -> bool:
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

    return is_integer(parts[0]) and is_integer(parts[1])


def is_string(token: str) -> bool:
    """
    :param token: token as string
    :return: True if token is a string, otherwise False
    """
    if token is None:
        return False

    return token[0] == '"' and token[-1] == '"' and len(token) > 1


def is_separator(token: str) -> bool:
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
    file: TextIO = open(file_name, 'r')

    raw_lines: list[str] = file.readlines()
    lines, line_numbers = clear_lines(raw_lines)

    tokens_raw: list[list[str]] = []  # separated, but no types

    for line in lines:
        line_of_tokens: list[str] = []

        length: int = len(line)
        token: str = ''

        in_string: bool = False
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

            # when we hit " it's time to count all text as string till we hit other ",
            # however it MUSTN'T be an " in the text
            if line[index] == '"' and not line[index - 1] == '\\':
                in_string = not in_string
                # don't 'continue', because we need " to recognize token as string

            # when we are in string we don't care about any operators, spaces, but care about '\'
            if in_string and line[index] == '\\':
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
            # till here

            # when we're not in string things are easier
            if line[index] in SPECIAL_SYMBOLS and not in_string:
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

        # extra cautiousness
        if line_of_tokens:
            tokens_raw.append(line_of_tokens)

    tokens: list[TokenList] = give_types_for_tokens(tokens_raw)  # differentiate tokens

    return tokens, line_numbers


def print_tokens(file_name: str) -> None:
    """
    Used for outputting processed tokens from .min file
    :param file_name: path to the file to be checked
    """
    print('Raw tokens:')

    tokens, line_numbers = get_tokens(file_name)
    combined = zip(line_numbers, tokens)
    pprint(dict(combined))

    print('-' * 70)

# endregion


if __name__ == '__main__':
    filename = input('Enter path to .min file you want to convert to tokens of: ')
    print_tokens(filename)
