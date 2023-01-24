import os

from parser import make_tree, print_tree
from lexer import print_tokens
import sys
import importlib.util

# ON DEBUG
from pprint import pprint

def execute_line():
    pass


def execute_function(function_name):
    pass


def handle_libraries():
    pass


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
                args = [method[2]]

                callables[name] = [callable_, args]

    return callables


def execute(file_name):
    tree = make_tree(file_name)

    callables = find_callables(tree)

    if 'main' in callables.keys():
        execute_function('main')
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
