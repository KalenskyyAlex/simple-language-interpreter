"""
This module does the most important work in interpreter.
It correctly parses given token list, to logical tree, to
prepare it for execution in interpreter.

Parser handles syntax errors such as unexpected statements,
invalid statements

Run '$python parser.py' to only get logical tree of .min from raw
text in .min file or use as module 'from parser import make_tree'
"""

# region Imported modules

from lexer import get_tokens

from typing import Any
from typing import Iterable

from pprint import pprint

# endregion

# region Declared types

StrToken = list[str]
NumToken = list[str | float | int]
Token = StrToken | NumToken
TokenList = list[Token]
NestedTokenList = list[Token | list]
TreeNode = dict[str, Any]
BlockList = list[TreeNode | TokenList | NestedTokenList]

# endregion

# region Declared globals

tokens: TokenList = []
line_numbers: list[int] = []
function_tree_element: TreeNode = {}
variable_tree_element: TreeNode = {}
return_tree_element: TreeNode = {}
break_tree_element: TreeNode = {}
body_tree_element: BlockList = []
nested = 0
in_function_body = False

tree: list[dict] = []

# endregion

# region Private functions

def validate_use_syntax(line: TokenList | NestedTokenList, line_number: int) -> None:
    """
    forms 'use'-like block of tree
    raise SYNTAX ERROR if syntax with 'use' keyword is incorrect

    :param line: array of tokens from one line of code
    :param line_number: number of line given for error handling
    """
    if len(line) == 2:
        if line[0][0] == 'use':
            if line[1][1] == 'lib':
                return

    raise Exception(f'INVALID SYNTAX ERROR AT LINE {line_number}: INVALID LIBRARY CALL')


def validate_start_syntax(line: TokenList | NestedTokenList, line_number: int) -> None:
    """
    forms 'function'-like block of tree
    raise SYNTAX ERROR if syntax with 'start' keyword is incorrect

    :param line: array of tokens from one line of code
    :param line_number: number of line given for error handling
    """
    global function_tree_element

    function_tree_element = {}

    if line[0][0] == 'start' and line[1][1] == 'fnc':
        name = line[1][0]

        function_tree_element['line'] = line_number
        function_tree_element['name'] = name
        function_tree_element['args'] = []
        function_tree_element['body'] = []

        # check if we have arguments to fill 'args'
        if len(line) > 2:
            if line[2][0] == '|' and len(line) > 3:
                line = line[3:]

                split: TokenList = []

                for token in line:
                    # arguments are separated by coma
                    if token[1] == 'sep':
                        validate_is_syntax(split, line_number)

                        function_tree_element['args'].append(variable_tree_element)
                        split = []
                    else:
                        split.append(token)

                # we check and add last argument block
                validate_is_syntax(split, line_number)

                function_tree_element['args'].append(variable_tree_element)

                return
        else:
            return

    raise Exception(f'INVALID SYNTAX ERROR AT LINE {line_number}: INVALID FUNCTION ASSIGN')


def validate_is_syntax(block: TokenList | NestedTokenList, line_number: int) -> None:
    """
    forms 'variable'-like block of tree
    raise SYNTAX ERROR if syntax with 'is' keyword is incorrect

    :param block: array of tokens, part of one line of code
    :param line_number: number of line given for error handling
    """
    global variable_tree_element

    variable_tree_element = {}

    if len(block) == 3:
        if block[1][0] == 'is':
            if block[0][1] == 'var':
                if block[2][1] == 'typ':
                    variable_tree_element['line'] = line_number
                    variable_tree_element['left'] = block[0]
                    variable_tree_element['operation'] = ['is', 'opr']
                    variable_tree_element['right'] = block[2]

                    return

    raise Exception(f'INVALID SYNTAX ERROR AT LINE {line_number}: INVALID VARIABLE ASSIGN')


def validate_return_syntax(block: TokenList | NestedTokenList, line_number: int) -> None:
    """
    forms 'return'-like block of tree
    raise SYNTAX ERROR if syntax with 'return' keyword is incorrect

    :param block: array of tokens, part of one line of code
    :param line_number: number of line given for error handling
    """
    global return_tree_element

    return_tree_element = {}

    if block[0] == ['return', 'kwd']:
        return_tree_element['line'] = line_number
        return_tree_element['left'] = None
        return_tree_element['operation'] = ['return', 'kwd']
        return_tree_element['right'] = block[1:]

        return

    raise Exception(f'INVALID SYNTAX ERROR AT LINE {line_number}: INVALID KEY AFTER \'return\'.')


def validate_break_syntax(block: TokenList | NestedTokenList, line_number: int) -> None:
    """
    forms 'break'-like block of tree
    raise SYNTAX ERROR if syntax with 'break' keyword is incorrect

    :param block: array of tokens, part of one line of code
    :param line_number: number of line given for error handling
    """
    global break_tree_element

    break_tree_element = {}

    if len(block) == 1:
        if block[0] == ['break', 'kwd']:
            break_tree_element['line'] = line_number
            break_tree_element['left'] = None
            break_tree_element['operation'] = block[0]
            break_tree_element['right'] = None

            return

    raise Exception(f'INVALID SYNTAX ERROR AT LINE{line_number}: INVALID KEY AFTER \'return\'. VARIABLE EXPECTED')


def fill_body(line: TokenList | NestedTokenList, line_number: int) -> None:
    """
    generalization of validate_* methods
    fills one line of code to 'body'-like tree block
    on error raise one of exceptions from validate_* methods
    if there is no special commands in line, then
    parse line with operate_* methods

    :param line: array of tokens from one line of code
    :param line_number: number of line given for error handling
    """
    global body_tree_element
    global return_tree_element

    if ['is', 'opr'] in line:
        validate_is_syntax(line, line_number)

        body_tree_element.append(variable_tree_element)
    elif ['return', 'kwd'] in line:
        validate_return_syntax(line, line_number)

        return_tree_element['right'] = operate_calls(return_tree_element['right'], line_number)
        return_tree_element['right'] = operate_helper(return_tree_element['right'], line_number, operate_1)
        return_tree_element['right'] = operate_helper(return_tree_element['right'], line_number, operate_2)
        return_tree_element['right'] = operate_helper(return_tree_element['right'], line_number, operate_3)

        if isinstance(return_tree_element, dict):
            return_tree_element['line'] = line_number

        body_tree_element.append(return_tree_element)
    elif ['break', 'kwd'] in line:
        validate_break_syntax(line, line_number)

        body_tree_element.append(break_tree_element)
    else:
        if not line == ['end', 'kwd']:
            line = nest(line, line_number)

            line = operate_calls(line, line_number)

            line = operate_helper(line, line_number, operate_1)

            line = operate_helper(line, line_number, operate_2)

            line = operate_helper(line, line_number, operate_3)

            if isinstance(line, dict):
                line['line'] = line_number

            body_tree_element.append(line)


def has_nesting(line: TokenList | NestedTokenList) -> bool:
    """
    :param line: array of tokens from one line of code
    :return: True if line has nesting, otherwise False
    """
    if ['(', 'opr'] in line or [')', 'opr'] in line:
        return True

    return False


def nest(line: TokenList | NestedTokenList, line_number: int) -> NestedTokenList:
    """
    nest given line recursively
    :param line: array of tokens from one line of code to nest
    :param line_number: number of line given for error handling
    """
    # base case - no nesting
    if not has_nesting(line):
        return line
    else:
        nested_line: NestedTokenList = []
        nested_: int = 0
        nested_segment: NestedTokenList = []
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
            raise Exception(f'INVALID SYNTAX ERROR AT LINE {line_number}: INVALID NESTING')

        return nested_line


def operate_separators(segment: Any, line_number: int) -> Any:
    """
    nest code segment by separators
    :param segment: array of tokens, part of one line of code
    :param line_number: number of line given for error handling
    """
    if isinstance(segment, int) or isinstance(segment, float):
        return segment
    if len(segment) == 1 and isinstance(segment[0], str):
        return segment
    else:
        operated_segment = segment
        for index in range(len(segment)):
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
    if isinstance(segment, int) or isinstance(segment, float):
        return segment
    if len(segment) == 1 and isinstance(segment[0], str):
        return segment
    else:
        operated_segment = segment
        if isinstance(segment, dict):
            operated_segment['right'] = operate_calls(segment['right'], line_number)
            operated_segment['left'] = operate_calls(segment['left'], line_number)
        else:
            for index in range(len(segment)):
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


def operate_helper(line: Any, line_number: int, method: callable) -> Any:
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


def operate_helper_new(line, line_number, method, operators):
    if isinstance(line, dict):
        line['left'] = operate_helper(line['left'], line_number, method)
        line['right'] = operate_helper(line['right'], line_number, method)
    else:
        line = method(line, line_number)

    return line


def operate_1(segment: Any, line_number: int) -> Any:
    """
    nest code segment by '=' (assign) operator
    :param segment: array of tokens, part of one line of code
    :param line_number: number of line given for error handling
    :return: nested segment of code
    """
    if isinstance(segment, int) or isinstance(segment, float):
        return segment
    if len(segment) == 1 and isinstance(segment[0], str):
        return segment
    else:
        operated_segment = segment
        for index in range(len(segment)):
            token = segment[index]
            if not isinstance(token, int) and not isinstance(token, float):
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
    if isinstance(segment, int) or isinstance(segment, float):
        return segment
    if len(segment) == 1 and isinstance(segment[0], str):
        return segment
    else:
        operated_segment = segment

        for index in range(len(segment)):
            token = segment[index]
            if not isinstance(token, int) and not isinstance(token, float):
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
    if isinstance(segment, int) or isinstance(segment, float):
        return segment
    if not ['*', 'opr'] in segment and not ['/', 'opr'] in segment and not ['%', 'opr'] in segment:
        return segment
    else:
        operated_segment = segment

        for index in range(len(segment)):
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
def operate(segment: Any, line_number: int, operators: list[str]) -> Any:
    """
    nest code segment by given operators
    :param segment: array of tokens, part of one line of code
    :param line_number: number of line given for error handling
    :param operators: operators for used to nest code segment
    :return: nested segment of code
    """
    operated_segment = segment

    for index in range(len(segment)):
        token = segment[index]

        if token[1] == 'opr':
            if token[0] in operators:
                left = operate_helper_new(segment[:index], line_number, operate, operators)
                right = operate_helper_new(segment[index + 1:], line_number, operate, operators)

                operated_segment = {
                    'left': left,
                    'operation': token,
                    'right': right
                }

                return operated_segment


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

    for index in range(len(block)):
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
    global in_function_body
    global nested
    global body_tree_element

    global tokens
    global line_numbers

    tokens, line_numbers = get_tokens(file_name)

    for index in range(len(tokens)):

        line = tokens[index]
        line_number = line_numbers[index]

        if in_function_body:
            if ['start', 'kwd'] in line:
                raise f'INVALID SYNTAX ERROR AT LINE {line_number}: CAN NOT ASSIGN FUNCTION IN FUNCTION\'S BODY'

            if ['if', 'kwd'] in line:
                nested += 1
            if ['while', 'kwd'] in line:
                nested += 1
            if ['end', 'kwd'] in line:
                nested -= 1

            fill_body(line, line_number)
            if len(body_tree_element) == 0:
                return
        else:
            if ['use', 'kwd'] in line:
                validate_use_syntax(line, line_number)

                tree.append({
                    'line': line_number,
                    'left': None,
                    'operation': 'use',
                    'right': line[1][0]
                })

            if ['start', 'kwd'] in line:
                validate_start_syntax(line, line_number)

                tree.append(function_tree_element)
                nested += 1
                body_tree_element = []
                in_function_body = True

            if ['if', 'kwd'] in line or\
                    ['else', 'kwd'] in line or\
                    ['elif', 'kwd'] in line or\
                    ['loop', 'kwd'] in line or\
                    ['end', 'kdw'] in line:
                raise f'INVALID SYNTAX ERROR AT LINE {line_number}: CAN NOT USE KEYWORD OUTSIDE OF FUNCTION\'S BODY'

        if nested == 0 and in_function_body:
            in_function_body = False
            body_tree_element = nest_vertical(body_tree_element, tree[-1]['line'])
            if body_tree_element[-1] == [['end', 'kwd']]:
                body_tree_element = body_tree_element[:-1]
            tree[-1]['body'] = body_tree_element

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
