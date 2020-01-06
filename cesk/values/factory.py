'''Is a factory for each value type'''
import cesk.config
from cesk.exceptions import UnknownConfiguration

class Factory():
    '''Factory holding the constructor for each value'''

    @staticmethod
    def getPythonObjectClass(): #pylint: disable=invalid-name
        '''returns class for python objects'''
        from .python_object import PythonObject
        Factory.getPythonObjectClass = lambda: PythonObject
        return PythonObject

    @staticmethod
    def getIntegerClass(): #pylint: disable=invalid-name
        '''returns class for Integer'''
        if cesk.config.CONFIG['values'] == 'concrete':
            from .concrete_integer import ConcreteInteger as Integer
        elif cesk.config.CONFIG['values'] == 'abstract':
            from .k_integer import KInteger as Integer
        elif cesk.config.CONFIG['values'] == 'trivial':
            from .tri_integer import TriInteger as Integer
        else:
            raise UnknownConfiguration('values')
        Factory.getIntegerClass = lambda: Integer #perform checks only once
        return Integer

    @staticmethod
    def getPointerClass(): #pylint: disable=invalid-name
        '''returns class for Pointer'''
        if cesk.config.CONFIG['values'] == 'concrete':
            from .concrete_pointer import ConcretePointer as Pointer
        elif cesk.config.CONFIG['values'] == 'abstract':
            from .abstract_pointer import AbstractPointer as Pointer
        elif cesk.config.CONFIG['values'] == 'trivial':
            from .abstract_pointer import AbstractPointer as Pointer
        else:
            raise UnknownConfiguration('values')
        Factory.getPointerClass = lambda: Pointer #perform checks only once
        return Pointer

    @staticmethod
    def getCharClass(): #pylint: disable=invalid-name
        '''returns class for Char'''
        if cesk.config.CONFIG['values'] == 'concrete':
            from .concrete_char import ConcreteChar as Char
        elif cesk.config.CONFIG['values'] == 'abstract':
            from .abstract_char import AbstractChar as Char
        elif cesk.config.CONFIG['values'] == 'trivial':
            from .abstract_char import AbstractChar as Char
        else:
            raise UnknownConfiguration('values')
        Factory.getCharClass = lambda: Char #perform checks only once
        return Char

    @staticmethod
    def getFloatClass(): #pylint: disable=invalid-name
        '''retuns class for Float'''
        if cesk.config.CONFIG['values'] == 'concrete':
            from .concrete_float import ConcreteFloat as Float
        elif cesk.config.CONFIG['values'] == 'abstract':
            from .tfloat import TFloat as Float
        elif cesk.config.CONFIG['values'] == 'trivial':
            from .tfloat import TFloat as Float
        else:
            raise UnknownConfiguration('values')
        Factory.getFloatClass = lambda: Float #perform checks only once
        return Float

    @staticmethod
    def Char(data, type_of): #pylint: disable=invalid-name
        '''Char constructor'''
        return Factory.getCharClass()(data, type_of)

    @staticmethod
    def Float(data, type_of): #pylint: disable=invalid-name
        '''Float constructor'''
        return Factory.getFloatClass()(data, type_of)

    @staticmethod
    def Integer(data, type_of, size=1): #pylint: disable=invalid-name
        '''Integer constructor'''
        return Factory.getIntegerClass()(data, type_of, size)

    @staticmethod
    def Pointer(address, type_size, offset=0): #pylint: disable=invalid-name
        '''Pointer constructor'''
        return Factory.getPointerClass()(address, type_size, offset)

    @staticmethod
    def PythonObject(node): #pylint: disable=invalid-name
        '''Python Object constructor'''
        return Factory.getPythonObjectClass()(node)
