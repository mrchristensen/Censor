"""Classes to represent values, and a function for generating
a value based on an assignment node"""
import pycparser
import logging
from cesk.linksearch import get_sizes
import cesk.config
from cesk.values.base_values import ReferenceValue, UnitializedValue
import cesk.limits as limits
if cesk.config.CONFIG['values'] == 'concrete':
    from cesk.values.concrete import Integer, Float, Char, Pointer
elif cesk.config.CONFIG['values'] == 'abstract':
    # from cesk.values.abstract import Integer, Float, Char, Pointer
    from cesk.values.abstract import IntAsFloat as Float
    from cesk.values.abstract import Integer, Char, Pointer
else:
    raise Exception("Unknown value type = " + cesk.config.CONFIG['values'])
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
            return Float(value[:-1], 'float')
        elif value[-1] in "lL":
            return Float(value, 'long double')
        else:
            return Float(value, 'double')
    elif type_of == 'int':
        u = ''
        if value[-1] in "uU":
            u = 'unsigned '
            value = value[:-1]
        if value[-1] not in "lL":
            val = int(value, 0)
            if val <= limits.RANGES['unsigned '+type_of].max:
                return Integer(val, u+type_of)
        else:
            value = value[:-1]
        type_of = 'long '+type_of
        val = int(value, 0)

        if val <= limits.RANGES['unsigned '+type_of].max:
            return Integer(val, u+type_of)
        type_of = 'long '+type_of
        if val <= limits.RANGES['unsigned '+type_of].max:
            return Integer(val, u+type_of)

    elif type_of == 'char':
        return Char(value, type_of)

    raise Exception("Unkown Constant Type %s", type_of)


def generate_value(value, type_of='bit_value', size=None):
    """ given value in bits and type_of as string, size for special cases 
        special cases include pointer, bit_value, uninitialized """
    if "char" in type_of:
        return Char(value, type_of)
    if type_of in limits.RANGES:
        return Integer(value, type_of)
    if "float" in type_of or "double" in type_of:
        return Float(value, type_of)
    if type_of == 'bit_value':
        return Integer(value, type_of, size)

    if type_of == 'pointer':
        raise Exception(
            'Pointer not expected here/not valid to change dynamically')

    if type_of == 'uninitialized':
        return Integer(value, 'bit_value', size)

    raise Exception("Unexpected value type %s", type_of)

def generate_unitialized_value(size):
    """ Generates special value that is unitialized but has a size """
    return UnitializedValue(size)


def generate_default_value(size):
    """Generates a default value of the given size (used for uninitialized
    variables)."""
    value = Integer(0, 'bit_value', size)
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
        get_sizes(ptr_type, sizes)  # returns alignment
        size = sum(sizes)
    return Pointer(pointer.data, size, pointer.offset)

def generate_null_pointer():
    """ Build a pointer that will not dereference """
    return Pointer(0, 1)

def generate_frame_address(frame, ident):
    """ Build a Frame Address """
    return FrameAddress(frame, ident)


def cast(value, typedeclt, state=None):  # pylint: disable=unused-argument
    """Casts the given value a  a value of the given type."""
    result = None

    if isinstance(typedeclt, pycparser.c_ast.Typename):
        result = cast(value, typedeclt.type, state)
    elif isinstance(typedeclt, pycparser.c_ast.PtrDecl):
        if isinstance(value, ReferenceValue):
            result = copy_pointer(value, typedeclt.type)
        else:
            # normal number being turned into a pointer not valid to dereference
            # TODO manage tracking of this
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
