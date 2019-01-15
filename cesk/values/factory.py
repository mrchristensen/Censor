'''Is a factory for each value type'''
import cesk.config


class Factory():
    '''Factory holding the constructor for each value'''

    @staticmethod
    def getIntegerClass():
        '''returns class for Integer'''
        if cesk.config.CONFIG['values'] == 'concrete':
            from .concrete_integer import ConcreteInteger as Integer
        elif cesk.config.CONFIG['values'] == 'abstract':
            from .k_integer import KInteger as Integer
        return Integer

    @staticmethod
    def getPointerClass():
        '''returns class for Pointer'''
        if cesk.config.CONFIG['values'] == 'concrete':
            from .concrete_pointer import ConcretePointer as Pointer
        elif cesk.config.CONFIG['values'] == 'abstract':
            from .abstract_pointer import AbstractPointer as Pointer
        return Pointer

    @staticmethod
    def getCharClass():
        '''returns class for Char'''
        if cesk.config.CONFIG['values'] == 'concrete':
            from .concrete_char import ConcreteChar as Char
        elif cesk.config.CONFIG['values'] == 'abstract':
            from .abstract_char import AbstractChar as Char
        return Char

    @staticmethod
    def getFloatClass():
        '''retuns class for Float'''
        if cesk.config.CONFIG['values'] == 'concrete':
            from .concrete_float import ConcreteFloat as Float
        elif cesk.config.CONFIG['values'] == 'abstract':
            from .tfloat import TFloat as Float
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
