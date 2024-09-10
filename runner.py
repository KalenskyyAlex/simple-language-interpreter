"""
Python Script used to read and interpret users input into actions in interpreter
"""

import sys
from interpreter.min_interpreter import print_code, execute
from interpreter.min_lexer import print_tokens
from interpreter.min_parser import print_tree
from interpreter.utils.globals import enable_API_mode

if __name__ == '__main__':
    # do not output errors traceback from Python
    # sys.tracebacklimit = -1

    try:
        FIRST_ARG = sys.argv[1]

        if FIRST_ARG == '--help':
            print('Usage: python min_interpreter.py [filename] [flag1] [flag2] ...')
            print('Flags available:')
            print('\t-c - show executed code')
            print('\t-l - shot lexer result (raw tokens)')
            print('\t-p - show parser result (code tree)')
            print('\t-a - enable API_MODE (notify about waiting for input when running on server side)')
        else:
            available_flags = ['-p', '-c', '-l', '-a']
            flags = sys.argv[2:]

            unknown_token = any(flag for flag in flags if flag not in available_flags)

            if unknown_token:
                print('Unknown flag: Try typing runner.py --help to see usage info')
            else:
                if '-c' in flags:
                    print_code(FIRST_ARG)

                if '-l' in flags:
                    print_tokens(FIRST_ARG)

                if '-p' in flags:
                    print_tree(FIRST_ARG)

                if '-a' in flags:
                    enable_API_mode()

                print("Produced output:")
                execute(FIRST_ARG)

            if '-a' in flags:
                with open('finished', 'w') as f:
                    f.write('finished')

    except (FileNotFoundError, IndexError):
        print('Try typing runner.py --help to see usage info')
