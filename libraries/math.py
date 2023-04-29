"""
This library implements standard mathematical operations in MINIMUM
"""

def get_methods():
    """
    used for MINIMUM interpreter to interact with library
    """
    return [
        ['sqrt', sqrt_, ['float|int']],
        ['pow', pow_, ['float|int']]
    ]

def sqrt_(arg: list[int | float]) -> int | float:
    """
    :param arg: real number
    :return: return square root of given number
    """
    return arg[0] ** 0.5

def pow_(arg: list[int | float]) -> int | float:
    """
    :param arg: two real numbers
    :return: first number in power of second number
    """
    return arg[0] ** arg[1]


if __name__ == '__main__':
    print('This library implements standard mathematical operations in MINIMUM')
