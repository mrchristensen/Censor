"""Classes to represent values, and a function for generating
a value based on an assignment node"""
import cesk.limits as limits

BINOPS = {
    "+" : "__add__",
    "-" : "__sub__",
    "*" : "__mul__",
    "/" : "__truediv__",
    "%" : "__mod__",
    "<" : "__lt__",
    "<=": "__le__",
    "==": "__eq__",
    "!=": "__ne__",
    ">" : "__gt__",
    ">=": "__ge__",
}

class ArithmeticValue: #pylint:disable=too-few-public-methods
    """Abstract class for polymorphism between abstract and concrete values"""
    data = None
    type_of = None
    def perform_operation(self, operator, value): # pylint: disable=inconsistent-return-statements
        """Performs operation and returns value."""
        if operator in BINOPS:
            method = self.__getattribute__(BINOPS[operator])
            return method(value)
        else:
            print("Operator not implemented!")

    def get_truth_value(self):
        """Returns a bool denoting what truth value the ArithmeticValue would have
        if it were inside of an if statement in C"""
        return bool(self.data)

    def __add__(self, other):
        pass

    def __sub__(self, other):
        pass

    def __mul__(self, other):
        pass

    def __truediv__(self, other):
        pass

    def __lt__(self, other):
        return Integer(int(self.data < other.data), 'int')

    def __le__(self, other):
        return Integer(int(self.data <= other.data), 'int')

    def __eq__(self, other):
        return Integer(int(self.data == other.data), 'int')

    def __ne__(self, other):
        return Integer(int(self.data != other.data), 'int')

    def __gt__(self, other):
        return Integer(int(self.data > other.data), 'int')

    def __ge__(self, other):
        return Integer(int(self.data >= other.data), 'int')


class Integer(ArithmeticValue): #pylint:disable=too-few-public-methods
    """Concrete implementation of an Integral Type"""
    max_value = limits.INT_MAX
    min_value = limits.INT_MIN

    def __init__(self, data, type_of):
        self.data = int(data)
        self.type_of = type_of

    def __add__(self, other):
        return Integer(self.data + other.data, self.type_of)

    def __sub__(self, other):
        return Integer(self.data - other.data, self.type_of)

    def __mul__(self, other):
        return Integer(self.data * other.data, self.type_of)

    def __truediv__(self, other):
        return Integer(self.data / other.data, self.type_of)

    def __mod__(self, other):
        return Integer(self.data % other.data, self.type_of)



class Float(ArithmeticValue):  #pylint:disable=too-few-public-methods
    """Concrete implementation of a float.
    NOTE: this class will represent 'float,' and 'double,' and 'long double'
    from C99 as a 64 bit floating point number. This gives some potentially
    incorrect rounding for c programs that use the 'float' or 'long double'
    data types, which is supposed to be represented as a 32 or float."""

    def __init__(self, data, type_of):
        self.data = float(data)
        self.type_of = type_of

    def __add__(self, other):
        return Float(self.data + other.data, self.type_of)

    def __sub__(self, other):
        return Float(self.data - other.data, self.type_of)

    def __mul__(self, other):
        return Float(self.data * other.data, self.type_of)

    def __truediv__(self, other):
        return Float(self.data / other.data, self.type_of)


class Pointer(Integer):  #pylint:disable=too-few-public-methods
    """Concrete implementation of a Pointer to any type."""
    pass


def generate_value(stmt):
    """Given an assignment node, return a value of the correct type"""
    return Integer(stmt.value, stmt.type)
