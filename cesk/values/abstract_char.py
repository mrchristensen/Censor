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
        
    def __str__(self):
        try:
            return chr(self.data)
        except ValueError: # does not map to ascii (e.g. negative chars)
            return str(self.data)