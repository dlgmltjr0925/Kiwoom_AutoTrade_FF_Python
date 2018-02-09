class A(object):
    def __init__(self):
        self.a = None
        self.b = 1

class B(object):
    def __init__(self):
        self.c = None
        self.d = 2

if __name__ == '__main__':
    a = A()
    b = a
    a.b = 4
    b.a = 1
    print(a.b)
    print(b.b)
    print(a.a)
