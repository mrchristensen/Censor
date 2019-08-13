'''Abstract Char Class'''
from .factory import Factory

class AbstractChar(Factory.getIntegerClass()):
    '''Implementation of an char Type'''
    def __init__(self, data, type_of='char', foo=None):#pylint: disable=unused-argument
        if isinstance(data, str) and ('\'' in data):
            char = data.replace("\'", "")
            val = ord(char)
        else:
            val = data
        super().__init__(val, type_of)

    def __str__(self):
        try:
            return chr(self.data)
        except ValueError: # does not map to ascii (e.g. negative chars)
            return str(self.data)
