'''Is a factory for each value type'''
import cesk.config
if cesk.config.CONFIG['values'] == 'concrete':
    pass
#     from cesk.values.concrete import Integer, Char, Pointer
#     from cesk.values.concrete_float import ConcreteFloat as Float
elif cesk.config.CONFIG['values'] == 'abstract':
    pass
#     from cesk.values.abstract import IntAsFloat as Float
#     from cesk.values.abstract import Integer, Char, Pointer
else:
    raise Exception("Unknown value type = " + cesk.config.CONFIG['values'])


class Factory():
    '''Factory holding the constructor for each value'''

    @staticmethod
    def getIntegerClass():
        '''returns class for Integer'''
        from .concrete_integer import ConcreteInteger as Integer
        return Integer

    @staticmethod
    def getPointerClass():
        '''returns class for Pointer'''
        from .concrete_pointer import ConcretePointer as Pointer
        return Pointer

    @staticmethod
    def getCharClass():
        '''returns class for Char'''
        from .concrete_char import ConcreteChar as Char
        return Char

    @staticmethod
    def getFloatClass():
        '''retuns class for Float'''
        from .concrete_float import ConcreteFloat as Float
        return Float
        
    @staticmethod
    def Char(data, type_of):
        '''Char constructor'''
        return Factory.getCharClass()(data, type_of)

    @staticmethod
    def Float(data, type_of):
        '''Float constructor'''
        return Factory.getFloatClass()(data, type_of)

    @staticmethod
    def Integer(data, type_of, size=1):
        '''Integer constructor'''
        return Factory.getIntegerClass()(data, type_of, size)

    @staticmethod
    def Pointer(address, type_size, offset=0):
        '''Pointer constructor'''
        return Factory.getPointerClass()(address, type_size, offset)
