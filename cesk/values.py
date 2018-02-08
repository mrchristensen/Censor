"""Classes to represent values, and a function for generating
a value based on an assignment node"""
import cesk.limits as limits

class Value: #pylint:disable=too-few-public-methods
    """Abstract class for polymorphism between abstract and concrete values"""

    def perform_operation(self, operator, value): # pylint: disable=inconsistent-return-statements
        """Performs operation and returns value."""
        if operator == "+":
            return self + value
        elif operator == "-":
            return self - value
        elif operator == "*":
            return self * value
        elif operator == "/":
            return self / value
        else:
            print("Operator not implemented!")

    def __add__(self, other):
        pass

    def __sub__(self, other):
        pass

    def __mul__(self, other):
        pass

    def __div__(self, other):
        pass


class Integer(Value): #pylint:disable=too-few-public-methods
    """Concrete implementation of an Integral Type"""
    data = None
    type_of = None
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


class Pointer(Value):  #pylint:disable=too-few-public-methods
    """Concrete implementation of a Pointer to any type."""
    address = 0

    def __init__(self, data, type_of):
        pass




def generate_value(stmt):
    """Given an assignment node, return a value of the correct type"""
    print(stmt)
    stmt.show()
    return Integer(stmt.value, stmt.type)
