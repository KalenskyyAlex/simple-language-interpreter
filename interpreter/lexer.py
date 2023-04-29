"""
This module processes raw text given in .min file,
and divide it on tokens, with recognized types
Run as '$python lexer.py' to only create tokens from raw text
or use as module
"""

from pprint import pprint
from typing import TextIO

def clear_lines(lines_raw: list[str]) -> tuple[list[str], list[int]]:
    """
    deletes whitespace, eol, comments
    :param lines_raw: unprocessed lines of text from .min file
    :return: array of 'cleared' lines with parallel array of line numbers for each line
    """
    lines: list[str] = []
    line_numbers: list[int] = []

    # removing comments, tabs, eol symbols
    lines_count = len(lines_raw)
    for index in range(lines_count):
        line = lines_raw[index]

        line = line.split('~')[0]

        if line == '':
            continue

        if line[-1] == '\n':
            line = line[:-1]

        if line == '':
            continue

        line = line.replace('\t', '')

        if line == '':
            continue

        line_numbers.append(index + 1)  # line count starts from 1
        lines.append(line)

    return lines, line_numbers


def get_tokens(file_name: str) -> tuple[list[list[str]], list[int]]:
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
            # next 3 if's cares about special symbols (\', \\, \", \n) and how to add them, properly, cause
            # in string it doesn't recognize '\ + symbol' as special symbol, but as '\\ + \ + symbol'

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
                if line[index + 1] == 'n':
                    token += '\n'
                elif line[index + 1] == '\'':
                    token += '\''
                elif line[index + 1] == '\"':
                    token += '\"'
                elif line[index + 1] == '\\':
                    token += '\\'

                skip_next = True
                continue  # we've already added token
            # till here

            # when we're not in string things are easier
            if line[index] in special_symbols and not in_string:
                # several special symbols in raw creates '' tokens
                if token != '':
                    line_of_tokens.append(token)

                token = ''
                if line[index] != ' ':
                    line_of_tokens.append(line[index])  # we count operators as tokens as well, except spaces

                    # for 2-symbol operators, like '++', '--', '>=', '<=' or '=='
                    if index + 1 < length:
                        if line[index + 1] == '+' and line[index] == '+':
                            line_of_tokens[-1] += '+'
                            skip_next = True
                        elif line[index + 1] == '-' and line[index] == '-':
                            line_of_tokens[-1] += '-'
                            skip_next = True
                        elif line[index + 1] == '=':
                            if line[index] in ['>', '<', '=']:
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

    tokens: list[list[str]] = give_types_for_tokens(tokens_raw)  # differentiate tokens

    return tokens, line_numbers


# when we 'hit' them, we add tokens
special_symbols = ['=', '|', ' ', '+', '-', '/', '*', '%', '(', ')', '>', '<', ',']


def give_types_for_tokens(tokens_raw: list[list[str]]):
    """
    gives each given token a type
    :param tokens_raw: nested array of tokens without type;
    :return: array of tokens with added types
    """
    prev_token: str = ''

    tokens: list[list[list[str | float | int]]] = []

    for line in tokens_raw:
        line_with_types: list[list[str | float | int]] = []

        for token in line:
            if is_keyword(token):
                line_with_types.append([token, 'kwd'])
            elif is_operator(token):
                if token == '|':
                    line_with_types[-1][1] = 'fnc'
                line_with_types.append([token, 'opr'])
            elif is_separator(token):
                line_with_types.append([token, 'sep'])
            elif is_type(token):
                line_with_types.append([token, 'typ'])
            elif is_boolean(token):
                line_with_types.append([token, 'bool'])
            elif is_integer(token):
                line_with_types.append([int(token), 'int'])
            elif is_float(token):
                line_with_types.append([float(token), 'float'])
            elif is_string(token):
                line_with_types.append([token[1:-1], 'str'])
            else:
                if prev_token == 'start':
                    line_with_types.append([token, 'fnc'])
                elif prev_token == 'use':
                    line_with_types.append([token, 'lib'])
                else:
                    line_with_types.append([token, 'var'])

            prev_token = token

        tokens.append(line_with_types)

    return tokens


keywords = ['start', 'end', 'use', 'return', 'break', 'while', 'if', 'else', 'elif']
operators = ['+', '-', '*', '/', '%', '(', ')', 'is', 'and', 'or', 'not', '>', '<', '<=', '>=', '==', '|', '=']
booleans = ['true', 'false']
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
types = ['int', 'float', 'str', 'bool']


def is_keyword(token: str) -> bool:
    """
    :param token: token as string
    :return: True if token is a keyword, otherwise False
    """
    return token in keywords


def is_operator(token: str) -> bool:
    """
    :param token: token as string
    :return: True if token is an operator, otherwise False
    """
    return token in operators


def is_type(token: str) -> bool:
    """
    :param token: token as string
    :return: True if token is a type, otherwise False
    """
    return token in types


def is_boolean(token: str) -> bool:
    """
    :param token: token as string
    :return: True if token is a boolean, otherwise False
    """
    return token in booleans


def is_integer(token: str) -> bool:
    """
    :param token: token as string
    :return: True if token is a integer, otherwise False
    """
    if token[0] == '-':
        token = token[1:]

    for numeral in token:
        if numeral not in numbers:
            return False

    return True


def is_float(token: str) -> bool:
    """
    :param token: token as string
    :return: True if token is a float, otherwise False
    """
    parts: list[str] = token.split('.')

    # if string has NO point '.', it isn't a floating point number
    if len(parts) == 1:
        return False

    return is_integer(parts[0]) and is_integer(parts[1])


def is_string(token: str) -> bool:
    """
    :param token: token as string
    :return: True if token is a string, otherwise False
    """
    return token[0] == '"' and token[-1] == '"'


def is_separator(token: str) -> bool:
    """
    :param token: token as string
    :return: True if token is a separator, otherwise False
    """
    return token == ','


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


if __name__ == '__main__':
    filename = input('Enter path to .min file you want to convert to tokens of: ')
    print_tokens(filename)
