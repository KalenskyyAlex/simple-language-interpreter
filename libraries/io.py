"""
This library implements standard i/o operations in MINIMUM
"""
from typing import Optional

from interpreter.utils.structures import Token
from interpreter.utils.globals import API_MODE

def get_methods():
    """
    used for MINIMUM interpreter to interact with library
    """
    return [
            ['in', in_, ['typ']],
            ['out', out, ['int|float|str|bool']]
    ]


def out(arg: list) -> None:
    """
    outputs an arg
    :param arg: variable to print
    """
    print(arg[0], end="")


def in_(arg: list) -> Token:
    """
    API_MODE=True: will signal about waiting for input into input_needed
    reads from standard input
    :return: string read from standard input
    """
    if API_MODE:
        with open("input_needed", "w") as f:
            f.write("input_needed")

    type_ = None
    result: Optional[int | float | str | bool] = None
    match arg[0]:
        case 'int':
            type_ = 'int'
            result = int(input())
        case 'float':
            type_ = 'float'
            result = float(input())
        case 'str':
            type_ = 'str'
            result = input()
        case 'bool':
            type_ = 'bool'
            result = bool(input())

    # clearing file - no input needed no more
    if API_MODE:
        with open("input_needed", "w"):
            pass

    return Token(type_, result)


if __name__ == '__main__':
    print('This library implements standard i/o operations in MINIMUM')
