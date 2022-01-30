from abc import ABC, abstractmethod


class Base(ABC):
    def __init__(self):
        print("Base init")

    @property
    @abstractmethod
    def testprop(self):
        pass

    @testprop.setter
    def testprop(self, arg):
        self._testprop = arg


class Deriv(Base):
    def __init__(self):
        print("Deriv init")

    #     self.a=1
    #     self._testprop=2

    # @property
    # def testprop(self):
    #     return self._testprop
    def printtest():
        print("Printing in Deriv function.")

    # @abstractmethod
    # def failtest():
    #     pass


class Dervi2(Deriv):
    def __init__(self):
        print("Deriv2 init")
        self._testprop = 2

    @property
    def testprop(self):
        return self._testprop


obj = Dervi2()
print(obj.__dict__)
# print(obj.a)
print(obj.testprop)
obj.testprop = 599
print(obj.testprop)


# class GStest():
#     def __init__(self, a, b):
#         self.a = a
#         self.b = b
#         self.c = (a + b) / 2 + 1000

#     @property
#     def c(self):
#         return self._c

#     @c.setter
#     def c(self, c):
#         self._c = c

# obj = GStest(2,4)
# print(obj.a)
# print(obj.b)
# print(obj.c)
