import cesk.config as cnf

class CESKException(Exception):
    """ General superclass for CESK Exceptions """
    error_code = 1
    def __init__(self, msg=""):
        super().__init__(msg)

class MemoryAccessViolation(CESKException):
    """ Exception class to signify an out of bounds memory access """
    error_code = 2
    def __init__(self, msg=""):
        super().__init__("Illegal Memory Access Detected: %s"%msg)

class UnknownConfiguration(CESKException):
    """ Configuration value is invalid """
    error_code = 3
    def __init__(self, config=""):
        super().__init__("Configuration Error: %s:%s"%(config, cnf.CONFIG[config]))

#Other ideas for errors
#Unitialized Value Read

