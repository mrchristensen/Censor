"""Classes to represent values, and a function for generating
a value based on an assignment node"""
import pycparser
import logging
from cesk.linksearch import get_sizes
import cesk.config
from cesk.values import base_values as BV #import BV.ReferenceValue, BV.UnitializedValue, BV.ByteValue
import cesk.limits as limits
from .factory import Factory

# needs to know what size it needs to be sometimes
def generate_constant_value(value, type_of='int'):
    """ Given a string, parse it as a constant value. """
    if type_of == 'string':
        raise NotImplementedError("Need to implement string constant")
        #return PtrDecl([], TypeDecl(None, [], IdentifierType(['char'])))
    elif type_of == 'float':
        if value[-1] in "fF":
            return Factory.Float(value[:-1], 'float')
        elif value[-1] in "lL":
            return Factory.Float(value, 'long double')
        else:
            return Factory.Float(value, 'double')
    elif type_of == 'int':
        u = ''
        if value[-1] in "uU":
            u = 'unsigned '
            value = value[:-1]
        if value[-1] not in "lL":
            val = int(value, 0)
            if val <= limits.RANGES['unsigned '+type_of].max:
                return Factory.Integer(val, u+type_of)
        else:
            value = value[:-1]
        type_of = 'long '+type_of
        val = int(value, 0)

        if val <= limits.RANGES['unsigned '+type_of].max:
            return Factory.Integer(val, u+type_of)
        type_of = 'long '+type_of
        if val <= limits.RANGES['unsigned '+type_of].max:
            return Factory.Integer(val, u+type_of)

    elif type_of == 'char':
        return Factory.Char(value, type_of)

    raise Exception("Unkown Constant Type %s", type_of)


def generate_value(value, type_of):
    """ given value in bits and type_of as string, size for special cases 
        special cases include pointer, bit_value, uninitialized """
    if not isinstance(value, BV.ByteValue):
        raise Exception("BV.ByteValue must be passed into generate_value")

    if "char" in type_of:
        return Factory.getCharClass().from_byte_value(value, type_of)
    if type_of in limits.RANGES:
        return Factory.getIntegerClass().from_byte_value(value, type_of)
    if "float" in type_of or "double" in type_of:
        return Factory.getFloatClass().from_byte_value(value, type_of)

    if type_of == 'pointer':
        raise Exception(
            'Pointer not expected here/not valid to change dynamically')

    if type_of == 'uninitialized' or type_of == 'bit_value':
        #debate whether this should return an Integer or BV.ByteValue
        #if BV.ByteValue a few more functions need to be added
        #or if unitialized was an option for individual types rather than a group
        return Factory.getIntegerClass().from_byte_value(value, 'bit_value')

    raise Exception("Unexpected value type %s", type_of)

def generate_unitialized_value(size):
    """ Generates special value that is unitialized but has a size """
    return BV.UnitializedValue(size)


def generate_default_value(size):
    """Generates a default value of the given size (used for uninitialized
    variables)."""
    value = Factory.Integer(0, 'bit_value', size)
    return value


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

def cast(value, typedeclt, state=None):  # pylint: disable=unused-argument
    """Casts the given value a  a value of the given type."""
    result = None
    #Int -> Int
    #Int -> Pointer
    #Int -> Float

    #Float -> Int
    #Float -> Float

    #Pointer -> Int
    #Pointer -> Pointer

    #BV.ByteValue -> ALL
    if isinstance(value, BV.SizedSet):
        result = BV.SizedSet(value.size)
        for item in value:
            result.add(cast(item, typedeclt, state))
    elif isinstance(typedeclt, pycparser.c_ast.Typename):
        result = cast(value, typedeclt.type, state)
    elif isinstance(typedeclt, pycparser.c_ast.PtrDecl):
        if isinstance(value, BV.ReferenceValue):
            result = copy_pointer(value, typedeclt.type) #P -> P
        elif isinstance(value, BV.BaseInteger): #I -> P
            # normal number being turned into a pointer not valid to dereference
            # TODO manage tracking of this
            logging.debug(" Cast %s to %s", str(value), str(typedeclt))
            address = state.stor.get_nearest_address(value.data)
            result = copy_pointer(address, typedeclt.type)
    elif isinstance(typedeclt, pycparser.c_ast.TypeDecl):
        types = typedeclt.type.names
        logging.debug("Casting %s to type %s",str(value)," ".join(types))
        byte_value = value.get_byte_value()
        logging.debug("Byte_Value before cast %s", str(byte_value))
        result = generate_value(byte_value, " ".join(types))
        logging.debug("Cast result is %s",str(result.data))
    else:
        logging.error('\tUnsupported cast: ' + str(typedeclt.type))
        raise Exception("Unsupported cast")
    
    return result
