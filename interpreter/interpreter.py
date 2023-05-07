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
import sys
import importlib.util
import copy

from typing import Any, Callable

from lexer import print_tokens
from min_parser import parse, print_tree
from structures import Token
from commons import CallablePacked, CallablesList, VariablesList, ExecutionResult

# endregion

# region Private functions

def execute_arithmetical_block(expression: list[Token],
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
    left = expression[0]
    right = expression[2]

    type_left = left[1]
    operation = expression[1]
    type_right = right[1]
    # type check

    if type_left == 'var':
        for index in range(1, nesting_level + 1):
            if left[0] in visible_variables[index].keys():
                left = visible_variables[index][left[0]]
                type_left = left[1]

    if type_right == 'var':
        for index in range(1, nesting_level + 1):
            if right[0] in visible_variables[index].keys():
                right = visible_variables[index][right[0]]
                type_right = right[1]

    if not isinstance(type_left, str) or not isinstance(type_right, str) or \
       not isinstance(left[0], (int, float)) or not isinstance(right[0], (int, float)):
        raise RuntimeError(f'UNABLE TO RECOGNIZE TYPE OF VARIABLES AT LINE {line_number}')

    if not operation == [',', 'sep']:
        if type_left not in 'int float' or type_right not in 'int float':
            raise RuntimeError(f'COMPILATION ERROR AT LINE {line_number}: OPERANDS SUPPOSED TO '
                               f'BE OF TYPE int OR float, GOT {type_left} AND {type_right}')

    match operation:
        case ['+', 'opr']:
            result = left[0] + right[0]
            new_type = 'int' if type_left != 'float' and type_right != 'float' else 'float'
            return [result, new_type], True
        case ['-', 'opr']:
            result = left[0] - right[0]
            new_type = 'int' if type_left != 'float' and type_right != 'float' else 'float'
            return [result, new_type], True
        case ['*', 'opr']:
            result = left[0] * right[0]
            new_type = 'int' if type_left != 'float' and type_right != 'float' else 'float'
            return [result, new_type], True
        case ['/', 'opr']:
            if right[0] != 0:
                result = left[0] / right[0]
                new_type = 'int' if type_left != 'float' and type_right != 'float' else 'float'
                return [result, new_type], True

            raise RuntimeError(f'ZERO-DIVISION ERROR AT LINE {line_number}')
        case ['%', 'opr']:
            result = left[0] % right[0]
            new_type = 'int' if type_left != 'float' and type_right != 'float' else 'float'
            return [result, new_type], True
        case [',', 'sep']:
            args: list = []
            match isinstance(left[0], str):
                case True:
                    args += left
                case False:
                    args.append(left)

            match isinstance(right[0], str):
                case True:
                    args += right
                case False:
                    args.append(right)

            return args, True
        case _:
            raise RuntimeError(f'UNKNOWN IDENTIFIER ERROR AT LINE {line_number}')


def execute_var_related_block(expression: list[Token | dict | list],
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
    left = expression[0]
    right = expression[2]

    match expression[1]:
        case ['is', 'opr']:
            # type check
            if right[1] == 'typ':
                if left[1] == 'var':
                    if nesting_level not in visible_variables.keys():
                        visible_variables[nesting_level] = {}

                    # conflicting variables
                    if left[0] not in visible_variables[nesting_level].keys():
                        visible_variables[nesting_level][left[0]] = [0, right[0]]

                        if right[0] == 'str':
                            visible_variables[nesting_level][left[0]][0] = ''
                        elif right[0] == 'bool':
                            visible_variables[nesting_level][left[0]][0] = False

                        return None, True

                    raise RuntimeError(f'COMPILATION ERROR AT LINE {line_number}: ' +
                                       'REDECLARATION OF A VARIABLE')
        case ['=', 'opr']:
            var_name = left[0]
            type_ = visible_variables[nesting_level][var_name][1]

            if right[1] == 'var':
                for index in range(1, nesting_level + 1):
                    if right[0] in visible_variables[index].keys():
                        right = visible_variables[index][right[0]]

            # type check
            if right[1] == type_:
                visible_variables[nesting_level][var_name][0] = right[0]
                return None, True

            raise RuntimeError(f'COMPILATION ERROR AT LINE {line_number}: {var_name} IS ' +
                               f'TYPE OF {type_} BUT ASSIGNED VALUE IS TYPE OF {right[1]}')

    return None, True


def execute_func_related_block(expression: list[Token | dict | list],
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
    left = expression[0]
    right = expression[2]

    match expression[1]:
        case ['|', 'opr']:
            args_count = len(right)
            for arg_index in range(args_count):
                current_arg = right[arg_index]
                if isinstance(current_arg, list):
                    arg: Token = current_arg

                    if arg[1] != 'var':
                        continue

                    for index in range(1, nesting_level + 1):
                        if arg[0] in visible_variables[index].keys():
                            right[arg_index] = visible_variables[index][arg[0]]

            if left[0] in callables.keys():
                if isinstance(left[0], str) and isinstance(right, list):
                    return execute_function(left[0], callables, right), True

                raise RuntimeError('CANNOT EXECUTE FUNCTION WITH NON-STRING NAME ' +
                                   f'AT LINE {line_number}')

            raise RuntimeError(f'COMPILATION ERROR AT LINE {line_number}: FUNCTION {left[0]} ' +
                               'IS NOT FOUND')
        case ['return', 'kwd']:
            if right is None:
                return None, False

            if isinstance(right, dict):
                return_, _ = execute_line(right, callables, nesting_level,
                                          line_number, visible_variables)

                return return_, False

            raise RuntimeError(f'NOT PROCESSABLE RETURN AT LINE {line_number}')

    return None, True


def validate_args(args: list, args_needed: list, function_name: str) -> None:
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
            type_ = token[1]

            types_available = args_needed[index]
            if type_ not in types_available:
                raise RuntimeError(f'COMPILATION ERROR: FUNCTION {function_name} EXPECTS ' +
                                   f'{types_available} AS A PARAMETER BUT {type_} GIVEN')
    else:
        raise RuntimeError(f'COMPILATION ERROR: FUNCTION {function_name} REQUIRES ' +
                           f'{len(args_needed)} ARGUMENTS BUT {len(args)} GIVEN')


def execute_py_function(function_name: str, packed_function: CallablePacked,
                        args: list) -> list | None:
    """
    execute python built-in function

    :param function_name: function to be executed
    :param packed_function: function to execute
    :param args: arguments which are passed to the function
    :return: return of function, if exists
    """
    args_needed_py_func: list = []
    if isinstance(packed_function[1], list):
        args_needed_py_func = packed_function[1]

    if callable(packed_function[0]):
        function: Callable = packed_function[0]

        validate_args(args, args_needed_py_func, function_name)

        args_count = len(args_needed_py_func)
        args_values: list[float | int | str] = []

        for index in range(args_count):
            token = args[index]
            type_ = token[1]

            match type_:
                case 'int':
                    args_values.append(int(token[0]))
                case 'float':
                    args_values.append(float(token[0]))
                case 'str':
                    args_values.append(token[0])
                case 'bool':
                    args_values.append(token[0] == 'true')

        return function(args_values)

    return None


def execute_min_function(function_name: str, function: dict, args: list, callables: CallablesList,
                         visible_variables: VariablesList) -> list | None:
    """
    execute function line by line

    :param function_name: function to be executed
    :param function: function to execute
    :param args: arguments which are passed to the function
    :param callables: global pool of functions in program
    :param visible_variables: current pool of variables available
    :return: return of function, if exists
    """
    for index in range(len(function['args'])):
        line = function['args'][index]
        execute_line(line, callables, 1, function['line'], visible_variables)

        argument = args[index][0]
        visible_variables[1][function['args'][index]['left'][0]][0] = argument

    args_needed_min_func = function['args']
    args_needed_min_func = list(map(lambda arg: arg['right'][0], args_needed_min_func))

    validate_args(args, args_needed_min_func, function_name)

    for line in function['body']:
        line_number: int = line['line']
        response, running = execute_line(copy.deepcopy(line), callables, 1,
                                         line_number, visible_variables)

        if not running:
            if isinstance(response, list):
                return response

            raise RuntimeError(f'NOT PROCESSABLE RETURN IN FUNC {function_name} ' +
                               f'AT LINE {line_number}')

    return None


def find_callables(tree: list) -> CallablesList:
    """
        fills functions_list, which are either Python callables from
        imported libraries or MINIMUM functions

        :param tree: code tree made on base of given file with min_parser.py
        :return: returns dictionary of functions:
        {'function_name': *either Python callable or MINIMUM code block*, ...}
    """
    callables: CallablesList = {}
    for block in tree:
        if 'body' in block.keys():
            callables[block['name']] = {
                'body': block['body'],
                'args': block['args'],
                'line': block['line']
            }
        elif 'operation' in block.keys() and block['operation'] == 'use':
            root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
            path = root_directory + '/libraries/' + block['right'] + '.py'
            spec = importlib.util.spec_from_file_location(block['right'], path)

            if spec is None or spec.loader is None:
                raise RuntimeError(f'UNABLE TO READ/FIND LIBRARY {block["right"]} ' +
                                   f'AT LINE {block["line"]}')

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

def execute_line(line: dict[str, Any], callables: CallablesList,
                 nesting_level: int, line_number: int,
                 visible_variables: VariablesList) -> ExecutionResult:
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
    if isinstance(line, list):
        return line, True

    right = line['right']
    left = line['left']

    right, _ = execute_line(right, callables, nesting_level,
                            line_number, visible_variables)
    left, _ = execute_line(left, callables, nesting_level,
                           line_number, visible_variables)

    if line['operation'] in [['is', 'opr'], ['=', 'opr']]:
        return execute_var_related_block([left, line['operation'], right], line_number,
                                         nesting_level, visible_variables)
    if line['operation'] in [['|', 'opr'], ['return', 'kwd']]:
        return execute_func_related_block([left, line['operation'], right], line_number,
                                          nesting_level, visible_variables, callables)

    return execute_arithmetical_block([left, line['operation'], right], line_number,
                                      nesting_level, visible_variables)


def execute_function(function_name: str, callables: CallablesList, args: list) -> list | None:
    """
    executes either min or py function

    :param function_name: function to be executed
    :param callables: global pool of functions in program
    :param args: arguments which are passed to the function
    :return: return of function, if exists
    """
    visible_variables: VariablesList = {}

    packed_function: CallablePacked | dict = callables[function_name]

    if isinstance(packed_function, dict):
        return execute_min_function(function_name, packed_function, args,
                                    callables, visible_variables)

    return execute_py_function(function_name, packed_function, args)


def execute(file_name: str):
    """
    executes given code, starting from 'main' function
    raises an error is there is no 'main' function

    :param file_name: name of .min file to be executed
    """
    tree: list = parse(file_name)

    callables: CallablesList = find_callables(tree)

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


if __name__ == '__main__':
    # do not output errors traceback from Python
    sys.tracebacklimit = -1

    try:
        FIRST_ARG = sys.argv[1]

        if FIRST_ARG == '--help':
            print('Usage: python interpreter.py [filename] [flag1] [flag2] ...')
            print('Flags available:')
            print('\t-c - show executed code')
            print('\t-l - shot lexer result (raw tokens)')
            print('\t-p - show parser result (code tree)')
        else:
            available_flags = ['-p', '-c', '-l']
            flags = sys.argv[2:]

            unknown_token = any(flag for flag in flags if flag not in available_flags)

            if unknown_token:
                print('Unknown token: Try typing interpreter.py --help to see usage info')
            else:
                if '-c' in flags:
                    print_code(FIRST_ARG)

                if '-l' in flags:
                    print_tokens(FIRST_ARG)

                if '-p' in flags:
                    print_tree(FIRST_ARG)
                print("Produced output:")
                execute(FIRST_ARG)
    except (FileNotFoundError, IndexError):
        print('Try typing interpreter.py --help to see usage info')
