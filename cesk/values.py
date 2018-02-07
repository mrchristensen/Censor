"""Classes to represent values, and a function for generating
a value based on an assignment node"""

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


class ConcreteValue(Value): #pylint:disable=too-few-public-methods
    """Concrete implementation of Value"""
    data = None
    type_of = None

    def __init__(self, data, type_of):
        self.data = int(data)
        self.type_of = type_of

    def __add__(self, other):
        return ConcreteValue(self.data + other.data, self.type_of)

    def __sub__(self, other):
        return ConcreteValue(self.data - other.data, self.type_of)

    def __mul__(self, other):
        return ConcreteValue(self.data * other.data, self.type_of)

    def __truediv__(self, other):
        return ConcreteValue(self.data / other.data, self.type_of)


def generate_value(stmt):
    """Given an assignment node, return a value of the correct type"""
    return ConcreteValue(stmt.value, stmt.type)
