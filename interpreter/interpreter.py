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

from typing import Any

from parser import make_tree, print_tree
from lexer import print_tokens

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

# do not output errors traceback from Python
sys.tracebacklimit = -1

# ON DEBUG
# from pprint import pprint

# region Private functions

def execute_line(line, callables, nesting_level, line_number, visible_variables):
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

    right, ended_right = execute_line(right, callables, nesting_level,
                                      line_number, visible_variables)
    left, ended_left = execute_line(left, callables, nesting_level,
                                    line_number, visible_variables)

    if line['operation'] == ['is', 'opr']:
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
                else:
                    raise Exception(f'COMPILATION ERROR AT LINE {line_number}: ' +
                                    'REDECLARATION OF A VARIABLE')
    elif line['operation'] in [['=', 'opr'], ['|', 'opr']]:
        if line['operation'] == ['=', 'opr']:
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
            else:
                raise Exception(f'COMPILATION ERROR AT LINE {line_number}: {var_name} IS ' +
                                f'TYPE OF {type_} BUT ASSIGNED VALUE IS TYPE OF {right[1]}')
        elif line['operation'] == ['|', 'opr']:
            for arg_index in range(len(right)):
                arg = right[arg_index]
                if arg[1] == 'var':
                    for index in range(1, nesting_level + 1):
                        if arg[0] in visible_variables[index].keys():
                            right[arg_index] = visible_variables[index][arg[0]]

            if left[0] in callables.keys():
                return execute_function(left[0], callables, right), True
            else:
                raise Exception(f'COMPILATION ERROR AT LINE {line_number}: FUNCTION {left[0]} ' +
                                'IS NOT FOUND')
        elif line['operation'] == ['return', 'kwd']:
            if line['right'] is None:
                return None, False

            return_ = execute_line(line['right'], callables, nesting_level,
                                   line_number, visible_variables)

            return return_, False
    else:
        # type check
        type_left = left[1]
        type_right = right[1]

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

        if not line['operation'] == [',', 'sep']:
            if type_left not in 'int float' or type_right not in 'int float':
                raise Exception(f'COMPILATION ERROR AT LINE {line_number}: OPERANDS SUPPOSED TO '
                                f'BE OF TYPE int OR float, GOT {type_left} AND {type_right}')

        if line['operation'] == ['+', 'opr']:
            sum_ = left[0] + right[0]
            new_type = 'int' if type_left != 'float' and type_right != 'float' else 'float'
            return [sum_, new_type], True
        elif line['operation'] == ['-', 'opr']:
            difference = left[0] - right[0]
            new_type = 'int' if type_left != 'float' and type_right != 'float' else 'float'
            return [difference, new_type], True
        elif line['operation'] == ['*', 'opr']:
            product = left[0] * right[0]
            new_type = 'int' if type_left != 'float' and type_right != 'float' else 'float'
            return [product, new_type], True
        elif line['operation'] == ['/', 'opr']:
            if right[0] != 0:
                quotient = left[0] / right[0]
                new_type = 'int' if type_left != 'float' and type_right != 'float' else 'float'
                return [quotient, new_type], True
            else:
                raise Exception(f'ZERO-DIVISION ERROR AT LINE {line_number}')
        elif line['operation'] == ['%', 'opr']:
            modulo = left[0] % right[0]
            new_type = 'int' if type_left != 'float' and type_right != 'float' else 'float'
            return [modulo, new_type], True
        elif line['operation'] == [',', 'sep']:
            args = []
            if isinstance(left[0], str):
                args += left
            else:
                args.append(left)

            if isinstance(right[0], str):
                args += right
            else:
                args.append(right)

            return args, True
        else:
            raise Exception(f'UNKNOWN IDENTIFIER ERROR AT LINE {line_number}')


def validate_args(args, args_needed, function_name):
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
                raise Exception(f'COMPILATION ERROR: FUNCTION {function_name} EXPECTS ' +
                                f'{types_available} AS A PARAMETER BUT {type_} GIVEN')
    else:
        raise Exception(f'COMPILATION ERROR: FUNCTION {function_name} REQUIRES ' +
                        f'{len(args_needed)} ARGUMENTS BUT {len(args)} GIVEN')


def execute_function(function_name, callables, args):
    """
    execute function line by line

    :param function_name: function to be executed
    :param callables: global pool of functions in program
    :param args: arguments which are passed to the function
    :return: return of function, if exists
    """
    visible_variables = {}

    if isinstance(callables[function_name], dict):
        for index in range(len(callables[function_name]['args'])):
            line = callables[function_name]['args'][index]
            execute_line(line, callables, 1, callables[function_name]['line'], visible_variables)

            argument = args[index][0]
            visible_variables[1][callables[function_name]['args'][index]['left'][0]][0] = argument

        args_needed = callables[function_name]['args']
        args_needed = list(map(lambda arg: arg['right'][0], args_needed))

        validate_args(args, args_needed, function_name)

        for line in callables[function_name]['body']:
            line_number = line['line']
            response, running = execute_line(copy.deepcopy(line), callables, 1,
                                             line_number, visible_variables)

            if not running:
                return response

        return None
    else:
        args_needed = callables[function_name][1]
        function = callables[function_name][0]

        validate_args(args, args_needed, function_name)

        args_count = len(args_needed)
        args_values = []

        for index in range(args_count):
            token = args[index]
            type_ = token[1]

            if type_ == 'int':
                args_values.append(int(token[0]))
            elif type_ == 'float':
                args_values.append(float(token[0]))
            elif type_ == 'str':
                args_values.append(token[0])
            elif type_ == 'bool':
                args_values.append(token[0] == 'true')

        return function(args_values)


def find_callables(tree):
    """
        fills functions_list, which are either Python callables from
        imported libraries or MINIMUM functions

        :param tree: code tree made on base of given file with parser.py
        :return: returns dictionary of functions:
        {'function_name': *either Python callable or MINIMUM code block*, ...}
    """
    callables = {}
    for block in tree:
        if 'body' in block.keys():
            callables[block['name']] = {
                'body': block['body'],
                'args': block['args'],
                'line': block['line']
            }
            pass
        elif 'operation' in block.keys() and block['operation'] == 'use':
            root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
            path = root_directory + '/libraries/' + block['right'] + '.py'
            spec = importlib.util.spec_from_file_location(block['right'], path)

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
def execute(file_name):
    """
    executes given code, starting from 'main' function
    raises an error is there is no 'main' function

    :param file_name: name of .min file to be executed
    """
    tree = make_tree(file_name)

    callables = find_callables(tree)

    if 'main' in callables.keys():
        execute_function('main', callables, [])
    else:
        raise Exception("COMPILATION ERROR: 'main' FUNCTION NOT FOUND")


def print_code(file_name):
    """
    outputs code given in .min file

    :param file_name: name of .min file to be read
    """
    print('Executed code:')
    file = open(file_name, 'r')

    lines = file.readlines()

    max_len = len(lines[0])
    for line in lines:
        max_len = max(max_len, len(line))
        print(line, end=('' if line[-1] == '\n' else '\n'))

    file.close()

    print("-" * (max_len + 1))

# endregion


if __name__ == '__main__':
    try:
        first_arg = sys.argv[1]

        if first_arg == '--help':
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
                    print_code(first_arg)

                if '-l' in flags:
                    print_tokens(first_arg)

                if '-p' in flags:
                    print_tree(first_arg)
                print("Produced output:")
                execute(first_arg)
    except (FileNotFoundError, IndexError):
        print('Try typing interpreter.py --help to see usage info')
