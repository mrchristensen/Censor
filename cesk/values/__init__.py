"""Classes to represent values, and a function for generating
a value based on an assignment node"""
import cesk.limits as limits
import pycparser
import logging
from pydoc import locate
import cesk.linksearch as ls

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
        return ConcreteInteger(int(self.data < other.data), 'int')
        #pass
    def __le__(self, other):
        return ConcreteInteger(int(self.data <= other.data), 'int')
        #pass
    def __eq__(self, other):
        #pass
        return ConcreteInteger(int(self.data == other.data), 'int')
    def __ne__(self, other):
        #pass
        return ConcreteInteger(int(self.data != other.data), 'int')
    def __gt__(self, other):
        #pass
        return ConcreteInteger(int(self.data > other.data), 'int')
    def __ge__(self, other):
        #pass
        return ConcreteInteger(int(self.data >= other.data), 'int')
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
        if self.data:
            return "(" + self.type_of + ") " + str(self.data)
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

class Integer(ArithmeticValue):
    """ Abstract Class to represent Integral Types """
    #Every Operator needs to be implemented so no Exceptions Needed
    def __init__(self, data, type_of, size=1):
        pass

class Float(ArithmeticValue):
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

class ConcreteInteger(Integer): #pylint:disable=too-few-public-methods
    """Concrete implementation of an Integral Type"""

    def __init__(self, data, type_of, size=1):
        if type_of is 'bit_value':
            self.type_of = type_of
            self.size = size
            self.min_value = 0
            self.max_value = 2**size - 1 
            self.data = int(data)
        else:
            self.type_of = type_of
            self.size = limits.CONFIG.get_size(type_of.split())
            self.min_value, self.max_value = limits.RANGES[type_of]
            self.data = self.bound(data)

    def __add__(self, other):
        value = self.bound(self.data + other.data)
        return ConcreteInteger(value, self.type_of, self.size)

    def __sub__(self, other):
        value = self.bound(self.data - other.data)
        return ConcreteInteger(value, self.type_of, self.size)

    def __mul__(self, other):
        value = self.bound(self.data * other.data)
        return ConcreteInteger(value, self.type_of, self.size)

    def __truediv__(self, other):
        value = self.bound(self.data // other.data)
        return ConcreteInteger(value, self.type_of, self.size)

    def __mod__(self, other):
        value = self.bound(self.data % other.data)
        return ConcreteInteger(value, self.type_of, self.size)

    def bound(self, value):
        """ Simulates two's complement overflow of integral types """
        n = value - self.min_value
        m = self.max_value - self.min_value + 1
        k = n % m
        x = k + self.min_value
        return x

    def get_value(self, start=-1, num_bytes=None):
        """value of the unsigned bits stored"""
        result = self.data
        if self.data < 0:
            result += self.max_value - self.min_value + 1
            #result +=  pow(2,(self.size*8))
        if ((start == -1) or
                (start == 0 and num_bytes == self.size)):
            #Get all of the bytes
            return result

        result //= 2**(start*8)
        result %= pow(2, num_bytes*8)

        return result

class Char(ConcreteInteger):
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

class ConcreteFloat(Float):  #pylint:disable=too-few-public-methods
    """Concrete implementation of a float.
    NOTE: this class will represent 'float,' and 'double,' and 'long double'
    from C99 as a 64 bit floating point number. This gives some potentially
    incorrect rounding for c programs that use the 'float' or 'long double'
    data types, which is supposed to be represented as a 32 or float."""

    def __init__(self, data, type_of):
        self.data = float(data)
        self.type_of = type_of
        self.size = limits.CONFIG.get_size(type_of.split())

    def __add__(self, other):
        return ConcreteFloat(self.data + other.data, self.type_of)

    def __sub__(self, other):
        return ConcreteFloat(self.data - other.data, self.type_of)

    def __mul__(self, other):
        return ConcreteFloat(self.data * other.data, self.type_of)

    def __truediv__(self, other):
        return ConcreteFloat(self.data / other.data, self.type_of)

    def get_value(self, start=-1, num_bytes=None):
        """value of the unsigned bits stored"""
        #TODO get binary value
        return self.data

class ReferenceValue(ArithmeticValue): #pylint:disable=all
    """Abstract Class for polymorphism between Arrays, Pointers, ect."""

class Pointer(ReferenceValue):  #pylint:disable=too-few-public-methods
    """Concrete implementation of a Pointer to a store address."""

    def __init__(self, address, type_size, offset=0):
        self.data = int(address)
        self.size = limits.CONFIG.get_word_size()
        self.type_size = type_size
        self.offset = offset
        self.type_of = 'pointer'

    def __hash__(self):
        return self.data

    def __eq__(self, other):
        if not isinstance(other, ReferenceValue):
            return ConcreteInteger(0, 'int')
        return ConcreteInteger(int(self.data == other.data), 'int')

    def update(self, stor):
        """ moves the pointer along the pred and succ map """
        #if self.offset < 0 or self.offset >= self.type_size:
        offset = self.offset
        self.offset = 0
        ptr = stor.add_offset_to_pointer(self, offset)
        self.offset = ptr.offset
        self.data = ptr.data

    def __add__(self, other):
        ptr = copy_pointer(self)
        if isinstance(other, ConcreteInteger):
            ptr.offset += other.data
        elif isinstance(other, int):
            ptr.offset += other
        else:
            raise Exception("Pointers can only be added to int")
        return ptr

    def __sub__(self, other):
        ptr = copy_pointer(self)

        if isinstance(other, ConcreteInteger):
            ptr.offset += -1 * other.data
            return ptr
        elif isinstance(other, int):
            ptr.offset += -1 * other
            return ptr
        elif isinstance(other, Pointer):
            return ConcreteInteger((self.get_value() - other.get_value()), 'int')
        else:
            raise Exception("Pointers can only be subtracted by int")

    def __str__(self):
        return 'Pointer at '+str(self.data)+'.'+str(self.offset) +\
                ' size '+ str(self.type_size)

    def get_value(self, start=-1, num_bytes=None):
        """ value of the unsigned bits stored from start to start+num_bytes """
        result = self.data + self.offset
        if self.data < 0:
            result += pow(2, self.size)
        if ((start == -1) or
                (start == 0 and num_bytes == self.size)):
            return result

        result //= 2**(start*8)
        result %= pow(2, num_bytes*8)

        return result

class FrameAddress:
    """ Contains a link between frame and id """

    def __init__(self, frame_id, ident):
        self.frame = frame_id
        self.ident = ident
        #super(FrameAddress, self).__init__(0, 1)

    def get_frame(self):
        """ Returns frame identifier """
        return self.frame

    def get_id(self):
        """ Returns identifier name """
        return self.ident

    def __hash__(self):
        return 1+43*hash(self.ident)+73*hash(self.frame)

    def __eq__(self, other):
        if not isinstance(other, FrameAddress):
            return False
        return self.ident == other.ident and self.frame == other.frame


# needs to know what size it needs to be sometimes
def generate_constant_value(value, type_of='int'):
    """ Given a string, parse it as a constant value. """
    if type_of == 'string':
        raise NotImplementedError("Need to implement string constant")
        #return PtrDecl([], TypeDecl(None, [], IdentifierType(['char'])))
    elif type_of == 'float':
        if value[-1] in "fF":
            return ConcreteFloat(value,'float')
        elif value[-1] in "lL":
            return ConcreteFloat(value,'long double')
        else:
            return ConcreteFloat(value, 'double') 
    elif type_of == 'int':
        u = ''
        if value[-1] in "uU":
            u = 'unsigned '
            value = value[:-1]
        if value[-1] not in "lL":
            val = int(value, 0)
            if val <= limits.RANGES['unsigned '+type_of].max:
                return ConcreteInteger(val, u+type_of)
        else:
            value = value[:-1]
        type_of = 'long '+type_of
        val = int(value, 0)

        if val <= limits.RANGES['unsigned '+type_of].max:
            return ConcreteInteger(val, u+type_of)
        type_of = 'long '+type_of
        if val <= limits.RANGES['unsigned '+type_of].max:
            return ConcreteInteger(val, u+type_of)

    elif type_of == 'char':
        return Char(value, type_of)

    raise Exception("Unkown Constant Type %s", type_of)


def generate_value(value, type_of='bit_value', size=None):
    """ given value in bits and type_of as string, size for special cases 
        special cases include pointer, bit_value, uninitialized """
    if "char" in type_of:
        return Char(value, type_of)
    if type_of in limits.RANGES:
        return ConcreteInteger(value, type_of)
    if "float" in type_of or "double" in type_of:
        return ConcreteFloat(value, type_of)
    if type_of == 'bit_value':
        return ConcreteInteger(value, type_of, size)

    if type_of == 'pointer':
        raise Exception('Pointer not expected here/not valid to change dynamically')

    if type_of == 'uninitialized':
        return ConcreteInteger(value, 'bit_value', size)

    raise Exception("Unexpected value type %s",type_of)

def generate_unitialized_value(size):
   """ Generates special value that is unitialized but has a size """
   return UnitializedValue(size)

def generate_default_value(size):
    """Generates a default value of the given size (used for uninitialized
    variables)."""
    value = ConcreteInteger(0, 'bit_value', size)
    return value


def generate_pointer(address, size):
    """Given a address (int) package it into a pointer"""
    return Pointer(address, size, 0)

def copy_pointer(pointer, ptr_type=None):
    """ Given a point a type and the state
        generate the cast if needed pointer (shallow copy of pointer) """
    if ptr_type is None:
        size = pointer.type_size
    else: #cast to ptr of different type
        sizes = []
        ls.get_sizes(ptr_type, sizes) #returns alignment
        size = sum(sizes)
    return Pointer(pointer.data, size, pointer.offset)

def generate_null_pointer():
    """ Build a pointer that will not dereference """
    return Pointer(0, 1)

def generate_frame_address(frame, ident):
    """ Build a Frame Address """
    return FrameAddress(frame, ident)

def cast(value, typedeclt, state=None): #pylint: disable=unused-argument
    """Casts the given value a  a value of the given type."""
    result = None

    if isinstance(typedeclt, pycparser.c_ast.Typename):
        result = cast(value, typedeclt.type, state)
    elif isinstance(typedeclt, pycparser.c_ast.PtrDecl):
        if isinstance(value, ReferenceValue): 
            result = copy_pointer(value, typedeclt.type)
        else:
            #normal number being turned into a pointer not valid to dereference
            #TODO manage tracking of this
            logging.debug(" Cast %s to %s", str(value), str(typedeclt))
            address = state.stor.get_nearest_address(value.data)
            result = copy_pointer(address, typedeclt.type)
    elif isinstance(typedeclt, pycparser.c_ast.TypeDecl):
        types = typedeclt.type.names
        result = generate_value(value.get_value(), " ".join(types))
    else:
        logging.error('\tUnsupported cast: ' + str(typedeclt.type))
        raise Exception("Unsupported cast")
    
    assert result.data != None
    return result
