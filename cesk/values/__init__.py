"""Classes to represent values, and a function for generating
a value based on an assignment node"""
import logging
import pycparser.c_ast as AST
from cesk.linksearch import get_sizes
import cesk.config
from cesk.values import base_values as BV
import cesk.limits as limits
from cesk.exceptions import CESKException
from .factory import Factory


def string_constant(value):
    """ handle makeing a const string constant """
    #TODO this needs a better implementation so as to be able to copy or
    #   read at an index
    return value, 'string'
    #raise NotImplementedError("Need to implement string constant")
    #return PtrDecl([], TypeDecl(None, [], IdentifierType(['char'])))

def float_constant(value):
    """ handle makeing a const float constant """
    if value[-1] in "fF":
        return float(value[:-1]), 'float'
    elif value[-1] in "lL":
        return float(value), 'long double'
    else:
        return float(value), 'double'

def int_constant(value):
    """ handle makeing a const int constant """
    unsigned = ''
    type_of = 'int'
    if value[-1] in "uU":
        unsigned = 'unsigned '
        value = value[:-1]
    if value[-1] not in "lL":
        val = int(value, 0)
        if val <= limits.RANGES['unsigned '+type_of].max:
            return val, unsigned+type_of
    else:
        value = value[:-1]
    type_of = 'long '+type_of
    val = int(value, 0)

    if val <= limits.RANGES['unsigned '+type_of].max:
        return val, unsigned+type_of
    type_of = 'long '+type_of
    if val <= limits.RANGES['unsigned '+type_of].max:
        return val, unsigned+type_of

def char_constant(value):
    """ handle makeing a const char constant """
    if isinstance(value, str):
        if len(value) == 1:
            return ord(value), 'char'
        if value[0] == "'":
            return char_constant(value[1:-1])
        if value[0] == "\\":
            return int(value[1:]), 'char'
    return value, 'char'

# needs to know what size it needs to be sometimes
def generate_constant_value(value, type_of='int'):
    """ Given a string, parse it as a constant value. """
    if type_of == 'string':
        #raise CESKException("implementation needed for general use of strings")
        return string_constant(value)[0]
    elif type_of == 'float' or type_of == 'double':
        return Factory.Float(*float_constant(value))
    elif type_of == 'int':
        logging.debug(value)
        return Factory.Integer(*int_constant(value))
    elif type_of == 'char':
        return Factory.Char(*char_constant(value))

    raise CESKException("Unkown Constant Type %s"%type_of)


def generate_value(value, type_of):
    """ given value in bits and type_of as string, size for special cases
        special cases include pointer, bit_value, uninitialized """
    if not isinstance(value, BV.ByteValue):
        raise CESKException("BV.ByteValue must be passed into generate_value")

    if "char" in type_of:
        return Factory.getCharClass().from_byte_value(value, type_of)
    if type_of in limits.RANGES:
        return Factory.getIntegerClass().from_byte_value(value, type_of)
    if "float" in type_of or "double" in type_of:
        return Factory.getFloatClass().from_byte_value(value, type_of)

    if type_of == 'pointer':
        #TODO change to be a pointer offset from null
        raise CESKException(
            'Pointer not expected here/not valid to create dynamically')

    if type_of == 'uninitialized' or type_of == 'bit_value':
        #debate whether this should return an Integer or BV.ByteValue
        #if BV.ByteValue a few more functions need to be added or
        #if unitialized was an option for individual types rather than a group
        return Factory.getIntegerClass().from_byte_value(value, 'bit_value')

    raise CESKException("Unexpected value type %s"%type_of)

def generate_unitialized_value(size):
    """ Generates special value that is unitialized but has a size """
    return BV.UnitializedValue(size)


def generate_default_value(size):
    """Generates a default value of the given size (used for uninitialized
    variables)."""
    value = Factory.Integer(0, 'bit_value', size)
    return value

def generate_function_definition(node):
    '''Wraps node in a function definition'''
    return Factory.FunctionDefinition(node)

def generate_pointer(address, size):
    """Given a address (int) package it into a pointer"""
    return Factory.Pointer(address, size, 0)

def copy_pointer(pointer, ptr_type=None):
    """ Given a point a type and the state
        generate the cast if needed pointer (shallow copy of pointer) """
    if ptr_type is None:
        size = pointer.type_size
    else: #cast to ptr of different type
        sizes = []
        get_sizes(ptr_type, sizes)  # returns alignment
        size = sum(sizes)
    return Factory.Pointer(pointer.data, size, pointer.offset)

def generate_null_pointer():
    """ Build a pointer that will not dereference """
    return Factory.Pointer(0, 1)

#value is the value to be cast ( I think )
#typedeclt is the type to cast to ( I think )
#state (cesk state)
def cast(value, typedeclt, state=None):  # pylint: disable=unused-argument
    """Casts the given value a  a value of the given type."""
    result = value
    #Int -> Int
    #Int -> Pointer
    #Int -> Float

    #Float -> Int
    #Float -> Float

    #Pointer -> Int
    #Pointer -> Pointer

    #BV.ByteValue -> ALL
    if isinstance(typedeclt, AST.Typename):
        return cast(value, typedeclt.type, state)

    if isinstance(value, BV.SizedSet):
        sizes = []
        get_sizes(typedeclt, sizes)  # returns alignment
        size = sum(sizes)
        result = BV.SizedSet(size)
        for item in value:
            new_item = cast(item, typedeclt, state)
            result.add(new_item)
    #typedeclt could be a PtrDecl in the c_ast
    elif isinstance(typedeclt, AST.PtrDecl):
        #value could be a baseValue(see base_values.py) of ReferenceValue
        if isinstance(value, BV.ReferenceValue):
            result = copy_pointer(value, typedeclt.type) #P ->
        #value could be a BaseInteger, if it is, it shouldn't be?
        #by the end, this should be unnecessary?
        elif isinstance(value, BV.BaseInteger): #I -> P
            # normal number being turned into a pointer not valid to dereference
            # TODO manage tracking of this
            address = state.stor.get_nearest_address(value.data)
            result = copy_pointer(address, typedeclt.type)
        elif isinstance(value, BV.ByteValue):
            address = state.stor.get_nearest_address(
                generate_value(value, "long").data)
            result = copy_pointer(address, typedeclt.type)
    #typedeclt is any TypeDecl in c_ast
    elif isinstance(typedeclt, AST.TypeDecl):
        if isinstance(typedeclt.type, AST.IdentifierType):
            types = typedeclt.type.names
            byte_value = value.get_byte_value()
            logging.debug(byte_value)
            result = generate_value(byte_value, " ".join(types))
        else:
            #TODO do this the right way, the rest of casting as well
            #this is a temperary measure for struct and union casts
            result = value
    else:
        logging.error('\tUnsupported cast: %s', str(typedeclt.type))
        raise CESKException("Unsupported cast")

    logging.debug("Cast %s to %s", str(value), str(result))
    return result
