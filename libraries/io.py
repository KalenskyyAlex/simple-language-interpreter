"""
This library implements standard i/o operations in MINIMUM
"""

def get_methods():
    """
    used for MINIMUM interpreter to interact with library
    """
    return [
            ['in', in_, []],
            ['out', out, ['int|float|str|bool']]
    ]


def out(arg: list) -> None:
    """
    outputs an arg
    :param arg: variable to print
    """
    print(arg[0], end="")


def in_() -> str:
    """
    reads from standard input
    :return: string read from standard input
    """
    return input()


if __name__ == '__main__':
    print('This library implements standard i/o operations in MINIMUM')
