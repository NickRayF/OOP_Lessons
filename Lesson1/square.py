import math

class Figure:
    def area(self):
        raise NotImplementedError

    def perimeter(self):
        raise NotImplementedError

class Square(Figure):
    def __init__(self, side):
        self._side = side

    @property
    def side(self):
        return self._side

    def area(self):
        return self._side ** 2

    def perimeter(self):
        return self._side * 4

class Circle(Figure):
    def __init__(self, rad):
        self._rad = rad

    @property
    def rad(self):
        return self._rad

    def area(self):
        return math.pi * self._rad ** 2

    def perimeter(self):
        return 2 * math.pi * self._rad

class Rectangle(Figure):
    def __init__(self, side1, side2):
        self._side1 = side1
        self._side2 = side2

    @property
    def side1(self):
        return self._side1

    @property
    def side2(self):
        return self._side2

    def area(self):
        return self._side1 * self._side2

    def perimeter(self):
        return (self._side1 + self._side2) * 2

class Triangle(Figure):
    def __init__(self, a: float, b: float, c: float):
        if a <= 0 or b <= 0 or c <= 0:
            raise ValueError
        if not (a + b > c and a + c > b and b + c > a):
            raise ValueError
        self._a = a
        self._b = b
        self._c = c

    @property
    def a(self):
        return self._a

    @property
    def b(self):
        return self._b

    @property
    def c(self):
        return self._c

    def area(self):
        s = (self._a + self._b + self._c) / 2
        return math.sqrt(s * (s - self._a) * (s - self._b) * (s - self._c))

    def perimeter(self):
        return self._a + self._b + self._c

class Trapezoid(Figure):
    def __init__(self, base1, base2, side1, side2, height):
        self._base1 = base1
        self._base2 = base2
        self._side1 = side1
        self._side2 = side2
        self._height = height

    @property
    def base1(self):
        return self._base1

    @property
    def base2(self):
        return self._base2

    def area(self):
        return (self._base1 + self._base2) * self._height / 2

    def perimeter(self):
        return self._base1 + self._base2 + self._side1 + self._side2





if __name__ == "__main__":
    s = Square(5)
    print(s.area(), s.perimeter())
    c = Circle(3)
    print(c.area(), c.perimeter())
    r = Rectangle(4, 6)
    print(r.area(), r.perimeter())
    t = Triangle(3, 4, 5)
    print(t.area(), t.perimeter())
    tr = Trapezoid(6, 4, 3, 3, 5)
    print(tr.area(), tr.perimeter())