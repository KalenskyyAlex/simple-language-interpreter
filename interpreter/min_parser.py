"""
This module does the most important work in interpreter.
It correctly parses given token list, to logical tree, to
prepare it for execution in interpreter.

Parser handles syntax errors such as unexpected statements,
invalid statements

Run '$python min_parser.py' to only get logical tree of .min from raw
text in .min file or use as module 'from parser import make_tree'
"""

# region Imported modules

from pprint import pprint
from typing import Any
from typing import Callable

from lexer import get_tokens
from structures import TokenType, Node, NodeType, Function, FunctionType
from commons import TOKEN_TYPES, USE, START, PIPE, CREATE, COMMA, RETURN, BREAK
from commons import TokenList

# endregion

# region Declared globals

tokens: list[TokenList] = []
line_numbers: list[int] = []
body_tree_element: list[NodeType] = []

tree: list[FunctionType | NodeType] = []

# endregion

# region Private functions

def is_valid_variable(token: TokenType) -> bool:
    """
    :param token: token
    :return: True, if token has valid type and name to be a variable token, otherwise False
    """
    if token.type == 'var' and isinstance(token.value, str):
        if token.value.strip():
            return True

    return False

def is_valid_library(token: TokenType) -> bool:
    """
    :param token: token
    :return: True, if token has valid type and name to be a library token, otherwise False
    """
    if token.type == 'lib' and isinstance(token.value, str):
        if token.value.strip():
            return True

    return False

def is_valid_type(token: TokenType) -> bool:
    """
    :param token: token
    :return: True, if token has valid type and name to be a type token, otherwise False
    """
    return token.type == 'typ' and token.value in TOKEN_TYPES


def validate_use_syntax(line: TokenList, line_number: int) -> None:
    """
    raise SYNTAX ERROR if syntax with 'use' keyword is incorrect

    :param line: array of tokens from one line of code
    :param line_number: number of line given for error handling
    """
    if len(line) == 2:
        if line[0] == USE and isinstance(line[1], TokenType):
            if is_valid_library(line[1]):
                return

    raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: INVALID LIBRARY CALL')

def create_use_node(line: TokenList, line_number: int) -> NodeType:
    """
    creates Node for further library call

    :param line: array of tokens from one line of code
    :param line_number: number of line given for error handling
    """
    return Node(USE, line_number, line[1])


def validate_start_syntax(line: TokenList, line_number: int) -> None:
    """
    raise SYNTAX ERROR if syntax with 'start' keyword is incorrect

    :param line: array of tokens from one line of code
    :param line_number: number of line given for error handling
    """

    if not isinstance(line[0], TokenType) or not isinstance(line[1], TokenType):
        raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: NO BRACKETS ARE ALLOWED')

    if not line[0] != START or not line[1].type == 'fnc':
        raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: INVALID FUNCTION ASSIGN')

    if len(line) > 2:
        if line[2] != PIPE:
            raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: ' +
                              'PIPE OPERATOR MUST BE BEFORE ARGUMENTS')

        line = line[3:]
        if len(line) == 0:
            raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: ' +
                              'NO ARGUMENTS AFTER PIPE OPERATOR')

        tokens_count = len(line)
        if (tokens_count + 1) % 4 != 0:
            raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: ' +
                              'INVALID ARGUMENTS STRUCTURE')

        for index in range(tokens_count):
            token = line[index]
            if not isinstance(token, TokenType):
                raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: NO BRACKETS ARE ALLOWED')

            match index % 4:
                case 0:
                    if token.type != 'var':
                        raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: ' +
                                          'ARGUMENTS MUST BE OF TYPE VAR')
                case 1:
                    if token != CREATE:
                        raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: ' +
                                          'MISSING IS OPERATOR')
                case 2:
                    if token.type != 'typ':
                        raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: ' +
                                          'INVALID TYPE')
                case 3:
                    if token != COMMA:
                        raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: ' +
                                          'MISSING COMMA BETWEEN ARGUMENTS')

def create_start_node(line: TokenList, line_number: int) -> FunctionType:
    """
    creates Function for logical tree

    :param line: array of tokens from one line of code
    :param line_number: number of line given for error handling
    """
    if not isinstance(line[1], TokenType):
        raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: NO BRACKETS ARE ALLOWED')

    if not isinstance(line[1].value, str):
        raise TypeError(f'NAME OF FUNCTION MUST BE STRING AT LINE {line_number}')

    name: str = line[1].value
    args: list[NodeType] = []
    body: list[NodeType] = []

    # check if we have arguments to fill 'args'
    if len(line) > 2:
        line = line[3:]

        split: TokenList = []

        for token in line:
            # arguments are separated by coma
            if token == COMMA:
                validate_is_syntax(split, line_number)
                args.append(create_variable_node(split, line_number))

                split = []
            else:
                split.append(token)

        # we check and add last argument block
        validate_is_syntax(split, line_number)
        args.append(create_variable_node(split, line_number))

    return Function(name, args, body, line_number)


def validate_is_syntax(block: TokenList, line_number: int) -> None:
    """
    raise SYNTAX ERROR if syntax with 'is' keyword is incorrect

    :param block: array of tokens, part of one line of code
    :param line_number: number of line given for error handling
    """
    if len(block) == 3:
        if block[1] == CREATE:
            if isinstance(block[0], TokenType) and isinstance(block[2], TokenType):
                if is_valid_variable(block[0]) and is_valid_type(block[2]):
                    return

    raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: INVALID VARIABLE ASSIGN')

def create_variable_node(block: TokenList, line_number: int) -> NodeType:
    """
    creates Node for variable assign

    :param block: array of tokens, part of one line of code
    :param line_number: number of line given for error handling
    """
    return Node(CREATE, line_number, block[2], block[0])


def validate_return_syntax(block: TokenList, line_number: int) -> None:
    """
    raise SYNTAX ERROR if syntax with 'return' keyword is incorrect

    :param block: array of tokens, part of one line of code
    :param line_number: number of line given for error handling
    """
    if block[0] != RETURN:
        raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: INVALID KEY AFTER \'return\'.')

def create_return_node(block: TokenList, line_number: int) -> NodeType:
    """
    creates Node for function return handling

    :param block: array of tokens, part of one line of code
    :param line_number: number of line given for error handling
    """
    right = block[1:]
    right = operate_calls(right, line_number)
    right = operate_helper(right, line_number, operate_1)
    right = operate_helper(right, line_number, operate_2)
    right = operate_helper(right, line_number, operate_3)

    return Node(RETURN, line_number, right)


def validate_break_syntax(block: TokenList, line_number: int) -> None:
    """
    raise SYNTAX ERROR if syntax with 'break' keyword is incorrect

    :param block: array of tokens, part of one line of code
    :param line_number: number of line given for error handling
    """
    if not len(block) == 1 or not block[0] == RETURN:
        raise SyntaxError(f'INVALID SYNTAX AT LINE{line_number}: INVALID KEY ' +
                          'AFTER \'return\'. VARIABLE EXPECTED')

def create_break_node(line_number: int) -> NodeType:
    """
    creates simple break-Node

    :param line_number: number of line given for error handling
    """
    return Node(BREAK, line_number)


def fill_body(line: TokenList, line_number: int) -> None:
    """
    generalization of validate_* methods
    fills one line of code to 'body'-like tree block
    on error raise one of exceptions from validate_* methods
    if there is no special commands in line, then
    parse line with operate_* methods

    :param line: array of tokens from one line of code
    :param line_number: number of line given for error handling
    """
    if ['is', 'opr'] in line:
        validate_is_syntax(line, line_number)
        body_tree_element.append(create_variable_node(line, line_number))
    elif ['return', 'kwd'] in line:
        validate_return_syntax(line, line_number)
        body_tree_element.append(create_return_node(line, line_number))
    elif ['break', 'kwd'] in line:
        validate_break_syntax(line, line_number)
        body_tree_element.append(create_break_node(line_number))
    else:
        if not line == ['end', 'kwd']:
            line = nest(line, line_number)

            line = operate_calls(line, line_number)

            line = operate_helper(line, line_number, operate_1)
            line = operate_helper(line, line_number, operate_2)
            line = operate_helper(line, line_number, operate_3)

            if isinstance(line[0], NodeType):
                complete_node = line[0]
                body_tree_element.append(complete_node)
            else:
                raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: FAILED TO OPERATE LINE')

def has_nesting(line: TokenList) -> bool:
    """
    :param line: array of tokens from one line of code
    :return: True if line has nesting, otherwise False
    """
    if ['(', 'opr'] in line or [')', 'opr'] in line:
        return True

    return False


def nest(line: TokenList, line_number: int) -> TokenList:
    """
    nest given line recursively
    :param line: array of tokens from one line of code to nest
    :param line_number: number of line given for error handling
    """
    # base case - no nesting
    if not has_nesting(line):
        return line

    nested_line: TokenList = []
    nested_: int = 0
    nested_segment: TokenList = []
    for token in line:
        if token == ['(', 'opr']:
            nested_ += 1

            if nested_ == 1:
                continue

        if token == [')', 'opr']:
            nested_ -= 1

        if not nested_ == 0:
            nested_segment.append(token)

        if nested_ == 0:
            if len(nested_segment) == 0:
                nested_line.append(token)
            else:
                nested_segment = nest(nested_segment, line_number)
                nested_line.append(nested_segment)
                nested_segment = []

    if not nested_ == 0:
        raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: INVALID NESTING')

    return nested_line


def operate_separators(segment: Any, line_number: int) -> Any:
    """
    nest code segment by separators
    :param segment: array of tokens, part of one line of code
    :param line_number: number of line given for error handling
    """
    if isinstance(segment, (int, float)):
        return segment
    if len(segment) == 1 and isinstance(segment[0], str):
        return segment

    operated_segment = segment
    tokens_count = len(segment)
    for index in range(tokens_count):
        token = segment[index]
        if isinstance(token[0], str):
            if token[1] == 'sep':
                if token[0] == ',':
                    left = operate_separators(segment[:index], line_number)

                    if len(left) == 1 and isinstance(left[0], dict):
                        left = left[0]

                    right = operate_separators(segment[index + 1:], line_number)

                    if len(right) == 1 and isinstance(right[0], dict):
                        right = right[0]

                    operated_segment = {
                        'left': left[0] if len(left) == 1 else left,
                        'operation': token,
                        'right': right[0] if len(right) == 1 else right
                    }
                    break

    return operated_segment


# TODO unify operate ... methods
# TODO REPLACE operate1 and this methods sequence
def operate_calls(segment: Any, line_number: int) -> Any:
    """
    nest code segment by '|' (function) operator
    :param segment: array of tokens, part of one line of code
    :param line_number: number of line given for error handling
    """
    if isinstance(segment, (float, int)):
        return segment
    if len(segment) == 1 and isinstance(segment[0], str):
        return segment

    operated_segment = segment
    if isinstance(segment, dict):
        operated_segment['right'] = operate_calls(segment['right'], line_number)
        operated_segment['left'] = operate_calls(segment['left'], line_number)
    else:
        tokens_count = len(segment)
        for index in range(tokens_count):
            token = segment[index]

            if not isinstance(token, int) and not isinstance(token, float):
                if isinstance(token[0], str):
                    if token[1] == 'opr':
                        if token[0] == '|':
                            left = operate_calls(segment[:index], line_number)

                            if len(left) == 1 and isinstance(left[0], dict):
                                left = left[0]

                            right = operate_separators(segment[index + 1:], line_number)

                            if len(right) == 1 and isinstance(right[0], dict):
                                right = right[0]

                            right = operate_calls(right, line_number)

                            if len(right) == 1 and isinstance(right[0], dict):
                                right = right[0]

                            operated_segment = {
                                'left': left[0] if len(left) == 1 else left,
                                'operation': token,
                                'right': right
                            }
                            break
                else:
                    segment[index] = operate_calls(token, line_number)

    return operated_segment


def operate_helper(line: Any, line_number: int, method: Callable) -> Any:
    """
    is needed to go through already modified line (partially nested)
    :param line: array of tokens, from one line of code
    :param line_number: number of line given for error handling
    :param method: function to nest parts of not nested line
    """
    if isinstance(line, dict):
        line['left'] = operate_helper(line['left'], line_number, method)
        line['right'] = operate_helper(line['right'], line_number, method)
    else:
        line = method(line, line_number)

    return line


# def operate_helper_new(line, line_number, method, operators):
#     if isinstance(line, dict):
#         line['left'] = operate_helper(line['left'], line_number, method)
#         line['right'] = operate_helper(line['right'], line_number, method)
#     else:
#         line = method(line, line_number)
#
#     return line


def operate_1(segment: Any, line_number: int) -> Any:
    """
    nest code segment by '=' (assign) operator
    :param segment: array of tokens, part of one line of code
    :param line_number: number of line given for error handling
    :return: nested segment of code
    """
    if isinstance(segment, (int, float)):
        return segment
    if len(segment) == 1 and isinstance(segment[0], str):
        return segment

    operated_segment = segment
    tokens_count = len(segment)
    for index in range(tokens_count):
        token = segment[index]
        if not isinstance(token, (int, float)):
            if isinstance(token[0], str):
                if token[1] == 'opr':
                    if token[0] == '=':
                        left = operate_1(segment[:index], line_number)

                        if len(left) == 1 and isinstance(left[0], dict):
                            left = left[0]

                        right = operate_1(segment[index + 1:], line_number)

                        if len(right) == 1 and isinstance(right[0], dict):
                            right = right[0]

                        operated_segment = {
                            'left': left[0] if len(left) == 1 else left,
                            'operation': token,
                            'right': right[0] if len(right) == 1 else right
                        }
                        break
            else:
                segment[index] = operate_1(token, line_number)

    return operated_segment


def operate_2(segment: Any, line_number: int) -> Any:
    """
    nest code segment by '+' (add) and '-' (subtract) operators
    :param segment: array of tokens, part of one line of code
    :param line_number: number of line given for error handling
    :return: nested segment of code
    """
    if isinstance(segment, (int, float)):
        return segment
    if len(segment) == 1 and isinstance(segment[0], str):
        return segment

    operated_segment = segment
    tokens_count = len(segment)
    for index in range(tokens_count):
        token = segment[index]
        if not isinstance(token, (int, float)):
            if isinstance(token, dict):
                continue
            if isinstance(token[0], str):
                if len(token) >= 2:
                    if token[1] == 'opr':
                        if token[0] == '+' or token[0] == '-':
                            left = operate_2(segment[:index], line_number)

                            if len(left) == 1 and isinstance(left[0], dict):
                                left = left[0]

                            right = operate_2(segment[index + 1:], line_number)

                            if len(right) == 1 and isinstance(right[0], dict):
                                right = right[0]

                            if len(left) == 0 and token[0] == '-':
                                left = [0, 'int']

                            operated_segment = {
                                'left': left[0] if len(left) == 1 else left,
                                'operation': token,
                                'right': right[0] if len(right) == 1 else right
                            }
                            break
            else:
                segment[index] = operate_2(token, line_number)

    return operated_segment


def operate_3(segment: Any, line_number: int) -> Any:
    """
    nest code segment by '*' (multiply), '/' (divide) and '%' (modulo) operators
    :param segment: array of tokens, part of one line of code
    :param line_number: number of line given for error handling
    :return: nested segment of code
    """
    if isinstance(segment, (int, float)):
        return segment
    if not ['*', 'opr'] in segment and not ['/', 'opr'] in segment and not ['%', 'opr'] in segment:
        return segment

    operated_segment = segment
    tokens_count = len(segment)
    for index in range(tokens_count):
        token = segment[index]

        if isinstance(token, dict):
            operate_helper(token, line_number, operate_3)
            continue

        if isinstance(token[0], str):
            if token[1] == 'opr':
                if token[0] == '*' or token[0] == '/' or token[0] == '%':
                    left = operate_3(segment[:index], line_number)

                    if len(left) == 1 and isinstance(left[0], dict):
                        left = left[0]

                    right = operate_3(segment[index + 1:], line_number)

                    if len(right) == 1 and isinstance(right[0], dict):
                        right = right[0]

                    operated_segment = {
                        'left': left[0] if len(left) == 1 else left,
                        'operation': token,
                        'right': right[0] if len(right) == 1 else right
                    }
                    break
        else:
            segment[index] = operate_3(token, line_number)

    return operated_segment


# TODO
# def operate(segment: Any, line_number: int, operators: list[str]) -> Any:
#     """
#     nest code segment by given operators
#     :param segment: array of tokens, part of one line of code
#     :param line_number: number of line given for error handling
#     :param operators: operators for used to nest code segment
#     :return: nested segment of code
#     """
#     operated_segment = segment
#
#     for index in range(len(segment)):
#         token = segment[index]
#
#         if token[1] == 'opr':
#             if token[0] in operators:
#                 left = operate_helper_new(segment[:index], line_number, operate, operators)
#                 right = operate_helper_new(segment[index + 1:], line_number, operate, operators)
#
#                 operated_segment = {
#                     'left': left,
#                     'operation': token,
#                     'right': right
#                 }
#
#                 return operated_segment


def nest_vertical(block: Any, line_number: int) -> Any:
    """
    nest code segment by if/else/while constructions
    :param block: array of tokens, several lines of code
    :param line_number: number of first line from block, given for error handling
    :return: nested block of code
    """
    new_block = []
    writing_inner_block = False
    block_nesting = 0
    inner_block = {}
    writing_else = False

    tokens_count = len(block)
    for index in range(tokens_count):
        line = block[index]

        if not writing_inner_block:
            if not isinstance(line, dict):
                if ['while', 'kwd'] in line:
                    operation = line[0]
                    condition = line[1:]
                    inner_block = {
                        'left': condition,
                        'operation': operation,
                        'right': [],
                        'line': line_number
                    }

                    block_nesting += 1
                    writing_inner_block = True
                elif ['if', 'kwd'] in line:
                    operation = line[0]
                    condition = line[1:]
                    inner_block = {
                        'left': condition,
                        'operation': operation,
                        'right': [],
                        'else': [],
                        'line': line_number
                    }
                    block_nesting += 1
                    writing_inner_block = True
                else:
                    new_block.append(line)
            else:
                new_block.append(line)
        else:
            if not isinstance(line, dict):
                if ['if', 'kwd'] in line or \
                        ['while', 'kwd'] in line:
                    block_nesting += 1
                elif ['end', 'kwd'] in line:
                    block_nesting -= 1
                elif block_nesting == 1 and ['else', 'kwd'] in line:
                    writing_else = True
                    continue

                if block_nesting == 0:
                    writing_inner_block = False
                    writing_else = False
                    inner_block['right'] = nest_vertical(inner_block['right'], line_number)
                    new_block.append(inner_block)
                elif writing_else:
                    inner_block['else'].append(line)
                else:
                    inner_block['right'].append(line)
            else:
                inner_block['right'].append(line)

        line_number += 1
    return new_block

# endregion

# region Public functions

def make_tree(file_name: str) -> Any:
    """
    creates logical tree from code in .min file
    :param file_name: path to .min file to be processed
    :return: logical tree created
    """
    global body_tree_element

    global tokens
    global line_numbers

    old_type_tokens, line_numbers = get_tokens(file_name)

    tokens = []
    nested = 0
    in_function_body = False

    for old_type_line in old_type_tokens:
        new_type_line: TokenList = []
        for old_type_token in old_type_line:
            new_type_line.append(old_type_token)
        tokens.append(new_type_line)

    tokens_count = len(tokens)
    for index in range(tokens_count):

        line = tokens[index]
        line_number = line_numbers[index]

        if in_function_body:
            if ['start', 'kwd'] in line:
                raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}:' +
                                  ' CAN NOT ASSIGN FUNCTION IN FUNCTION\'S BODY')

            if ['if', 'kwd'] in line:
                nested += 1
            if ['while', 'kwd'] in line:
                nested += 1
            if ['end', 'kwd'] in line:
                nested -= 1

            fill_body(line, line_number)
            if len(body_tree_element) == 0:
                raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: ' +
                                  'UNABLE TO READ LINE')
        else:
            if ['use', 'kwd'] in line:
                validate_use_syntax(line, line_number)
                tree.append(create_use_node(line, line_number))

            if ['start', 'kwd'] in line:
                validate_start_syntax(line, line_number)
                tree.append(create_start_node(line, line_number))

                nested += 1
                body_tree_element = []
                in_function_body = True

            if ['if', 'kwd'] in line or\
                    ['else', 'kwd'] in line or\
                    ['elif', 'kwd'] in line or\
                    ['loop', 'kwd'] in line or\
                    ['end', 'kdw'] in line:
                raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: ' +
                                  'CAN NOT USE KEYWORD OUTSIDE OF FUNCTION\'S BODY')

        if nested == 0 and in_function_body:
            in_function_body = False

            body_tree_element = nest_vertical(body_tree_element, tree[-1].line_number)
            if body_tree_element[-1] == [['end', 'kwd']]:
                body_tree_element = body_tree_element[:-1]

            if not isinstance(tree[-1], Function):
                raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: ' +
                                  'BLOCK IS NOT RECOGNIZED AS FUNCTION')

            proto_function = tree[-1]
            complete_function = Function(proto_function.name,
                                         proto_function.args,
                                         body_tree_element,
                                         proto_function.line_number)

            tree[-1] = complete_function

    return tree


def print_tree(file_name: str) -> None:
    """
    outputs logical tree created from code in .min file
    :param file_name: path to .min file to be processed
    """
    print("Produced tree:")

    pprint(make_tree(file_name),
           width=140)

    print("-" * 70)

# endregion


if __name__ == '__main__':
    filename = input('Enter path to .min file you want to parse: ')
    print_tree(filename)
