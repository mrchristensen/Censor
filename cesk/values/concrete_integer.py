from .base_values import BaseInteger
import cesk.limits as limits
from .factory import Factory

class ConcreteInteger(BaseInteger): #pylint:disable=too-few-public-methods
    """ implementation of an Integral Type"""

    def __init__(self, data, type_of, size=1):
        if type_of is 'bit_value':
            self.type_of = type_of
            self.size = size
            self.min_value = 0
            self.max_value = 2**size - 1 
            self.data = int(data)
        else:
            self.type_of = type_of
            self.size = limits.CONFIG.get_size(type_of.split())
            self.min_value, self.max_value = limits.RANGES[type_of]
            self.data = self.bound(data)

    def __add__(self, other):
        value = self.bound(self.data + other.data)
        return Factory.Integer(value, self.type_of, self.size)

    def __sub__(self, other):
        value = self.bound(self.data - other.data)
        return Factory.Integer(value, self.type_of, self.size)

    def __mul__(self, other):
        value = self.bound(self.data * other.data)
        return Factory.Integer(value, self.type_of, self.size)

    def __truediv__(self, other):
        value = self.bound(self.data // other.data)
        return Factory.Integer(value, self.type_of, self.size)

    def __mod__(self, other):
        value = self.bound(self.data % other.data)
        return Factory.Integer(value, self.type_of, self.size)
        
    def __lt__(self, other):
        return Factory.Integer(int(self.data < other.data), 'int')
        
    def __le__(self, other):
        return Factory.Integer(int(self.data <= other.data), 'int')
        
    def __eq__(self, other):
        return Factory.Integer(int(self.data == other.data), 'int')

    def __ne__(self, other):
        return Factory.Integer(int(self.data != other.data), 'int')

    def __gt__(self, other):
        return Factory.Integer(int(self.data > other.data), 'int')

    def __ge__(self, other):
        return Factory.Integer(int(self.data >= other.data), 'int')

    def bound(self, value):
        """ Simulates two's complement overflow of integral types """
        n = value - self.min_value
        m = self.max_value - self.min_value + 1
        k = n % m
        x = k + self.min_value
        return x

    def get_value(self, start=-1, num_bytes=None):
        """value of the unsigned bits stored"""
        result = self.data
        if self.data < 0:
            result += self.max_value - self.min_value + 1
            
        if ((start == -1) or
                (start == 0 and num_bytes == self.size)):
            #Get all of the bytes
            return result

        result //= 2**(start*8)
        result %= pow(2, num_bytes*8)

        return result
