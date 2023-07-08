"""
This module does the most important work in interpreter.
It correctly parses given token list, to logical tree, to
prepare it for execution in interpreter.

Parser handles syntax errors such as unexpected statements,
invalid statements

Run '$python min_parser.py' to only get logical tree of .min from raw
text in .min file or use as module 'from parser import parse'
"""

# region Imported modules

from pprint import pprint
from typing import Callable, Optional

from .min_lexer import get_tokens
from .utils.structures import Token, Node, Function, Block
from .utils.commons import TOKEN_TYPES, USE, START, PIPE, CREATE, COMMA, RETURN, BREAK
from .utils.commons import ASSIGN, PLUS, MINUS, DIVIDE, MODULO, MULTIPLY
from .utils.commons import LEFT_BRACKET, RIGHT_BRACKET, EQUALS, LESS_THAN, MORE_THAN, NO_LESS_THAN
from .utils.commons import WHILE, IF, ELSE, END, NO_MORE_THAN
from .utils.commons import TokenList

# endregion

# region Private functions

def __is_valid_variable(token: Token) -> bool:
    if token.type == 'var' and isinstance(token.value, str):
        if token.value.strip():
            return True

    return False

def __is_valid_library(token: Token) -> bool:
    if token.type == 'lib' and isinstance(token.value, str):
        if token.value.strip():
            return True

    return False

def __is_valid_type(token: Token) -> bool:
    return token.type == 'typ' and token.value in TOKEN_TYPES


def __is_unpackable(tokens_list: TokenList) -> bool:
    # returns True if there is only one element in tokens list, which is Token itself,
    # otherwise False
    return len(tokens_list) == 1 and isinstance(tokens_list[0], Node)


def __extract_node(token_list: TokenList) -> Node | TokenList:
    # unpacks single Token in list
    match len(token_list):
        case 0:
            raise RuntimeError('EMPTY TOKEN LIST GIVEN')
        case 1:
            if isinstance(token_list[0], Node):
                return token_list[0]

            raise RuntimeError('FAILED TO UNPACK TOKEN LIST')
        case _:
            return token_list


def __extract_token(token_list: TokenList) -> Token:
    # extracts Token from list, raises an error on fail
    match len(token_list):
        case 1:
            if isinstance(token_list[0], Token):
                return token_list[0]
            raise RuntimeError('FAILED TO UNPACK ARRAY OF NON-TOKEN TYPE')
        case _:
            raise RuntimeError('FAILED TO EXTRACT SINGLE TOKENS IN FINAL NODES')

def __extract_inlist_tokens_from_node(node: Node) -> Node:
    # extracts all one-in-list Tokens from Node
    if isinstance(node.left, Node):
        node.left = __extract_inlist_tokens_from_node(node.left)
    elif isinstance(node.left, list):
        node.left = __extract_token(node.left)

    if isinstance(node.right, Node):
        node.right = __extract_inlist_tokens_from_node(node.right)
    elif isinstance(node.right, list):
        node.right = __extract_token(node.right)

    return node

def __extract_inlist_tokens_from_block(block: Block) -> Block:
    lines_count = len(block.body)
    for index in range(lines_count):
        line = block.body[index]

        if isinstance(line, Node):
            block.body[index] = __extract_inlist_tokens_from_node(line)
        elif isinstance(line, Block):
            block.body[index] = __extract_inlist_tokens_from_block(line)

    if block.next_block:
        block.next_block = __extract_inlist_tokens_from_block(block.next_block)

    return block

def __extract_inlist_tokens_from_tree(tree: list[Function | Node]) -> list[Function | Node]:
    # extracts all one-in-list Tokens from tree
    tree_length = len(tree)
    for index in range(tree_length):
        element = tree[index]
        if isinstance(element, Node):
            tree[index] = __extract_inlist_tokens_from_node(element)
        elif isinstance(element, Function):
            new_body: list[Node | Block] = []
            for line in element.body:
                if isinstance(line, Node):
                    new_body.append(__extract_inlist_tokens_from_node(line))
                elif isinstance(line, Block):
                    new_body.append(__extract_inlist_tokens_from_block(line))

            new_args: list[Node] = [__extract_inlist_tokens_from_node(n) for n in element.args]

            name = element.name
            line_number = element.line_number

            if all(isinstance(node, Node) for node in new_args):
                tree[index] = Function(name, new_args, new_body, line_number)
            else:
                raise TypeError('BLOCK DETECTED IN FUNCTION ARGUMENTS')
        else:
            raise TypeError('UNKNOWN ELEMENTS IN PARSED TREE')

    return tree

def __validate_use_syntax(line: TokenList, line_number: int) -> None:
    # raises SYNTAX ERROR if syntax with 'use' keyword is incorrect
    if len(line) == 2:
        if line[0] == USE and isinstance(line[1], Token):
            if __is_valid_library(line[1]):
                return

    raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: INVALID LIBRARY CALL')

def __create_use_node(line: TokenList, line_number: int) -> Node:
    # creates Node for further library call
    return Node(USE, line_number, line[1])


def __validate_start_syntax(line: TokenList, line_number: int) -> None:
    # raise SYNTAX ERROR if syntax with 'start' keyword is incorrect
    if not isinstance(line[0], Token) or not isinstance(line[1], Token):
        raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: NO BRACKETS ARE ALLOWED')

    if line[0] != START or line[1].type != 'fnc':
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
            if not isinstance(token, Token):
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

def __parse_start(line: TokenList, line_number: int) -> tuple[list[Node], str]:
    # parses arguments for function
    if not isinstance(line[1], Token):
        raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: NO BRACKETS ARE ALLOWED')

    if not isinstance(line[1].value, str):
        raise TypeError(f'NAME OF FUNCTION MUST BE STRING AT LINE {line_number}')

    name: str = line[1].value
    args: list[Node] = []

    # check if we have arguments to fill 'args'
    if len(line) > 2:
        line = line[3:]

        split: TokenList = []

        for token in line:
            # arguments are separated by coma
            if token == COMMA:
                __validate_is_syntax(split, line_number)
                args.append(__create_variable_node(split, line_number))

                split = []
            else:
                split.append(token)

        # we check and add last argument block
        __validate_is_syntax(split, line_number)
        args.append(__create_variable_node(split, line_number))

    return args, name


def __validate_is_syntax(block: TokenList, line_number: int) -> None:
    # raise SYNTAX ERROR if syntax with 'is' keyword is incorrect
    if len(block) == 3:
        if block[1] == CREATE:
            if isinstance(block[0], Token) and isinstance(block[2], Token):
                if __is_valid_variable(block[0]) and __is_valid_type(block[2]):
                    return

    raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: INVALID VARIABLE ASSIGN')

def __create_variable_node(block: TokenList, line_number: int) -> Node:
    # creates Node for variable assign
    return Node(CREATE, line_number, block[2], block[0])


def __validate_return_syntax(block: TokenList, line_number: int) -> None:
    # raise SYNTAX ERROR if syntax with 'return' keyword is incorrect
    if block[0] != RETURN:
        raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: INVALID KEY AFTER \'return\'.')

def __create_return_node(block: TokenList, line_number: int) -> Node:
    # creates Node for function return handling
    right: Optional[Node | TokenList] = block[1:]

    if isinstance(right, list) and len(right) == 0:
        right = None

    if isinstance(right, list) and len(right) > 1:
        right = parse_line(right, line_number)

    return Node(RETURN, line_number, right)


def __validate_break_syntax(block: TokenList, line_number: int) -> None:
    # raise SYNTAX ERROR if syntax with 'break' keyword is incorrect
    if not len(block) == 1 or not block[0] == BREAK:
        raise SyntaxError(f'INVALID SYNTAX AT LINE{line_number}: INVALID KEY AFTER \'break\'')

def __create_break_node(line_number: int) -> Node:
    # creates simple break-Node
    return Node(BREAK, line_number)


def __has_nesting_raw(line: TokenList) -> bool:
    # returns True if line has nesting, otherwise False. Is used to nest raw line
    if LEFT_BRACKET in line or RIGHT_BRACKET in line:
        return True

    return False

def __has_nesting_processed(line: TokenList) -> bool:
    # returns True if line has nesting, otherwise False. Is used to check
    # for nesting in already nested line
    return any(isinstance(token, list | Node) for token in line)


def __nest(line: TokenList, line_number: int) -> TokenList:
    # nests given line recursively

    # base case - no nesting
    if not __has_nesting_raw(line):
        return line

    nested_line: TokenList = []
    nested: int = 0
    nested_segment: TokenList = []
    for token in line:
        if token == LEFT_BRACKET:
            nested += 1

            if nested == 1:
                continue

        if token == RIGHT_BRACKET:
            nested -= 1

        if not nested == 0:
            nested_segment.append(token)

        if nested == 0:
            if len(nested_segment) == 0:
                nested_line.append(token)
            else:
                nested_segment = __nest(nested_segment, line_number)
                nested_line.append(nested_segment)
                nested_segment = []

    if nested != 0:
        raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: INVALID NESTING')

    return nested_line


def __parse_calls(segment: TokenList, operators: TokenList, line_number: int) -> TokenList:
    # nests code segment by '|' (function) operator
    if isinstance(segment, list) and not any(operator in segment for operator in operators):
        if not __has_nesting_processed(segment):
            return segment

    operated_segment: TokenList = list(segment)

    tokens_count = len(segment)
    for index in range(tokens_count):
        token = segment[index]

        if isinstance(token, Node | list):
            token = __parse_helper(token, line_number, __parse_calls, [PIPE])
        elif token in operators:
            left = __parse_calls(operated_segment[:index], [PIPE], line_number)

            right = __parse_helper(operated_segment[index + 1:], line_number, __parse_by, [COMMA])
            if not isinstance(right, Token):
                right = __parse_helper(right, line_number, __parse_calls, [PIPE])

            if not right:
                operated_segment = [Node(token, line_number, None, left)]
            else:
                operated_segment = [Node(token, line_number, right, left)]

            break

        operated_segment[index] = token
    return operated_segment


def __parse_helper(line: Node | TokenList, line_number: int,
                   method: Callable, operators: TokenList) -> Node | TokenList:
    # is needed to go through already modified line (partially nested)
    if isinstance(line, Node):
        if line.left is not None:
            line.left = __parse_helper(line.left, line_number, method, operators)
        if line.right is not None:
            line.right = __parse_helper(line.right, line_number, method, operators)
    else:
        line = method(line, operators, line_number)

    if isinstance(line, list):
        if __is_unpackable(line):
            line = __extract_node(line)

    return line


def __parse_by(segment: TokenList, operators: TokenList, line_number: int) -> TokenList:
    # parse line by given operators
    if isinstance(segment, list) and not any(operator in segment for operator in operators):
        if not __has_nesting_processed(segment):
            return segment

    operated_segment: TokenList = list(segment)

    tokens_count = len(segment)
    for index in range(tokens_count):
        token = segment[index]

        if isinstance(token, Node | list):
            token = __parse_helper(token, line_number, __parse_by, operators)
        elif token in operators:
            left = __parse_helper(operated_segment[:index], line_number, __parse_by, operators)
            if not left:
                if token in [PLUS, MINUS]:
                    left = [Token('int', 0)]
                else:
                    raise SyntaxError(f'MISSING OPERAND BEFORE {token.value} AT LINE {line_number}')

            right = __parse_helper(operated_segment[index + 1:], line_number, __parse_by, operators)
            if not right:
                raise SyntaxError(f'MISSING OPERAND AFTER {token.value} AT LINE {line_number}')

            operated_segment = [Node(token, line_number, right, left)]
            break

        operated_segment[index] = token

    return operated_segment


def __create_block_header(line: TokenList, line_number: int) -> tuple[Token, Optional[Node]]:
    # nest code segment by if/else/while constructions
    operator = line[0]
    if not isinstance(operator, Token):
        raise SyntaxError(f'WRONG BLOCK HEADER AT LINE {line_number}')
    if operator not in [WHILE, IF, ELSE]:
        raise SyntaxError(f'WRONG OPERATOR IN BLOCK HEADER AT LINE {line_number}')

    condition = parse_line(line[1:], line_number) if operator != ELSE else None

    if condition:
        condition = __extract_inlist_tokens_from_node(condition)

    return operator, condition

def __find_end_else_indexes(body: list, start: int,
                            end: int) -> tuple[Optional[int], Optional[int]]:
    else_line_index: Optional[int] = None
    end_line_index: Optional[int] = None
    for index in range(start, end):
        line = body[index]
        if isinstance(line, list) and ELSE in line:
            else_line_index = index
        if isinstance(line, list) and END in line:
            end_line_index = index
            break

    return else_line_index, end_line_index

def __nest_blocks(raw_body: list[Node | TokenList], line_numbers: list[int]) -> list[Node | Block]:
    while True:
        last_while_if_index = None
        lines_count = len(raw_body)

        for index in range(lines_count - 1, -1, -1):
            line = raw_body[index]
            if isinstance(line, list):
                if IF in line or WHILE in line:
                    last_while_if_index = index
                    break

        if last_while_if_index is None:
            break

        line = raw_body[last_while_if_index]
        line_number = line_numbers[last_while_if_index]

        operator, condition = __create_block_header(line, line_number)  # type: ignore
        if operator == IF:
            else_line_index, end_line_index = __find_end_else_indexes(raw_body,
                                                                      last_while_if_index,
                                                                      lines_count)

            else_block = None
            if else_line_index is not None:
                else_block = Block(ELSE, None, raw_body[else_line_index + 1:end_line_index],
                                   line_numbers[else_line_index])

            if end_line_index is None:
                raise SyntaxError(f'MISSING END TO MATCH EXPRESSION AT LINE {line_number}')

            if_block = Block(IF, condition, raw_body[last_while_if_index + 1:else_line_index],
                             line_number, else_block)

            raw_body = raw_body[:last_while_if_index] + raw_body[end_line_index + 1:]
            line_numbers = line_numbers[:last_while_if_index] + line_numbers[end_line_index + 1:]
            raw_body.insert(last_while_if_index, if_block)  # type: ignore
        else:
            for index in range(last_while_if_index, lines_count):
                line = raw_body[index]
                if isinstance(line, list) and END in line:
                    block_body = raw_body[last_while_if_index + 1:index]
                    raw_body = raw_body[:last_while_if_index] + raw_body[index + 1:]
                    line_numbers = line_numbers[:last_while_if_index] + line_numbers[index + 1:]

                    block = Block(WHILE, condition, block_body, line_number)
                    raw_body.insert(last_while_if_index, block)  # type: ignore
                    break

    return raw_body  # type: ignore

# endregion

# region Public functions

def parse_line(line: TokenList, line_number: int) -> Optional[Node]:
    """
    creates one full converted to nodes line of code
    if method can't parse line, raise a specific error

    :param line: array of tokens from one line of code
    :param line_number: number of line given for error handling
    :return:
    """
    if line is None or line_number < 1:
        return None

    if any(kwd in line for kwd in [WHILE, IF, ELSE, END]):
        return None

    line = __nest(line, line_number)

    if CREATE in line:
        __validate_is_syntax(line, line_number)
        return __create_variable_node(line, line_number)
    if RETURN in line:
        __validate_return_syntax(line, line_number)
        return __create_return_node(line, line_number)
    if BREAK in line:
        __validate_break_syntax(line, line_number)
        return __create_break_node(line_number)

    processed_line = __parse_helper(line, line_number, __parse_by,
                                    [ASSIGN, EQUALS, LESS_THAN, MORE_THAN,
                                     NO_LESS_THAN, NO_MORE_THAN])
    processed_line = __parse_helper(processed_line, line_number, __parse_calls, [PIPE])
    processed_line = __parse_helper(processed_line, line_number, __parse_by,
                                    [PLUS, MINUS])
    processed_line = __parse_helper(processed_line, line_number, __parse_by,
                                    [MULTIPLY, DIVIDE, MODULO])

    if isinstance(processed_line, Node):
        return processed_line

    raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: FAILED TO OPERATE LINE')

def parse_function(block: list[TokenList], line_numbers: list[int]) -> Function:
    """
    creates a function

    :param block: block of code to parse into function(including header)
    :param line_numbers: corresponding line numbers for each line
    """
    __validate_start_syntax(block[0], line_numbers[0])
    args, name = __parse_start(block[0], line_numbers[0])
    body: list[Node | TokenList] = []

    block = block[1:]
    line_numbers = line_numbers[1:]

    for line, line_number in zip(block, line_numbers):
        if isinstance(line, list):
            if any(kwd in line for kwd in [IF, ELSE, WHILE, END]):
                body.append(line)
                continue

        processed_line = parse_line(line, line_number)
        if processed_line is not None:
            body.append(processed_line)

    nested_body: list[Node | Block] = __nest_blocks(body, line_numbers)
    return Function(name, args, nested_body, line_numbers[0])


def parse(file_name: str) -> list[Function | Node]:
    """
    creates logical tree from code in .min file
    :param file_name: path to .min file to be processed
    :return: logical tree created
    """
    if file_name is None:
        raise FileNotFoundError()

    tree: list[Function | Node] = []
    tokens, line_numbers = get_tokens(file_name)

    nested = 0
    in_function_body = False

    body: list[TokenList] = []
    body_line_numbers: list[int] = []

    tokens_count = len(tokens)
    for index in range(tokens_count):
        line = tokens[index]
        line_number = line_numbers[index]

        if in_function_body:
            if START in line:
                raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}:' +
                                  ' CAN NOT ASSIGN FUNCTION IN FUNCTION\'S BODY')

            if IF in line or WHILE in line:
                nested += 1
            if END in line:
                nested -= 1

            body.append(line)
            body_line_numbers.append(line_number)
        else:
            if USE in line:
                __validate_use_syntax(line, line_number)
                tree.append(__create_use_node(line, line_number))

            if START in line:
                body = [line]
                body_line_numbers = [line_number]

                nested += 1
                in_function_body = True

            if any(kwd in line for kwd in [IF, ELSE, WHILE, END]):
                raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: ' +
                                  'CAN NOT USE KEYWORD OUTSIDE OF FUNCTION\'S BODY')

        if nested == 0 and in_function_body:
            in_function_body = False

            function = parse_function(body, body_line_numbers)

            if not isinstance(function, Function):
                raise SyntaxError(f'INVALID SYNTAX AT LINE {line_number}: ' +
                                  'BLOCK IS NOT RECOGNIZED AS FUNCTION')

            tree.append(function)

    tree = __extract_inlist_tokens_from_tree(tree)
    return tree


def print_tree(file_name: str) -> None:
    """
    outputs logical tree created from code in .min file
    :param file_name: path to .min file to be processed
    """
    print("Produced tree:")

    pprint(parse(file_name),
           width=140)

    print("-" * 70)

# endregion
