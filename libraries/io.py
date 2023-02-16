def get_methods():
    return [
            ['in', in_, []],
            ['out', out, ['int|float|str|bool']]
    ]


def out(arg):
    print(arg[0], end="")


def in_():
    return input()
