class TLogElement:
    def __init__(self):
        self.__in1 = False
        self.__in2 = False
        self._res = False
        if not callable(getattr(self, "calc", None)):
            raise NotImplementedError("Нельзя создать такой объект!")
        self.__next = None
        self.__next_in = 0

    def __push(self):
        if not self.__next:
            return
        el, pin = self.__next
        if pin == 1:
            el.In1 = self._res
        elif pin == 2:
            el.In2 = self._res

    def __setIn1(self, v):
        self.__in1 = bool(v)
        self.calc()
        self.__push()

    def __setIn2(self, v):
        self.__in2 = bool(v)
        self.calc()
        self.__push()

    In1 = property(lambda s: s.__in1, __setIn1)
    In2 = property(lambda s: s.__in2, __setIn2)
    Res = property(lambda s: s._res)

    def link(self, nextEl, nextIn):
        self.__next = (nextEl, nextIn)


class TNot(TLogElement):
    def calc(self):
        self._res = not self.In1


class TLog2In(TLogElement):
    pass


class TAnd(TLog2In):
    def calc(self):
        self._res = self.In1 and self.In2


class TOr(TLog2In):
    def calc(self):
        self._res = self.In1 or self.In2


not_top = TNot()
and_top = TAnd()
not_bottom = TNot()
and_bottom = TAnd()
or_final = TOr()

not_top.link(and_top, 2)
and_top.link(or_final, 1)

not_bottom.link(and_bottom, 1)
and_bottom.link(or_final, 2)

print("X\tY\tРезультат")
for x, y in ((0, 0), (0, 1), (1, 0), (1, 1)):
    not_top.In1 = y
    and_top.In1 = x
    not_bottom.In1 = x
    and_bottom.In2 = y
    print(f"{x}\t{y}\t{int(or_final.Res)}")
