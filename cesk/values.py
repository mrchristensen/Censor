"""Classes to represent values, and a function for generating
a value based on an assignment node"""
import cesk.limits as limits
import pycparser
import logging
from pydoc import locate

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

class ArithmeticValue:
    """Abstract class for polymorphism between abstract and concrete values"""
    data = None
    type_of = None
    def perform_operation(self, operator, value):
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

    def __str__(self):
        if self.data is not None:
            return "(" + self.type_of + ") " + str(self.data)
        return super(ArithmeticValue,self).__str__() 


class Integer(ArithmeticValue): #pylint:disable=too-few-public-methods
    """Concrete implementation of an Integral Type"""
    def bound(self, value):
        # TODO document
        n = value - self.min_value
        m = self.max_value - self.min_value + 1
        k = n % m
        x = k + self.min_value
        return x
    
    def __init__(self, data, type_of):
        assert type_of != None
        self.type_of = type_of
        self.min_value, self.max_value = limits.RANGES[type_of]
        self.data = self.bound(int(data))

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
        if isinstance(data, str) and ('\'' in data):
            char = data.replace("\'", "")
            v = ord(char)
        else:
            v = data
        super().__init__(v, type_of)

    def __add__(self, other):
        value = super().__add__(other).data
        return Char(value, self.type_of)

    def __sub__(self, other):
        value = super().__sub__(other).data
        return Char(value, self.type_of)

    def __mul__(self, other):
        value = super().__mul__(other).data
        return Char(value, self.type_of)

    def __truediv__(self, other):
        value = super().__truediv__(other).data
        return Char(value, self.type_of)

    def __mod__(self, other):
        value = super().__mod__(other).data
        return Char(value, self.type_of)

    def get_char(self): 
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

    # TODO Dallin: Check with Kyle, refused bequest.  Check Array
    def __init__(self, address, holding_stor):
        # self.address changed to self.data so that all the same functionality is present
        self.data = int(address)
        self.stor = holding_stor
        self.offset = 0 #stores the offset from the address of the 

    def __hash__(self):
        return self.data

    def __eq__(self, other):
        if not isinstance(other, ReferenceValue):
            return Integer(0, 'int')
        return Integer(int(self.data == other.data), 'int')
    
    def dereference(self):
        """Reads the address the pointer points to and returns value"""
        if self.data == 0:
            raise Exception("SegFault")
        return self.stor.read(self.data)

    def index(self, stor, list_of_index):
        """Reads the address with a given offset from the pointer"""
        return self.index_for_address(list_of_index).dereference()

    def index_for_address(self, list_with_offset):
        """Finds the address with a given offset from the pointer"""
        if self.data == 0:
            raise Exception("SegFault")
        if len(list_with_offset) != 1:
            raise Exception("Invalid ArrayRef on Pointer")
        offset = list_with_offset[0]
        return self.stor.add_offset_to_pointer(self, offset)

    def __add__(self, other):
        if self.data == 0:
            return self
        if isinstance(other, Integer):
            offset = other.data
        elif isinstance(other, int):
            offset = other
        else:
            raise Exception("Pointers can only be added to int")
        return self.stor.add_offset_to_pointer(self, offset)

    def __sub__(self, other):
        if isinstance(other, Integer):
            offset = -1 * other.data
            return self.stor.add_offset_to_pointer(self, offset)
        elif isinstance(other, int):
            offset = -1 * other
            return self.stor.add_offset_to_pointer(self, offset)
        elif isinstance(other, Pointer):
            return self.data - other.data
        else:
            raise Exception("Pointers can only be subtracted by int")

    def __str__(self):
        return '<cesk.values.Pointer> at '+str(self.data)

#Should not nead any more
#class Array(ReferenceValue):
#    """Concrete implementation of an Array of data"""
#
#    def __init__(self, start_address, list_of_sizes, stor):
#        if not isinstance(start_address, ReferenceValue):
#            raise Exception("start_address should be Pointer not " +
#                            str(start_address))
#        self.start_address = start_address
#        self.list_of_sizes = list_of_sizes
#        self.stor = stor
#
#    def dereference(self):
#        """Reads the first item of the array"""
#        if len(self.list_of_sizes) > 1:
#            return self.start_address #could change this to return an array type    
#        return self.start_address.dereference()
#
#    def index(self, stor, list_of_index):
#        """Gets the object at a given index of an array. A[1][2]...[n]"""
#        address = self.index_for_address(list_of_index)
#        if len(self.list_of_sizes) > len(list_of_index):
#            remaining_sizes = self.list_of_sizes[-len(list_of_index):]
#            return generate_array(address, remaining_sizes, self.stor)
#
#        return address.dereference()
#
#    def index_for_address(self, list_of_index):
#        """Calculates stride and finds the address for a given index"""
#        
#        if len(self.list_of_sizes) < len(list_of_index):
#            raise Exception("Invalid ArrayRef on Array")
#        offset = 0
#        #the for loop calculates how many posistions to jump of a given set of indices and sizes of the subsections in the array
#        num_indices = len(list_of_index)
#        for i in range(num_indices):
#            stride = 1
#            for j in range(i+1, len(self.list_of_sizes)):
#                stride = stride * self.list_of_sizes[j]
#            offset = offset + list_of_index[i] * stride
#
#        #if less indices are given than are in the list of sizes it still needs to be treated as an array
#        if num_indices < len(self.list_of_sizes):
#            temp_address = self.stor.get_next_address()
#            new_temp_array = generate_array(self.start_address+offset,self.list_of_sizes[num_indices-1:-1],self.stor)
#            self.stor.write(temp_address, new_temp_array)
#            return temp_address
#
#        return self.start_address + offset
#
#    def __add__(self, other):
#        if isinstance(other, Integer):
#            offset = other.data
#        elif isinstance(other, int):
#            offset = other
#        else:
#            raise Exception("Pointers can only be added to int")
#        return self.stor.add_offset_to_pointer(self.start_address, offset)
#    
#    def __sub__(self, other):
#        if isinstance(other, Integer):
#            offset = -1 * other.data
#        elif isinstance(other, int):
#            offset = -1 * other
#        else:
#            raise Exception("Pointers can only be added to int")
#        return self.stor.add_offset_to_pointer(self.start_address, offset)
#
#
#
#    def __str__(self):
#        return '(Array) at '+str(self.start_address)


class Struct:
    def __init__(self,address,decls,stor):
        self.values = {}
        self.stor = stor
        self.data = address
        
        offset = 0
        for decl in decls:
            self.values[decl.name] = offset
            offset += 1
    
    def get_value(self, name):
        if name in self.values:
            return self.data + self.values[name]
        else:
            raise Exception(str(name)+' not found in struct') 


# TODO Dallin: discuss default type_of with Kyle
def generate_constant_value(value, type_of='int'):
    """Given a string, parse it as a constant value."""
    if "char" in type_of:
        return Char(value, type_of)
    if "float" in type_of:
        return Float(value, type_of)
    return Integer(value, type_of)


def generate_default_value(typedecl): #pylint: disable=unused-argument
    """Generates a default value of the given type (used for uninitialized
    variables)."""
    return generate_constant_value(0, typedecl)


def generate_pointer_value(address, stor):
    """Given a address (int) package it into a pointer"""
    return Pointer(address, stor)


def generate_null_pointer():
    return Pointer(0, None)


def generate_array(start_address, list_of_sizes, stor):
    #TODO this does not properly handle graph based stor
    return Array(start_address, list_of_sizes, stor)


def generate_struct(start_address, decls, stor):
    return Struct(start_address, decls, stor)


def cast(value, typedeclt, store=None): #pylint: disable=unused-argument
    """Casts the given value a  a value of the given type."""
    n = None
    #logging.debug('CAST: '+str(value)+" to type "+str(typedeclt))

    if isinstance(typedeclt, pycparser.c_ast.Typename):
        n = cast(value, typedeclt.type)
    elif isinstance(typedeclt, pycparser.c_ast.PtrDecl):
        # TODO This code may need to be more thoroughly tested
        # TODO Document well, include questions about more obscure test cases
        if isinstance(value, ReferenceValue): 
            address = value.data
            n = generate_pointer_value(address, value.stor)
        else:
            address = value.data
            n = generate_pointer_value(address, store)
    elif isinstance(typedeclt, pycparser.c_ast.TypeDecl):
        s = typedeclt.type.names
        n = generate_constant_value(str(value.data), " ".join(s))
    else:
        logging.error('\tUnsupported cast: ' + str(typedeclt.type))
        raise Exception("Unsupported cast")
    
    assert n.data != None
    return n 
