from .base_values import BaseFloat
from .factory import Factory
import cesk.limits as limits

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
        
    def __eq__(self, other):
        return Factory.Integer(int(self.data == other.data), 'int')

    def __ne__(self, other):
        return Factory.Integer(int(self.data != other.data), 'int')

    def __gt__(self, other):
        return Factory.Integer(int(self.data > other.data), 'int')

    def __ge__(self, other):
        return Factory.Integer(int(self.data >= other.data), 'int')

    def get_value(self, start=-1, num_bytes=None):
        """value of the unsigned bits stored"""
        #TODO get binary value
        return self.data

    def __str__(self):
        return "%f" % self.data