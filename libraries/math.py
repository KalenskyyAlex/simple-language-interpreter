def get_methods():
    return [
        ['sqrt', sqrt_, ['flt|int']],
        ['pow', pow_, ['flt|int']]
    ]

def sqrt_(arg):
    return arg[0] ** 0.5

def pow_(arg):
    return arg[0] ** arg[1]
