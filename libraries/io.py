def get_methods():
    return [
            ['in', in_, [['int|flt|str|bln']]],
            ['out', out, []]
    ]


def in_(arg):
    print(arg[0])


def out():
    return input()
