from cesk.exceptions import CESKException, TransformError

BINOPS = {
    "+" : "__add__",
    "-" : "__sub__",
    "*" : "__mul__", #non reference values
    "/" : "__truediv__", #non reference values
    "%" : "__mod__", #integer values only
    "<" : "__lt__",
    "<=": "__le__",
    "==": "equals",
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
    #data member that should be present in all subclasses
    #data = None #store the value a data type that matches
    #type_of = None #stores the type string
    #size = None #stores the size int

    #should not override
    def perform_operation(self, operator, value):
        """Performs operation and returns value."""
        if isinstance(value, SizedSet):
            result = SizedSet(self.size)
            for val in value:
                result.add(self.perform_operation(operator, val))
            return result
        if operator in BINOPS:
            method = self.__getattribute__(BINOPS[operator])
            return method(value)
        elif operator in UNOPS:
            method = self.__getattribute__(UNOPS[operator])
            return method() #second value is not needed
        else:
            raise TransformError("Unexpected Operation\n")
    def transformed(self, other=None):
        """ method to throw error message """ 
        raise TransformError("Operator should be removed by transforms\n");
    def interpreted(self, other=None):
        """ method to throw error message """ 
        raise TransformError("Operator should be handled by the interpreter\n");
    #Binary and Unary Operators that muxt be overridden
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
    def equals(self, other):
        """ Class to return an BaseInteger representing equals """
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

    #subclasses should implement the functions below if the default is not good enough
    def __str__(self):
        if self.data is not None:
            return str(self.data)
        return super(ArithmeticValue,self).__str__()

    def __eq__(self, other):
        if type(self) == type(other) and self.data == other.data:
            return True
        return False

    def __hash__(self):
        return hash(self.data)

    def get_truth_value(self):
        """Returns a bool denoting what truth value the ArithmeticValue would
        have if it were inside of an if statement in C
        can be true, false or both"""
        return set([bool(self.data)])

    def get_byte_value(self, start=-1, num_bytes=None):
        """ mimics bit values in memory but allows for top or unknown bits """
        pass

    @classmethod
    def from_byte_value(cls, byte_value, type_of):
        """ Takes a ByteValue and a type string and generates an instance of the class """
        pass

    def cast_to_integer(self, to_type):
        """ returns value as integer """
        pass

    def cast_to_float(self, to_type):
        """ returns value as float """
        pass

    def cast_to_pointer(self, to_type):
        """ returns value as pointer """
        pass

class BaseInteger(ArithmeticValue):
    """ Abstract Class to represent Integral Types """
    #Every Operator needs to be implemented so no Exceptions Needed

class BaseFloat(ArithmeticValue):
    """ Abstract Class for floating types """
    def __lshift__(self, other):
        raise TransformError("Floats do not support a left shift")
    def __rshift__(self, other):
        raise TransformError("Floats do not support a right shift")
    def __and__(self, other):
        raise TransformError("Floats do not support a binary and")
    def __xor__(self, other):
        raise TransformError("Floats do not support a binary xor")
    def __or__(self, other):
        raise TransformError("Floats do not support a binary or")
    def cast_to_pointer(self, to_type):
        raise TransformError("Floats can not be cast to pointers")

class ReferenceValue(ArithmeticValue): #pylint:disable=all
    """Abstract Class for polymorphism between Pointers, ect."""
    def cast_to_float(self, to_type):
        raise TransformError("Pointers can not be cast to floats")

    def get_block(self):
        """ Return block identifier """
        return 0

#Special Case values to handle needed gaps
class ByteValue:
    """ Class to represent values of bits from a partial read """
    one = 1
    zero = 0
    top = 2
    def __init__(self, size=0, default_value=2):
        #size in bytes
        self.bits = [default_value]*(size*8)
        self.size = size

    def append(self, other):
        """ increase self by others size and add its bits to self """
        self.size += other.size
        self.bits.extend(other.bits)

    def get_byte_value(self, start=-1, num_bytes=None):
        """ dummy to make casting easier """
        if start == -1:
            return self
        if start+num_bytes > self.size:
            raise CESKException("Request for too many bytes from byte value")
        value = ByteValue()
        value.size = num_bytes
        value.bits = self.bits[start*8:(start+num_bytes)*8]
        return value

    def get_bytes(self):
        """ Results in a bytes-like object of len self.size and top is randomized
            for the pack module used for floats """
        bytes_lst = []
        for byte in range(self.size):
            byte_val = 0
            for bit in range(8):
                if self.bits[byte*8+bit] == ByteValue.one or \
                   (self.bits[byte*8+bit] == ByteValue.top and
                        random.randint(0,1) == 1):
                    byte_val += 2**(7-bit)
            bytes_lst.append(byte_val)
        return bytes(bytes_lst)

    def fromInt(self, int_value):
        """ writes to location equivelent to the unsigned integer value """
        assert(int_value >= 0)
        index = 0
        while index < self.size*8:
            byte = int_value&255
            int_value //= 256
            for i in range(8):
                self.bits[index+(7-i)] = byte & 1
                byte //= 2
            index += 8

    @classmethod
    def fromByte(cls, byte_value):
        """ Takes a int 0-255 and converts to a size 1 byte value """
        assert(byte_value >= 0 and byte_value < 256)
        result = cls(1)
        for index in range(8):
            result.bits[7-index] = byte_value & 1
            byte_value //= 2

        return result

    def __str__(self):
       return str(self.bits)
 
class UnitializedValue(ArithmeticValue):
    """ Type to represent a unitialized value of a certian size """
    bad_use_str = 'Use of a unitialized value'
 
    def __init__(self, size, type_of='uninitialized'):
        self.size = size #in bytes
        self.data = None
        self.type_of = type_of

    def perform_operation(self, operator, value):
        """Performs operation and returns value."""
        raise CESKException(UnitializedValue.bad_use_str)        

    def get_truth_value(self):
        """Returns a bool denoting what truth value the ArithmeticValue would
        have if it were inside of an if statement in C"""
        raise CESKException(UnitializedValue.bad_use_str)

    def get_byte_value(self, offset=-1, num_bytes=None):
        """ Returns x random bytes, should only be valid if called from write """
        return ByteValue(self.size)

    def __str__(self):
        return "Unitialized Value size %d" % self.size

#helper class for the store
class SizedSet(set):
    ''' Set but with the extra feature of knowing the byte size
        of objects stored within, also mirrors some functionality
        of an arithmetic value, but returns sets instead  '''
    def __init__(self, size):
        super().__init__()
        self.size = size

    def get_truth_value(self):
        """ mimic calling truth value on all items in set """
        truth_value = set()
        for value in self:
            truth_value.update(value.get_truth_value())
        if not truth_value:#Empty Set could report error as well
            truth_value.update([True, False])
        return truth_value

    def perform_operation(self, operator, value):
        """ Selects and performs operation on all values in set and in value"""
        result = SizedSet(self.size)
        for left in self:
            if isinstance(value, SizedSet):
                for right in value:
                    result.add(left.perform_operation(operator, right))
            else:
                result.add(left.perform_operation(operator, value))
        return result

    def get_byte_value(self, offset=-1, num_bytes=None):
        """ Gets all values as their byte value """
        byte_values = SizedSet(self.size)
        for value in self:
            byte_values.add(value.get_byte_value(offset, num_bytes))
        return byte_values

    def __str__(self):
        result = []
        for item in self:
            result.append(str(item))
        return '{' + ','.join(result) + '}'

    #def get_byte_value
    #def from_byte_value not possible
