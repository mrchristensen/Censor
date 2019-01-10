from .factory import Factory

class AbstractChar(Factory.getIntegerClass()):
    """ implementation of an char Type"""
    def __init__(self, data, type_of='char', foo=None):
        if isinstance(data, str) and ('\'' in data):
            char = data.replace("\'", "")
            v = ord(char)
        else:
            v = data
        super().__init__(v, type_of)
