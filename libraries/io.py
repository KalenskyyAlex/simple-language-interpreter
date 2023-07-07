"""
This library implements standard i/o operations in MINIMUM
"""
from typing import Optional

from interpreter.utils.structures import Token

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
    reads from standard input
    :return: string read from standard input
    """
    type_ = None
    result: Optional[int | float | str | bool] = None
    match arg[0]:
        case 'int':
            type_ = 'int'
            result = int(input())
        case 'float':
            type_ = 'float'
            result = float(input())
        case 'float':
            type_ = 'str'
            result = input()
        case 'float':
            type_ = 'bool'
            result = bool(input())

    return Token(type_, result)


if __name__ == '__main__':
    print('This library implements standard i/o operations in MINIMUM')
