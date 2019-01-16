import cesk.values.base_values as BV
import cesk.limits as limits
from .factory import Factory
import random

class ConcreteInteger(BV.BaseInteger): #pylint:disable=too-few-public-methods
    """ implementation of an Integral Type"""

    def __init__(self, data, type_of, size=1):
        if type_of is 'bit_value':
            self.type_of = type_of
            self.size = size
            self.min_value = 0
            self.max_value = 2**(size*8) - 1 
            self.data = self.bound(data)
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

    def get_byte_value(self, start=-1, num_bytes=None):
        """value of the unsigned bits stored"""
        result = self.data
        byte_value = None
        if self.data < 0:
            result += self.max_value - self.min_value + 1 #make unsigned
            
        if not ((start == -1) or
                (start == 0 and num_bytes == self.size)):
            result //= 2**(start*8) #reduce to just the part needed
            result %= pow(2, num_bytes*8)
            byte_value = BV.ByteValue(num_bytes)
        else:
            byte_value = BV.ByteValue(self.size)

        byte_value.fromInt(result)
        return byte_value

    @classmethod
    def from_byte_value(cls, byte_value, type_of):
        """ Method for Integer Generation from a byte value """
        data = 0
        place = 1
        for byte in [byte_value.bits[i:i+8] for i in range(0,len(byte_value.bits),8)]:
            for bit in byte[::-1]:
                if bit == BV.ByteValue.one:
                    data += place
                elif bit == BV.ByteValue.top:
                    data += place*random.randint(0, 1)#unknown value pick a ranodm value
                place *= 2

        return cls(data, type_of, byte_value.size)
