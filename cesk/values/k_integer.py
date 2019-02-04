""" Abstract Integer that acts like a concrete integer from -1 to K """
import cesk.values.base_values as BV
from .concrete_integer import ConcreteInteger
from .abstract_literals import AbstractLiterals as AL
from .factory import Factory

class KInteger(ConcreteInteger):
    """ Implementation of K-integer """
    K = 100
    def __init__(self, data, type_of, size=1):
        if isinstance(data, set):
            data = AL.TOP
        super().__init__(data, type_of, size)
        self.min_value = -1
        self.max_value = KInteger.K

    def __add__(self, other):
        if self.data == AL.TOP or other.data == AL.TOP:
            return Factory.Integer(AL.TOP, self.type_of, self.size)
        else:
            return super().__add__(other)

    def __sub__(self, other):
        if self.data == AL.TOP or other.data == AL.TOP:
            return Factory.Integer(AL.TOP, self.type_of, self.size)
        else:
            return super().__sub__(other)

    def __mul__(self, other):
        if self.data == AL.TOP or other.data == AL.TOP:
            return Factory.Integer(AL.TOP, self.type_of, self.size)
        else:
            return super().__mul__(other)

    def __truediv__(self, other):
        if self.data == AL.TOP or other.data == AL.TOP:
            return Factory.Integer(AL.TOP, self.type_of, self.size)
        else:
            return super().__truediv__(other)

    def __mod__(self, other):
        if self.data == AL.TOP or other.data == AL.TOP:
            return Factory.Integer(AL.TOP, self.type_of, self.size)
        else:
            return super().__mod__(other)

    def __lt__(self, other):
        if self.data == AL.TOP or other.data == AL.TOP:
            return Factory.Integer(AL.TOP, self.type_of, self.size)
        else:
            return super().__lt__(other)

    def __le__(self, other):
        if self.data == AL.TOP or other.data == AL.TOP:
            return Factory.Integer(AL.TOP, self.type_of, self.size)
        else:
            return super().__le__(other)

    def equals(self, other):
        if self.data == AL.TOP or other.data == AL.TOP:
            return Factory.Integer(AL.TOP, self.type_of, self.size)
        else:
            return super().equals(other)

    def __ne__(self, other):
        if self.data == AL.TOP or other.data == AL.TOP:
            return Factory.Integer(AL.TOP, self.type_of, self.size)
        else:
            return super().__ne__(other)

    def __gt__(self, other):
        if self.data == AL.TOP or other.data == AL.TOP:
            return Factory.Integer(AL.TOP, self.type_of, self.size)
        else:
            return super().__gt__(other)

    def __ge__(self, other):
        if self.data == AL.TOP or other.data == AL.TOP:
            return Factory.Integer(AL.TOP, self.type_of, self.size)
        else:
            return super().__ge__(other)

    def bound(self, value):
        """ Simulates two's complement overflow of integral types """
        if value == AL.TOP or value < self.min_value or value > self.max_value:
            return AL.TOP
        else:
            return value

    def get_byte_value(self, start=-1, num_bytes=None):
        """value of the unsigned bits stored"""
        if self.data == AL.TOP:
            if start == -1:
                return BV.ByteValue(self.size)
            else:
                return BV.ByteValue(num_bytes)
        else:
            return super().get_byte_value(start, num_bytes)

    @classmethod
    def from_byte_value(cls, byte_value, type_of):
        """ Method for Integer Generation from a byte value """
        if BV.ByteValue.top in byte_value.bits:
            return Factory.Integer(AL.TOP, type_of)
        return super().from_byte_value(byte_value, type_of)
