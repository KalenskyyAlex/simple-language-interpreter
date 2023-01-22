def get_methods():
    return [
            ['in', in_, [['every']]],
            ['out', out, []]
    ]


def in_(obj):
    print(obj)


def out():
    return input()
