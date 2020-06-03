import time

class Timer:
    def __init__(self):
        self.start = None
        self.dt = None
    def __enter__(self):
        self.start = time.time()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dt = time.time() - self.start

class BligInt:
    ZEROS = 1
    MOD = 10**ZEROS

    @classmethod
    def from_big_endian(cls, parts = [], sign = 1):
        if abs(sign) != 1:
            raise ValueError("Invalid sign", sign)
        le = []
        for part in parts:
            if part < 0 or part >= BligInt.MOD:
                raise ValueError("Invalid part", part)
            le.append(part)
        le.reverse()
        return BligInt(le, sign)

    def __init__(self, parts = None, sign = 1):
        self.parts = [] if parts is None else parts
        self.sign = sign
        self.__drop_lead_zeros()

    def __drop_lead_zeros(self):
        try:
            while self.parts[-1] == 0:
                self.parts.pop()
        except IndexError:
            self.sign = 1

    def __add(self, other):
        a = self.parts
        b = other.parts
        a.extend(0 for i in range(len(b) - len(a)))
        div = 0
        for i in range(len(b)):
            div, mod = divmod(div + a[i] + b[i], BligInt.MOD)
            a[i] = mod
        for i in range(len(b), len(a)):
            div, mod = divmod(div + a[i], BligInt.MOD)
            a[i] = mod
            if div == 0:
                break
        if div > 0:
            a.append(div)

    def __subtract(self, other): #consider "two's" complement
        a = self.parts
        b = other.parts
        if  BligInt(a) < BligInt(b):
            a, b = b, a
        self.parts.extend(0 for i in range(len(other.parts) - len(self.parts)))
        div = 0
        for i in range(len(b)):
            div, mod = divmod(div + a[i] - b[i], BligInt.MOD)
            self.parts[i] = mod
        for i in range(len(b), len(a)):
            div, mod = divmod(div + a[i], BligInt.MOD)
            self.parts[i] = mod
            if div == 0:
                break
        self.sign *= 1 if a is self.parts else -1
        self.__drop_lead_zeros()

    def __iadd__(self, other):
        if self.sign == other.sign:
            self.__add(other)
        else:
            self.__subtract(other)
        return self

    def __isub__(self, other):
        if self.sign != other.sign:
            self.__add(other)
        else:
            self.__subtract(other)
        return self

    def __ilshift__(self, shift):
        if shift < 0:
            raise ValueError("Invalid shift", shift)
        self.parts = [0]*shift + self.parts
        return self

    def __lshift__(self, shift):
        c = BligInt(self.parts[:], self.sign)
        c <<= shift
        return c

    def __mul__(self, other):
        return caching_mul(self, other)

    def __add__(self, other):
        c = BligInt(self.parts[:], self.sign)
        c += other
        return c

    def __sub__(self, other):
        c = BligInt(self.parts[:], self.sign)
        c -= other
        return c

    def __lt__(self, other):
        if self is other:
            return False
        if self.sign != other.sign:
            return self.sign < other.sign
        a = self.parts
        b = other.parts
        if len(a) != len(b):
            return len(a) < len(b)
        for i in range(len(a) - 1, -1, -1):
            if a[i] != b[i]:
                return a[i] < b[i]
        return False

    def __eq__(self, other):
        return ((self < other) == False) and ((other < self) == False)

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        if self.parts == []:
            return "0"
        digit = "{0:0" + str(BligInt.ZEROS) + "}"
        return "{0}{1}".format("-" if self.sign < 0 else "", "".join(digit.format(a) for a in reversed(self.parts)))

def subdiv_mul(x, y):
    a = x.parts
    b = y.parts
    la = len(a)
    lb = len(b)

    if la == 0 or lb == 0:
        return BligInt([0])
    if la == 1 and lb == 1:
        div, mod = divmod(a[0] * b[0], BligInt.MOD)
        return BligInt([mod, div]) if div != 0 else BligInt([mod])

    da = la // 2
    db = lb // 2
    x1 = BligInt(a[da:])
    x0 = BligInt(a[:da])
    y1 = BligInt(b[db:])
    y0 = BligInt(b[:db])

    hi = subdiv_mul(x1, y1)
    hx = subdiv_mul(x1, y0)
    hy = subdiv_mul(y1, x0)
    lo = subdiv_mul(x0, y0)

    r = (hi << (da + db)) + (hx << da) + (hy << db) + lo
    r.sign = x.sign * y.sign
    return r

def karatsuba_mul(x, y):
    a = x.parts
    b = y.parts
    la = len(a)
    lb = len(b)

    if la == 0 or lb == 0:
        return BligInt([0])
    if la == 1 and lb == 1:
        div, mod = divmod(a[0] * b[0], BligInt.MOD)
        return BligInt([mod, div]) if div != 0 else BligInt([mod])

    half = max(la, lb)//2
    x1 = BligInt(a[half:])
    x0 = BligInt(a[:half])
    y1 = BligInt(b[half:])
    y0 = BligInt(b[:half])

    hi = karatsuba_mul(x1, y1)
    lo = karatsuba_mul(x0, y0)
    hf = karatsuba_mul(x0 + x1, y0 + y1) - hi - lo
    r = (hi << (2*half)) + (hf << half) + lo
    r.sign = x.sign*y.sign
    return r

def caching_mul(x, y):
    def mul1(n):
        div = 0
        mul = BligInt()
        for p in x.parts:
            div, mod = divmod(div + n*p, BligInt.MOD)
            mul.parts.append(mod)
        if div > 0:
            mul.parts.append(div)
        return mul
    cache = [mul1(n) for n in range(BligInt.MOD)]
    acc = BligInt()
    for i, n in enumerate(y.parts):
        mul = cache[n]
        acc += mul << i
    acc.sign = x.sign*y.sign
    return acc

LARGE_POS = BligInt.from_big_endian(x % BligInt.MOD for x in range(20, 0, -1))
SMALL_POS = BligInt.from_big_endian(x % BligInt.MOD for x in range(0, 20))
LARGE_NEG = BligInt() - LARGE_POS
SMALL_NEG = BligInt() - SMALL_POS

N = 100

def test(desc, func):
    with Timer() as dt:
        a = BligInt([1])
        for i in range(N):
            a = func(a, LARGE_POS)
    print(desc, dt.dt, "s")
    print(a)

def test_py_int():
    py_int = 0
    for i, p in enumerate(LARGE_POS.parts):
        py_int += p * BligInt.MOD ** i
    with Timer() as dt:
        a = 1
        for i in range(N):
            a = a*py_int
    print("Python int", dt.dt, "s")
    print(a)

print("{0}**{1}:".format(str(LARGE_POS), N))
test("Halfing", subdiv_mul)
test("Karatsuba", karatsuba_mul)
test("Caching", caching_mul)
test_py_int()

assert LARGE_NEG + LARGE_POS == LARGE_POS + LARGE_NEG
assert LARGE_NEG - LARGE_NEG == LARGE_POS - LARGE_POS
assert LARGE_POS - SMALL_POS + LARGE_NEG - SMALL_NEG == SMALL_POS - LARGE_POS - LARGE_NEG + SMALL_NEG
assert LARGE_POS - SMALL_POS == SMALL_NEG + LARGE_POS