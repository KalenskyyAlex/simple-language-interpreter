import os

from parser import make_tree, print_tree
from lexer import print_tokens
import sys
import importlib.util

# ON DEBUG
# from pprint import pprint

def execute_line(line, callables, nesting_level, line_number):
    global visible_variables
    if isinstance(line, list):
        return line, True
    # the simplest case
    else:
        right = line['right']
        left = line['left']

        right, success_right = execute_line(right, callables, nesting_level, line_number)
        left, success_left = execute_line(left, callables, nesting_level, line_number)

        if not success_right or not success_left:
            return None, False

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
                        print('COMPILATION ERROR AT LINE', line_number, ': REDECLARATION OF A VARIABLE')
                        return None, False
        elif line['operation'] == ['=', 'opr']:
            var_name = left[0]
            type_ = visible_variables[nesting_level][var_name][1]

            if type_ == 'var':
                for index in range(1, nesting_level + 1):
                    if right[0] in visible_variables[index].keys():
                        right = visible_variables[index][right[0]]

            # type check
            if right[1] == type_:
                visible_variables[nesting_level][var_name][0] = right[0]
                return None, True
            else:
                print('COMPILATION ERROR AT LINE', line_number, ':', var_name, 'IS TYPE OF', type_,
                      'BUT ASSIGNED VALUE IS TYPE OF', right[1])
                return None, False
        elif line['operation'] == ['+', 'opr']:
            # type check
            type_left = left[1]
            type_right = right[1]

            if type_left == 'var':
                for index in range(1, nesting_level + 1):
                    if left[0] in visible_variables[index].keys():
                        left = visible_variables[index][left[0]]
            if type_right == 'var':
                for index in range(1, nesting_level + 1):
                    if right[0] in visible_variables[index].keys():
                        right = visible_variables[index][right[0]]

            if type_left in 'int float' and type_right in 'int float':
                sum_ = left[0] + right[0]
                new_type = 'int' if type_left != 'float' and type_right != 'float' else 'float'
                return [sum_, new_type], True
            else:
                print('COMPILATION ERROR AT LINE', line_number, ': OPERANDS SUPPOSED TO BE OF TYPE int OR float, GOT',
                      type_left, 'AND', type_right)
                return None, False
        elif line['operation'] == ['-', 'opr']:
            type_left = left[1]
            type_right = right[1]

            if type_left == 'var':
                for index in range(1, nesting_level + 1):
                    if left[0] in visible_variables[index].keys():
                        left = visible_variables[index][left[0]]
            if type_right == 'var':
                for index in range(1, nesting_level + 1):
                    if right[0] in visible_variables[index].keys():
                        right = visible_variables[index][right[0]]

            if type_left in 'int float' and type_right in 'int float':
                difference = left[0] - right[0]
                new_type = 'int' if type_left != 'float' and type_right != 'float' else 'float'
                return [difference, new_type], True
            else:
                print('COMPILATION ERROR AT LINE', line_number, ': OPERANDS SUPPOSED TO BE OF TYPE int OR float, GOT',
                      type_left, 'AND', type_right)
                return None, False
        elif line['operation'] == ['*', 'opr']:
            type_left = left[1]
            type_right = right[1]

            if type_left == 'var':
                for index in range(1, nesting_level + 1):
                    if left[0] in visible_variables[index].keys():
                        left = visible_variables[index][left[0]]
            if type_right == 'var':
                for index in range(1, nesting_level + 1):
                    if right[0] in visible_variables[index].keys():
                        right = visible_variables[index][right[0]]

            if type_left in 'int float' and type_right in 'int float':
                product = left[0] * right[0]
                new_type = 'int' if type_left != 'float' and type_right != 'float' else 'float'
                return [product, new_type], True
            else:
                print('COMPILATION ERROR AT LINE', line_number, ': OPERANDS SUPPOSED TO BE OF TYPE int OR float, GOT',
                      type_left, 'AND', type_right)
                return None, False
        elif line['operation'] == ['/', 'opr']:
            type_left = left[1]
            type_right = right[1]

            if type_left == 'var':
                for index in range(1, nesting_level + 1):
                    if left[0] in visible_variables[index].keys():
                        left = visible_variables[index][left[0]]
            if type_right == 'var':
                for index in range(1, nesting_level + 1):
                    if right[0] in visible_variables[index].keys():
                        right = visible_variables[index][right[0]]

            if type_left in 'int float' and type_right in 'int float':
                if right[0] != 0:
                    quotient = left[0] / right[0]
                    new_type = 'int' if type_left != 'float' and type_right != 'float' else 'float'
                    return [quotient, new_type], True
                else:
                    print('ZERO-DIVISION ERROR AT LINE', line_number)
                    return None, False
            else:
                print('COMPILATION ERROR AT LINE', line_number, ': OPERANDS SUPPOSED TO BE OF TYPE int OR float, GOT',
                      type_left, 'AND', type_right)
                return None, False
        elif line['operation'] == ['%', 'opr']:
            type_left = left[1]
            type_right = right[1]

            if type_left == 'var':
                for index in range(1, nesting_level + 1):
                    if left[0] in visible_variables[index].keys():
                        left = visible_variables[index][left[0]]
            if type_right == 'var':
                for index in range(1, nesting_level + 1):
                    if right[0] in visible_variables[index].keys():
                        right = visible_variables[index][right[0]]

            if type_left in 'int float' and type_right in 'int float':
                modulo = left[0] % right[0]
                new_type = 'int' if type_left != 'float' and type_right != 'float' else 'float'
                return [modulo, new_type], True
            else:
                print('COMPILATION ERROR AT LINE', line_number, ': OPERANDS SUPPOSED TO BE OF TYPE int OR float, GOT',
                      type_left, 'AND', type_right)
                return None, False
        elif line['operation'] == ['|', 'opr']:
            if left[0] in callables.keys():
                return execute_function(left[0], callables, right), True
            else:
                print("COMPILATION ERROR AT LINE ", line_number, ": FUNCTION", left[0], "IS NOT FOUND")
                return None, False
        elif line['operation'] == [',', 'sep']:
            return left + right, True
        else:
            return None, False


visible_variables = {}


def args_pass(args, args_needed, function_name):
    args_count_needed = len(args_needed)
    args_count = len(args)

    if args_count_needed == args_count:
        for index in range(args_count):
            token = args[index]
            type_ = token[1]

            types_available = args_needed[index]
            if type_ not in types_available:
                print("COMPILATION ERROR: FUNCTION ",
                      function_name, "EXPECTS", types_available,
                      "AS A PARAMETER, BUT", type_, "GIVEN")
                return False
        return True
    else:
        print("COMPILATION ERROR: FUNCTION ",
              function_name, "REQUIRES", len(args_needed),
              "BUT", len(args), "GIVEN")
        return False


def execute_function(function_name, callables, args):
    global visible_variables
    if isinstance(callables[function_name], dict):
        args_needed = callables[function_name]['args']
        args_needed = list(map(lambda arg: arg['right'][0], args_needed))

        if args_pass(args, args_needed, function_name):
            # TODO passing arguments

            for line in callables[function_name]['body']:
                line_number = line['line']
                response, success = execute_line(line, callables, 1, line_number)
                if not success:
                    return
    else:
        args_needed = callables[function_name][1]
        function = callables[function_name][0]

        if args_pass(args, args_needed, function_name):
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

            function(args_values)


def find_callables(tree):
    """
        fills functions_list, which are either Python callables from imported libraries or MINIMUM functions

        :param tree: code tree made on base of given file with parser.py
        :return: returns dictionary of functions: {'function_name': *either Python callable or MINIMUM code block*, ...}
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
            path = root_directory + "/libraries/" + block['right'] + ".py"
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


def execute(file_name):
    tree = make_tree(file_name)

    callables = find_callables(tree)

    if 'main' in callables.keys():
        execute_function('main', callables, [])
        print(visible_variables)
    else:
        print("COMPILATION ERROR : 'main' FUNCTION NOT FOUND")


def print_code(file_name):
    print("Executed code:")
    file = open(file_name, 'r')

    lines = file.readlines()

    max_len = len(lines[0])
    for line in lines:
        max_len = max(max_len, len(line))
        print(line, end=('' if line[-1] == '\n' else '\n'))

    file.close()

    print("-" * (max_len + 1))


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
