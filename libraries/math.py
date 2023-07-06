"""
This library implements standard mathematical operations in MINIMUM
"""
from interpreter.utils.structures import Token

def get_methods():
    """
    used for MINIMUM interpreter to interact with library
    """
    return [
        ['sqrt', sqrt_, ['float|int']],
        ['pow', pow_, ['float|int']]
    ]

def sqrt_(arg: list[int | float]) -> Token:
    """
    :param arg: real number
    :return: return square root of given number
    """
    result = arg[0] ** 0.5
    type_ = 'int' if int(result) == result else 'float'
    result = round(result) if type_ == 'int' else result
    return Token(type_, result)

def pow_(arg: list[int | float]) -> Token:
    """
    :param arg: two real numbers
    :return: first number in power of second number
    """
    result = arg[0] ** arg[1]
    type_ = 'int' if int(result) == result else 'float'
    result = round(result) if type_ == 'int' else result
    return Token(type_, result)


if __name__ == '__main__':
    print('This library implements standard mathematical operations in MINIMUM')
