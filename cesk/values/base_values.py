BINOPS = {
    "+" : "__add__",
    "-" : "__sub__",
    "*" : "__mul__", #non reference values
    "/" : "__truediv__", #non reference values
    "%" : "__mod__", #integer values only
    "<" : "__lt__",
    "<=": "__le__",
    "==": "__eq__",
    "!=": "__ne__",
    ">" : "__gt__",
    ">=": "__ge__",
    "<<": "__lshift__", #integer only
    ">>": "__rshift__", #integer only
    "&" : "__and__", #integer only
    "^" : "__xor__", #integer ontl
    "|" : "__or__",  #integer only
    "&&": "transformed",
    "||": "transformed"
    #all assentments should be transformed
    #turinary operator is transformed as well
}

UNOPS = {
    "++" : "transformed",
    "--" : "transformed",
    "sizeof" : "transformed",
    "&" : "interpreted",
    "*" : "interpreted",
    "+" : "__pos__",
    "-" : "__neg__",
    "~" : "__inv__",
    "!" : "__not__"
}

class ArithmeticValue:
    """Abstract class for polymorphism between abstract and concrete values"""
    #data = None #store the value a data type that matches
    #type_of = None #stores the type string
    #size = None #stores the size int

    def perform_operation(self, operator, value):
        """Performs operation and returns value."""
        if operator in BINOPS:
            method = self.__getattribute__(BINOPS[operator])
            return method(value)
        elif operator in UNOPS:
            method = self.__getattribute__(UNOPS[operator])
            return method() #second value is not needed
        else:
            raise NotImplementedError()

    def get_truth_value(self):
        """Returns a bool denoting what truth value the ArithmeticValue would
        have if it were inside of an if statement in C"""
        return bool(self.data)

    def __add__(self, other):
        pass
    def __sub__(self, other):
        pass
    def __mul__(self, other):
        pass
    def __truediv__(self, other):
        pass
    def __mod__(self, other):
        pass
    def __lt__(self, other):
        pass
    def __le__(self, other):
        pass
    def __eq__(self, other):
        pass
    def __ne__(self, other):
        pass
    def __gt__(self, other):
        pass
    def __ge__(self, other):
        pass
    def __lshift__(self, other):
        pass
    def __rshift__(self, other):
        pass
    def __and__(self, other):
        pass
    def __xor__(self, other):
        pass
    def __or__(self, other):
        pass
    def __pos__(self):
        pass
    def __neg__(self):
        pass
    def __inv__(self):
        pass
    def __not__(self):
        pass
    def transformed(self, other=None):
        """ method to throw error message """ 
        raise NotImplementedError("Operator should be removed by transforms\n");
    def interpreted(self, other=None):
        """ method to throw error message """ 
        raise NotImplementedError("Operator should be handled by the interpreter\n");

    def __str__(self):
        if self.data is not None:
            return str(self.data)
        return super(ArithmeticValue,self).__str__()

class UnitializedValue(ArithmeticValue):
    """ Type to represent a unitialized value of a certian size """
    bad_use_str = 'Use of a unitialized value'
 
    def __init__(self, size):
        self.size = size
        self.data = None
        self.type_of = 'uninitialized'

    def perform_operation(self, operator, value):
        """Performs operation and returns value."""
        raise Exception(UnitializedValue.bad_use_str)        

    def get_truth_value(self):
        """Returns a bool denoting what truth value the ArithmeticValue would
        have if it were inside of an if statement in C"""
        raise Exception(UnitializedValue.bad_use_str)

    def get_value(self, offset, num_bytes):
        """ Returns 0, should only be valid if called from write """
        return 0
#Todo add class Byte value that is the result of a call to get value 

class BaseInteger(ArithmeticValue):
    """ Abstract Class to represent Integral Types """
    #Every Operator needs to be implemented so no Exceptions Needed
    def __init__(self, data, type_of, size=1):
        pass

class BaseFloat(ArithmeticValue):
    """ Abstract Class for floating types """
    def __lshift__(self, other):
        raise NotImplementedError("Floats do not support a left shift")
    def __rshift__(self, other):
        raise NotImplementedError("Floats do not support a right shift")
    def __and__(self, other):
        raise NotImplementedError("Floats do not support a binary and")
    def __xor__(self, other):
        raise NotImplementedError("Floats do not support a binary xor")
    def __or__(self, other):
        raise NotImplementedError("Floats do not support a binary or")

class ReferenceValue(ArithmeticValue): #pylint:disable=all
    """Abstract Class for polymorphism between Arrays, Pointers, ect."""

