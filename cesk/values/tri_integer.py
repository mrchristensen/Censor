""" Integer Class that only can be negative zero or positive """
import cesk.limits as limits
from .base_values import BaseInteger, ByteValue
from .factory import Factory
from .abstract_literals import AbstractLiterals as AL


class TriInteger(BaseInteger): #pylint:disable=too-few-public-methods
    """ implementation of an Integral Type for PLUS-MINUS-ZERO
        Assuming no overflow happens"""

    def __init__(self, data, type_of, size=1):
        self.data = set()
        if not isinstance(data, set):
            data = {data}
        for element in data:
            if isinstance(element, AL):
                self.data.add(element)
                continue
            if isinstance(element, str):
                element = float(element)
            if element == 0:
                self.data.add(AL.ZERO)
            elif element < 0:
                self.data.add(AL.MINUS)
            elif element > 0:
                self.data.add(AL.PLUS)
            else:
                raise Exception("Unkown value" +  str(element))
        if AL.TOP in self.data or \
                (AL.MINUS in self.data and \
                 AL.PLUS in self.data and \
                 AL.ZERO in self.data):
            self.data = set([AL.TOP])

        if type_of == 'bit_value':
            self.type_of = type_of
            self.size = size
            self.min_value = 0
            self.max_value = 2**size - 1

        else:
            self.type_of = type_of
            self.size = limits.CONFIG.get_size(type_of.split())

    def __add__(self, other):
        value = set()
        for ele1 in self.data:
            for ele2 in other.data:
                if ele1 == AL.MINUS and ele2 == AL.MINUS:
                    value.add(-1)
                elif ele1 == AL.PLUS and ele2 == AL.PLUS:
                    value.add(1)
                elif ele1 == AL.ZERO:
                    value.add(ele2)
                elif ele2 == AL.ZERO:
                    value.add(ele1)
                else:
                    value = set([AL.TOP])
                    break
        return Factory.Integer(value, self.type_of, self.size)

    def __neg__(self):
        value = set()
        if AL.ZERO in self.data:
            value.add(0)
        if AL.MINUS in self.data:
            value.add(1)
        if AL.PLUS in self.data:
            value.add(-1)
        return Factory.Integer(value, self.type_of, self.size)

    def __sub__(self, other):
        return self + -other

    def __mul__(self, other):
        value = set()
        # Handle Top
        if AL.TOP in self.data or AL.TOP in other.data:
            if len(self.data) == 1 and AL.ZERO in self.data:
                return Factory.Integer(set([0]), self.type_of, self.size)
            if len(other.data) == 1 and AL.ZERO in other.data:
                return Factory.Integer(set([0]), self.type_of, self.size)
            return Factory.Integer(set([AL.TOP]), self.type_of, self.size)
        for ele1 in self.data:
            for ele2 in other.data:
                if ele1 == AL.ZERO or ele2 == AL.ZERO:
                    value.add(0)
                elif ele1 == ele2:
                    value.add(1)
                else:
                    value.add(-1)
        return Factory.Integer(value, self.type_of, self.size)

    def __truediv__(self, other):
        value = {AL.TOP} #not entirely correct but close enough
        return Factory.Integer(value, self.type_of, self.size)

    def __mod__(self, other):
        value = {AL.TOP}
        return Factory.Integer(value, self.type_of, self.size)

    def __lt__(self, other):
        value = set()
        if AL.TOP in self.data or AL.TOP in other.data:
            return Factory.Integer(set([0, 1]), 'int')
        if AL.PLUS in self.data:
            value.add(0)
        if AL.PLUS in other.data:
            value.add(1)
        if AL.MINUS in self.data:
            value.add(1)
        if AL.MINUS in other.data:
            value.add(0)
        if AL.ZERO in self.data and AL.ZERO in other.data:
            value.add(0)
        return Factory.Integer(value, 'int')

    def __le__(self, other):
        return (other < self).__not__()

    def equals(self, other):
        value = set()
        if not isinstance(other, Factory.getIntegerClass()):
            return Factory.Integer({0}, 'int')
        if AL.TOP in self.data or AL.TOP in other.data:
            return Factory.Integer(set([0, 1]), 'int')
        if AL.PLUS in self.data:
            value.add(0)
            if AL.PLUS in other.data:
                return Factory.Integer(set([0, 1]), 'int')
        if AL.MINUS in self.data:
            value.add(0)
            if AL.MINUS in other.data:
                return Factory.Integer(set([0, 1]), 'int')
        if AL.ZERO in self.data:
            if AL.ZERO in other.data:
                value.add(1)
            if AL.MINUS in other.data:
                value.add(0)
            if AL.PLUS in other.data:
                value.add(0)

        return Factory.Integer(value, 'int')

    def __hash__(self):
        val = 0 #pylint: disable=invalid-name
        if AL.TOP in self.data:
            val += 1
        if AL.MINUS in self.data:
            val += 2
        if AL.ZERO in self.data:
            val += 4
        if AL.PLUS in self.data:
            val += 8
        return val

    def __not__(self):
        not_values = set()
        if AL.TOP in self.data:
            return Factory.Integer(set([0, 1]), 'int')
        if AL.PLUS in self.data or AL.MINUS in self.data:
            not_values.add(0)
        if AL.ZERO in self.data:
            not_values.add(1)
        return Factory.Integer(not_values, 'int')

    def __ne__(self, other):
        return (self == other).__not__()

    def __gt__(self, other):
        return other < self

    def __ge__(self, other):
        return (self < other).__not__()

    def get_byte_value(self, start=-1, num_bytes=None):
        """value of the unsigned bits stored"""
        byte_value = ByteValue(self.size)
        if AL.TOP in self.data:
            return byte_value

        if AL.MINUS in self.data:
            if len(self.data) == 1:
                byte_value.bits[0] = ByteValue.one
            return byte_value

        if AL.ZERO in self.data and len(self.data) == 1:
            byte_value = ByteValue(self.size, ByteValue.zero)
        else:
            byte_value.bits[0] = ByteValue.zero

        return byte_value

    @classmethod
    def from_byte_value(cls, byte_value, type_of):
        """ convert to abstract from byte value """
        types = set()
        if byte_value.bits[0] != ByteValue.zero:
            types.add(AL.MINUS)
        if all(i != ByteValue.one for i in byte_value.bits):
            types.add(AL.ZERO)
        if byte_value.bits[0] != ByteValue.one and \
                all(i != ByteValue.zero for i in byte_value.bits):
            types.add(AL.PLUS)

        return cls(types, type_of, byte_value.size)

    def get_truth_value(self):
        values = set()
        for val in self.data:
            if val == AL.ZERO:
                values.add(False)
            elif val == AL.TOP:
                values.add(True)
                values.add(False)
            else:
                values.add(True)
        return values
