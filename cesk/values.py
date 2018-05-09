"""Classes to represent values, and a function for generating
a value based on an assignment node"""
import cesk.limits as limits
from pydoc import locate
import pycparser

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
    def bound(self, value):
        while value > self.max_value or value < self.min_value:
            if value > self.max_value:
                value = self.min_value + value - self.max_value - 1
            elif value < self.min_value:
                value = self.max_value + value - self.min_value + 1
        return value
    
    def __init__(self, data, type_of):
        self.min_value, self.max_value = limits.RANGES[type_of]
        self.data = self.bound(int(data))
        self.type_of = type_of

    def __add__(self, other):
        value = self.bound(self.data + other.data)
        return Integer(value, self.type_of)

    def __sub__(self, other):
        value = self.bound(self.data - other.data)
        return Integer(value, self.type_of)

    def __mul__(self, other):
        value = self.bound(self.data * other.data)
        return Integer(value, self.type_of)

    def __truediv__(self, other):
        value = self.bound(self.data // other.data)
        return Integer(value, self.type_of)

    def __mod__(self, other):
        value = self.bound(self.data % other.data)
        return Integer(value, self.type_of)


class Char(Integer):
    """Concrete implementation of an char Type"""
    def __init__(self, data, type_of='char'):
        super().__init__(ord(data), type_of)

    def __add__(self, other):
        value = chr(super().__add__(other).data)
        return Char(value, self.type_of)

    def __sub__(self, other):
        value = chr(super().__sub__(other).data)
        return Char(value, self.type_of)

    def __mul__(self, other):
        value = chr(super().__mul__(other).data)
        return Char(value, self.type_of)

    def __truediv__(self, other):
        value = chr(super().__truediv__(other).data)
        return Char(value, self.type_of)

    def __mod__(self, other):
        value = chr(super().__mod__(other).data)
        return Char(value, self.type_of)

    def get_char(self) -> str: 
        return chr(self.data)


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


class ReferenceValue(ArithmeticValue): #pylint:disable=all
    """Abstract Class for polymorphism between Arrays, Pointers, ect."""

    def dereference(self, stor):
        pass

    def index(self, stor, list_of_index):
        pass

    def index_for_address(self, stor, list_of_index):
        pass


class Pointer(ReferenceValue):  #pylint:disable=too-few-public-methods
    """Concrete implementation of a Pointer to any type."""

    def __init__(self, address, holding_stor):
        self.address = int(address)
        self.holding_stor = holding_stor

    def __hash__(self):
        return self.address
    
    def __eq__(self, other):
        if not isinstance(other, ReferenceValue):
            return Integer(0, 'int')
        return Integer(int(self.address == other.address), 'int')

    def dereference(self):
        """Reads the address the pointer points to and returns value"""
        if self.address == 0:
            raise Exception("SegFault")
        return self.holding_stor.read(self.address)

    def index(self, stor, list_of_index):
        """Reads the address with a given offset from the pointer"""
        return self.index_for_address(list_of_index).dereference()

    def index_for_address(self, list_with_offset):
        """Finds the address with a given offset from the pointer"""
        if len(list_with_offset) != 1:
            raise Exception("Invalid ArrayRef on Pointer")
        offset = list_with_offset[0]
        return self.holding_stor.add_offset_to_pointer(self, offset)

    def __add__(self, other):
        if isinstance(other, Integer):
            offset = other.data
        elif isinstance(other, int):
            offset = other
        else:
            raise Exception("Pointers can only be added to int")
        return self.holding_stor.add_offset_to_pointer(self, offset)

    def __sub__(self, other):
        if isinstance(other, Integer):
            offset = -1 * other.data
        elif isinstance(other, int):
            offset = -1 * other
        else:
            raise Exception("Pointers can only be subtracted by int")
        return self.holding_stor.add_offset_to_pointer(self, offset)

class Array(ReferenceValue):
    """Concrete implementation of an Array of data"""

    def __init__(self, start_address, list_of_sizes, stor):
        if not isinstance(start_address, ReferenceValue):
            raise Exception("start_address should be Pointer not " +
                            str(start_address));
        self.start_address = start_address
        self.list_of_sizes = list_of_sizes
        self.stor = stor

    def dereference(self):
        """Reads the first item of the array"""
        return self.start_address.dereference()

    def index(self, stor, list_of_index):
        """Gets the object at a given index of an array. A[1][2]...[n]"""
        address = self.index_for_address(list_of_index)
        if len(self.list_of_sizes) > len(list_of_index):
            remaining_sizes = self.list_of_sizes[-len(list_of_index):]
            return generate_array(address, remaining_sizes, self.stor)

        return address.dereference()

    def index_for_address(self, list_of_index):
        """Calculates stride and finds the address for a given index"""
        if len(self.list_of_sizes) < len(list_of_index):
            raise Exception("Invalid ArrayRef on Array")
        offset = 0
        #TODO give a nice comment here
        for i in range(len(list_of_index)):
            stride = 1
            for j in range(i+1, len(self.list_of_sizes)):
                stride = stride * self.list_of_sizes[j]
            offset = offset + list_of_index[i] * stride
        return self.start_address + offset

def generate_constant_value(value, typ='int'):
    """Given a string, parse it as a constant value."""
    # TODO: also parse constant chars
    if "." in value:
        return Float(value, 'float')
    return Integer(value, typ)

def generate_default_value(typedecl): #pylint: disable=unused-argument
    """Generates a default value of the given type (used for uninitialized
    variables)."""
    # TODO
    return Integer(0, typedecl)

def generate_pointer_value(address, stor):
    """Given a address (int) package it into a pointer"""
    return Pointer(address, stor)

def generate_null_pointer():
    return Pointer(0, None)

def generate_array(start_address, list_of_sizes, stor):
    #TODO this does not properly handle graph based stor
    return Array(start_address, list_of_sizes, stor)

def cast(value, typedeclt): #pylint: disable=unused-argument
    """Casts the given value a  a value of the given type."""
    #TODO move the check for pycparser type to the function that calls cast so only an IdentifierType object is passed in
    #print('typedecl.type: ' + str(typedeclt.type))    
    print('Data: '+str(value.data))
    m = value.data
    if isinstance(typedeclt.type, pycparser.c_ast.IdentifierType):
        s = typedeclt.type.names[0]
        print('Cast from IdentifierType')
    else:
        print('Cast from other: '+str(typedeclt.type))
        s = typedeclt.type.type.names[0]
    if s == 'int':
        n = Integer(m, 'int')
    elif s == 'float':
        n = Float(m, 'float')
    #print(n.data)
    
    return n 
