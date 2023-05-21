"""
This module executes logical tree created in parser.
Interpreter does it line by line.

Interpreter handles runtime errors such as invalid types, missing
parameters, wrong casting, mathematical errors and so on

Run '$python interpreter.py --help' to see more usage instructions, or use
as module 'from interpreter import execute'
"""

# region Imported modules

import os
import importlib.util
import copy

from typing import Callable, Optional, Any

from .lexer import print_tokens
from .min_parser import parse, print_tree
from .utils.structures import Token, Node, Function
from .utils.commons import PyFunction, CallablesList, VariablesList, ExecutionResult
from .utils.commons import COMMA, PLUS, MINUS, DIVIDE, MULTIPLY, MODULO, ASSIGN, CREATE
from .utils.commons import RETURN, PIPE, USE

# endregion

# region Private functions

def __unpack_var(token: Token, line_number: int, nesting_level: int,
                 visible_variables: VariablesList) -> Token:
    """
    if given is a variable returns stored value, otherwise does nothing

    :param token: given Token
    :param nesting_level: current nesting level
    :param line_number: number of current line for error handling
    :param visible_variables: pool of variables visible in current nesting level
    :return: stored value or token itself
    """
    if token.type == 'var':
        found = False

        for index in range(nesting_level):
            if token.value in visible_variables[index].keys():
                token = visible_variables[index][token.value]
                found = True

        if not found:
            raise RuntimeError(f'VARIABLE {token.value} UNDECLARED AT LINE {line_number}')

    return token

def __execute_separator_block(expression: Node,
                              line_number: int, nesting_level: int,
                              visible_variables: VariablesList) -> tuple[list[Token], bool]:
    """
    merges two separated operands to array of operands

    :param expression: array in form of [operand] [operation] [operand]
    :param nesting_level: current nesting level
    :param line_number: number of current line for error handling
    :param visible_variables: pool of variables visible in current nesting level
    :return: array of Tokens
    """
    left: Token = expression.left
    right: Token = expression.right

    args: list = []
    if isinstance(left, list):
        args += left
    else:
        left = __unpack_var(left, line_number, nesting_level, visible_variables)
        args.append(left)

    if isinstance(right, list):
        args += right
    else:
        right = __unpack_var(right, line_number, nesting_level, visible_variables)
        args.append(right)

    return args, True
def __execute_arithmetical_block(expression: Node,
                                 line_number: int, nesting_level: int,
                                 visible_variables: VariablesList) -> ExecutionResult:
    """
    executes processed [operand] [operation] [operand]-like block of code
    if none of known operators present raises a runtime error
    if any of types doesn't match raises a runtime error

    :param expression: array in form of [operand] [operation] [operand]
    :param nesting_level: current nesting level
    :param line_number: number of current line for error handling
    :param visible_variables: pool of variables visible in current nesting level
    :return: (execution_result, function_still_running)
    """
    left: Token = expression.left
    right: Token = expression.right
    operator: Token = expression.operator

    left = __unpack_var(left, line_number, nesting_level, visible_variables)
    right = __unpack_var(right, line_number, nesting_level, visible_variables)

    if not isinstance(left.value, (int, float)) or not isinstance(right.value, (int, float)):
        raise RuntimeError(f'UNABLE TO RECOGNIZE TYPE OF VARIABLES AT LINE {line_number}')

    if left.type not in 'int float' or right.type not in 'int float':
        raise RuntimeError(f'COMPILATION ERROR AT LINE {line_number}: OPERANDS SUPPOSED TO '
                           f'BE OF TYPE int OR float, GOT {left.type} AND {right.type}')

    result: float | int
    if operator == PLUS:
        result = left.value + right.value
    elif operator == MINUS:
        result = left.value - right.value
    elif operator == MULTIPLY:
        result = left.value * right.value
    elif operator == DIVIDE:
        if right.value == 0:
            raise RuntimeError(f'ZERO-DIVISION ERROR AT LINE {line_number}')

        result = left.value / right.value
    elif operator == MODULO:
        result = left.value % right.value
    else:
        raise RuntimeError(f'UNKNOWN IDENTIFIER ERROR AT LINE {line_number}')

    new_type = 'int' if int(result) == result else 'float'
    return Token(new_type, result), True

def __execute_var_related_block(expression: Node,
                                line_number: int, nesting_level: int,
                                visible_variables: VariablesList) -> ExecutionResult:
    """
    executes operations of variable creation and assigning

    :param expression: array in form of [operand] [operation] [operand]
    :param nesting_level: current nesting level
    :param line_number: number of current line for error handling
    :param visible_variables: pool of variables visible in current nesting level
    :return: (execution_result, function_still_running)
    """
    left: Token = expression.left
    right: Token = expression.right
    operator = expression.operator

    if operator == CREATE:
        # type check
        if right.type == 'typ' and left.type == 'var':
            if nesting_level not in visible_variables.keys():
                visible_variables[nesting_level] = {}

            # conflicting variables
            for index in range(nesting_level):
                if left.value in visible_variables[index].keys():
                    raise RuntimeError(f'COMPILATION ERROR AT LINE {line_number}: ' +
                                       'REDECLARATION OF A VARIABLE')

            if right.value == 'str':
                visible_variables[nesting_level][left.value] = Token('str', '')
            elif right.value == 'bool':
                visible_variables[nesting_level][left.value] = Token('bool', False)
            else:
                visible_variables[nesting_level][left.value] = Token(right.type, 0)

            return None, True

        raise RuntimeError(f'COMPILATION ERROR AT LINE {line_number}: ' +
                           'WRONG IS OPERATOR USAGE')
    if operator == ASSIGN:
        var_name = left.value
        type_ = visible_variables[nesting_level][var_name][1]

        right = __unpack_var(right, line_number, nesting_level, visible_variables)

        # type check
        if right.type == type_:
            visible_variables[nesting_level][var_name] = right
            return None, True

        raise RuntimeError(f'COMPILATION ERROR AT LINE {line_number}: {var_name} IS ' +
                           f'TYPE OF {type_} BUT ASSIGNED VALUE IS TYPE OF {right.type}')

    return None, True

def __execute_func_related_block(expression: list[Token | list[Token]],
                                 line_number: int, nesting_level: int,
                                 visible_variables: VariablesList,
                                 callables: CallablesList) -> ExecutionResult:
    """
    executes operations function calling, function returning

    :param expression: array in form of [operand] [operation] [operand]
    :param nesting_level: current nesting level
    :param line_number: number of current line for error handling
    :param visible_variables: pool of variables visible in current nesting level
    :param callables: functions pool in program
    :return: (execution_result, function_still_running)
    """
    if not isinstance(expression[0], Token) or \
            not isinstance(expression[2], list) or \
            not isinstance(expression[1], Token):
        raise RuntimeError('FAILED TO USE PIPE OPERATOR ON WRONG OPERANDS' +
                           f'AT LINE {line_number}')

    left: Token = expression[0]
    right: list[Token] = expression[2]
    operator: Token = expression[1]

    if operator == PIPE:
        if left.value in callables.keys():
            if isinstance(left.value, str) and isinstance(right, list):
                return execute_function(left.value, callables, right), True

            raise RuntimeError('CANNOT EXECUTE FUNCTION WITH NON-STRING NAME ' +
                               f'AT LINE {line_number}')

        raise RuntimeError(f'COMPILATION ERROR AT LINE {line_number}: FUNCTION {left.value} ' +
                           'IS NOT FOUND')
    if operator == RETURN:
        if right is None:
            return None, False

        if isinstance(right, dict):
            return_, _ = execute_line(right, callables, nesting_level,
                                      line_number, visible_variables)

            return return_, False

        raise RuntimeError(f'NOT PROCESSABLE RETURN AT LINE {line_number}')

    return None, True


def __validate_args(args: list[Token], args_needed: list[str], function_name: str) -> None:
    """
    checks if arguments fit to function
    raises error if not

    :param args: arguments, that are passed
    :param args_needed: arguments, that are needed (and acceptable)
    :param function_name: function for which arguments are checked
    """
    args_count_needed = len(args_needed)
    args_count = len(args)

    if args_count_needed == args_count:
        for index in range(args_count):
            token = args[index]

            if token.type not in args_needed[index]:
                raise RuntimeError(f'COMPILATION ERROR: FUNCTION {function_name} EXPECTS ' +
                                   f'{args_needed[index]} AS A PARAMETER BUT {token.type} GIVEN')
    else:
        raise RuntimeError(f'COMPILATION ERROR: FUNCTION {function_name} REQUIRES ' +
                           f'{len(args_needed)} ARGUMENTS BUT {len(args)} GIVEN')


def __execute_py_function(function_name: str, packed_function: PyFunction,
                          args: list[Token]) -> Optional[Token]:
    """
    execute python built-in function

    :param function_name: function to be executed
    :param packed_function: function to execute
    :param args: arguments which are passed to the function
    :return: return of function, if exists
    """
    args_needed: list[str] = []
    if isinstance(packed_function[1], list):
        args_needed = packed_function[1]

    if callable(packed_function[0]):
        function: Callable = packed_function[0]

        __validate_args(args, args_needed, function_name)

        args_values: list[float | int | str | bool] = []

        args_count = len(args_needed)
        for index in range(args_count):
            token: Token = args[index]
            args_values.append(token.value)

        return function(args_values)

    return None


def __execute_min_function(function_name: str, function: Function, args: list,
                           callables: CallablesList) -> Optional[Token]:
    """
    execute function line by line

    :param function_name: function to be executed
    :param function: function to execute
    :param args: arguments which are passed to the function
    :param callables: global pool of functions in program
    :return: return of function, if exists
    """
    visible_variables: VariablesList = {}

    args_count = len(function.args)
    for index in range(args_count):
        line = function.args[index]
        execute_line(line, callables, 0, function.line_number, visible_variables)

        visible_variables[0][function.args[index].left.value] = args[index]

    args_needed: list[str] = list(map(lambda argument: argument.right.value, function.args))

    __validate_args(args, args_needed, function_name)

    for line in function.body:
        response, running = execute_line(copy.deepcopy(line), callables, 0,
                                         line.line_number, visible_variables)

        if not running:
            if isinstance(response, Token):
                return response

            raise RuntimeError(f'NOT PROCESSABLE RETURN IN FUNC {function_name} ' +
                               f'AT LINE {line.line_number}')

    return None


def __find_callables(tree: list[Function | Node]) -> CallablesList:
    """
        fills functions_list, which are either Python callables from
        imported libraries or MINIMUM functions

        :param tree: code tree made on base of given file with min_parser.py
        :return: returns dictionary of functions:
        {'function_name': *either Python callable or MINIMUM code block*, ...}
    """

    callables: CallablesList = {}
    for block in tree:
        if isinstance(block, Function):
            callables[block.name] = block
        elif isinstance(block, Node) and block.operator == USE:
            root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
            path = root_directory + '/libraries/' + block.right + '.py'
            spec = importlib.util.spec_from_file_location(block.right, path)

            if spec is None or spec.loader is None:
                raise RuntimeError(f'UNABLE TO READ/FIND LIBRARY {block.right} ' +
                                   f'AT LINE {block.line_number}')

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            methods = module.get_methods()

            for method in methods:
                name = method[0]
                callable_ = method[1]
                args = method[2]

                callables[name] = [callable_, args]

    return callables

# endregion

# region Public functions

def execute_line(line: Node | Token, callables: CallablesList,
                 nesting_level: int, line_number: int,
                 visible_variables: VariablesList) -> tuple[Any, bool]:
    """
    executes single line of code

    :param line: nested and processed line of code
    :param callables: functions pool in program
    :param nesting_level: current nesting level
    :param line_number: number of current line for error handling
    :param visible_variables: pool of variables visible in current nesting level
    :return: (execution_result, function_still_running)
    """
    # the simplest case
    if isinstance(line, Token):
        return line, True

    right = line.right
    left = line.left

    right, _ = execute_line(right, callables, nesting_level,
                            line_number, visible_variables)
    left, _ = execute_line(left, callables, nesting_level,
                           line_number, visible_variables)

    if line.operator in [CREATE, ASSIGN]:
        return __execute_var_related_block(Node(line.operator, line_number, right, left),
                                           line_number, nesting_level, visible_variables)
    if line.operator in [PIPE, RETURN]:
        return __execute_func_related_block([left, line.operator, right],
                                            line_number, nesting_level, visible_variables,
                                            callables)
    if line.operator == COMMA:
        return __execute_separator_block(Node(line.operator, line_number, right, left),
                                         line_number, nesting_level, visible_variables)

    return __execute_arithmetical_block(Node(line.operator, line_number, right, left),
                                        line_number, nesting_level, visible_variables)


def execute_function(function_name: str, callables: CallablesList, args: list) -> Optional[Token]:
    """
    executes either min or py function

    :param function_name: function to be executed
    :param callables: global pool of functions in program
    :param args: arguments which are passed to the function
    :return: return of function, if exists
    """
    function: PyFunction | Function = callables[function_name]

    if isinstance(function, Function):
        return __execute_min_function(function_name, function, args,
                                      callables)

    return __execute_py_function(function_name, function, args)


def execute(file_name: str):
    """
    executes given code, starting from 'main' function
    raises an error is there is no 'main' function

    :param file_name: name of .min file to be executed
    """
    tree: list[Function | Node] = parse(file_name)

    callables: CallablesList = __find_callables(tree)

    functions = callables.keys()
    if 'main' in functions:
        execute_function('main', callables, [])
    else:
        raise RuntimeError("COMPILATION ERROR: 'main' FUNCTION NOT FOUND")


def print_code(file_name: str):
    """
    outputs code given in .min file

    :param file_name: name of .min file to be read
    """
    print('Executed code:')
    file = open(file_name, 'r')

    lines: list[str] = file.readlines()

    max_len: int = len(lines[0])
    for line in lines:
        max_len = max(max_len, len(line))
        print(line, end=('' if line[-1] == '\n' else '\n'))

    file.close()

    print("-" * (max_len + 1))

# endregion