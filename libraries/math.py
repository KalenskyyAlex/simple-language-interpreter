def get_methods():
    return [
        ['sqrt', sqrt_, ['flt|int']],
        ['pow', pow_, ['flt|int']]
    ]

def sqrt_(number):
    return number ** 0.5

def pow_(number, power):
    return number ** power
