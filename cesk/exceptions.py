import cesk.config as cnf

class CESKException(Exception):
    """ General superclass for CESK Exceptions """
    def __init__(self, msg=""):
        super().__init__(msg)

class MemoryAccessViolation(CESKException):
    """ Exception class to signify an out of bounds memory access """
    def __init__(self, msg=""):
        super().__init__("Illegal Memory Access Detected: %s"%msg)

#Unitialized Value Read

class UnknownConfiguration(CESKException):
    """ Configuration value is invalid """
    def __init__(self, config=""):
        super().__init__("Configuration Error: %s:%s"%(config, cnf.CONFIG[config]))
