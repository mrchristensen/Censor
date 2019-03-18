""" Concrete Float Class """
import struct
import cesk.limits as limits
from .base_values import BaseFloat, ByteValue
from .factory import Factory

class ConcreteFloat(BaseFloat):  #pylint:disable=too-few-public-methods
    """ implementation of a float.
    NOTE: this class will represent 'float,' and 'double,' and 'long double'
    from C99 as a 64 bit floating point number. This gives some potentially
    incorrect rounding for c programs that use the 'float' or 'long double'
    data types, which is supposed to be represented as a 32 or float."""

    def __init__(self, data, type_of):
        self.data = float(data)
        self.type_of = type_of
        self.size = limits.CONFIG.get_size(type_of.split())

    def __add__(self, other):

        return Factory.Float(self.data + other.data, self.type_of)

    def __sub__(self, other):
        return Factory.Float(self.data - other.data, self.type_of)

    def __mul__(self, other):
        return Factory.Float(self.data * other.data, self.type_of)

    def __truediv__(self, other):
        return Factory.Float(self.data / other.data, self.type_of)

    def __lt__(self, other):
        return Factory.Integer(int(self.data < other.data), 'int') # here

    def __le__(self, other):
        return Factory.Integer(int(self.data <= other.data), 'int')

    def equals(self, other):
        return Factory.Integer(int(self.data == other.data), 'int')

    def __ne__(self, other):
        return Factory.Integer(int(self.data != other.data), 'int')

    def __gt__(self, other):
        return Factory.Integer(int(self.data > other.data), 'int')

    def __ge__(self, other):
        return Factory.Integer(int(self.data >= other.data), 'int')

    def __str__(self):
        return "%f" % self.data
    def __hash__(self):
        return hash(self.data)
    def __eq__(self, other):
        return self.data == other.data

    def get_byte_value(self, start=-1, num_bytes=None):
        """value of the unsigned bits stored"""
        #TODO get binary value
        if start == -1:
            num_bytes = self.size
            start = 0
        if self.size == 4:
            byte_array = struct.pack('!f', self.data)
        elif self.size == 8:
            byte_array = struct.pack('!d', self.data)
        else:
            return ByteValue(num_bytes) #returns top number of bytes

        byte_value = ByteValue()
        for i in range(num_bytes):
            byte_value.append(ByteValue.fromByte(byte_array[start+i]))

        return byte_value

    @classmethod
    def from_byte_value(cls, byte_value, type_of):
        """ Method for Integer Generation from a byte value """
        float_value = cls(0.0, type_of)

        if byte_value.size == 4:
            float_value.data = struct.unpack('!f', byte_value.get_bytes())[0]
        elif byte_value.size == 8:
            float_value.data = struct.unpack('!d', byte_value.get_bytes())[0]

        return float_value
