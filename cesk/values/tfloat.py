from .factory import Factory
from .abstract_literals import AbstractLiterals
from .base_values import ByteValue, BaseFloat
import cesk.limits as limits

class TFloat(BaseFloat):  #pylint:disable=too-few-public-methods
    """Abstraction of Float where Float can only be T"""

    def __init__(self, data, type_of):
        self.data = set([AbstractLiterals.TOP])
        self.type_of = type_of
        self.size = limits.CONFIG.get_size(type_of.split())

    def __add__(self, other):
        return Factory.Float(0, self.type_of)

    def __sub__(self, other):
        return Factory.Float(0, self.type_of)

    def __mul__(self, other):
        return Factory.Float(0, self.type_of)

    def __truediv__(self, other):
        return Factory.Float(0, self.type_of)

    def __lt__(self, other):
        return Factory.Integer(set([0, 1]), 'int')

    def __le__(self, other):
        return Factory.Integer(set([0, 1]), 'int')

    def __eq__(self, other):
        return Factory.Integer(set([0, 1]), 'int')

    def __ne__(self, other):
        return Factory.Integer(set([0, 1]), 'int')

    def __gt__(self, other):
        return Factory.Integer(set([0, 1]), 'int')

    def __ge__(self, other):
        return Factory.Integer(set([0, 1]), 'int')

    def get_byte_value(self, start=-1, num_bytes=None):
        """value of the unsigned bits stored"""
        #TODO get binary value
        return ByteValue(self.size)
    
    def get_truth_value(self):
        return set([True, False])

    @classmethod
    def from_byte_value(cls, value, type_of):
        return cls(set([AbstractLiterals.TOP]), type_of)
        