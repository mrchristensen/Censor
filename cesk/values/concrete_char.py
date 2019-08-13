'''The char class'''
import random
from .factory import Factory
from .base_values import ByteValue

class ConcreteChar(Factory.getIntegerClass()):
    '''Implementation of an char Type'''
    def __init__(self, data, type_of='char', size=None):
        if isinstance(data, str) and ('\'' in data):
            char = data.replace("\'", "")
            val = ord(char)
        else:
            val = data
        super().__init__(val, type_of)

    def __add__(self, other):
        value = super().__add__(other).data
        return Factory.Char(value, self.type_of)

    def __sub__(self, other):
        value = super().__sub__(other).data
        return Factory.Char(value, self.type_of)

    def __mul__(self, other):
        value = super().__mul__(other).data
        return Factory.Char(value, self.type_of)

    def __truediv__(self, other):
        value = super().__truediv__(other).data
        return Factory.Char(value, self.type_of)

    def __mod__(self, other):
        value = super().__mod__(other).data
        return Factory.Char(value, self.type_of)

    def get_char(self):
        '''Changes int value to char'''
        return chr(self.data)

    def __str__(self):
        try:
            return chr(self.data)
        except ValueError: # does not map to ascii (e.g. negative chars)
            return str(self.data)

    @classmethod
    def from_byte_value(cls, byte_value, type_of):
        '''Method for Integer Generation from a byte value'''
        data = 0
        place = 128
        for bit in byte_value.bits:
            if bit == ByteValue.one:
                data += place
            elif bit == ByteValue.top:
                data += place*random.randint(0, 1)#unknown pick a random value
            place //= 2

        return cls(data, type_of)
