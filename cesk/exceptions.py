'''Exceptions for the CESK interpreter'''
import cesk.config as cnf

class CESKException(Exception):
    '''General superclass for CESK Exceptions'''
    error_code = 1
    def __init__(self, msg=""):
        super().__init__('CESK '+msg)

class MemoryAccessViolation(CESKException):
    '''Exception class to signify an out of bounds memory access'''
    error_code = 2
    def __init__(self, msg=""):
        super().__init__("Illegal Memory Access Detected-> %s"%msg)

class UnknownConfiguration(CESKException):
    '''Configuration value is invalid'''
    error_code = 3
    def __init__(self, config=""):
        super().__init__("Configuration Error: %s:%s"%
                         (config, cnf.CONFIG[config]))

class TransformError(CESKException):
    '''Error for things that should be removed by the Transforms
        or not expected to be found in c code'''
    error_code = 4
#Other ideas for errors
#Uninitialized Value Read
