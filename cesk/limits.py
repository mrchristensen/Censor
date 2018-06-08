from enum import Enum
from collections import namedtuple

#This file acts as a configuration to match complier needs/wants 

class Number_Representation(Enum):
    ONES_COMPLEMENT = 1
    TWOS_COMPLEMENT = 2

class Struct_Packing_Scheme(Enum):
    PACT_COMPACT = 1
    GCC_STD = 2

#actual min size of floats and doubles are unspecified, but this matches the min requirements with IEEE standard for floating point representation
STD_MIN_BYTE_WIDTHS = { 'char':1, 'short':2, 'int':2, 'long':4, 'long long':8, 'float':4, 'double':8, 'long double':8, 'void':1, 'word':4 }
GCC_SPICEY_BYTE_WIDTHS = { 'char':1, 'short':2, 'int':4, 'long':8, 'long long':8, 'float':4, 'double':8, 'long double':16, 'void':1, 'word':8 } 

#defualt char could be either signed or unsigned
std_char_sign = True #not set but this is most common
gcc_char_sign = True

class Config_Types(Enum):
    GCC = 'gcc' 
    STD = 'std'
    CESK = 'cesk'

class Config:
    def __init__(self, config_type):
        if config_type == Config_Types.GCC:
            self.num_rep = Number_Representation.TWOS_COMPLEMENT
            self.size_dict = GCC_SPICEY_BYTE_WIDTHS
            self.char_sign = gcc_char_sign
            self.packing_scheme = Struct_Packing_Scheme.GCC_STD
        elif config_type == Config_Types.STD:
            self.num_rep = Number_Representation.ONES_COMPLEMENT
            self.size_dict = STD_MIN_BYTE_WIDTHS
            self.char_sign = std_char_sign
            self.packing_scheme = Struct_Packing_Scheme.GCC_STD
        elif config_type == CONFIG_Types.CESK:
            self.num_rep = Number_Representation.TWOS_COMPLEMENT
            self.size_dict = GCC_SPICEY_BYTE_WIDTHS
            self.char_sign = std_char_sign
            self.packing_scheme = Struct_Packing_Scheme.PACT_COMPACT

#---------------------------------------------------------------------
# Change this line to change configuration
config = Config(Config_Types.STD)
#---------------------------------------------------------------------

def get_size_identifier(identifiers):
    typ = None
    for identifier in identifiers:
        if identifier in ['long', 'float', 'double', 'char', 'short', 'void']:       
            if typ is not None:
                typ += ' '+identifier
            else:
                typ = identifier
        elif (typ is None) and (identifier == 'int'):
            typ = identifier
    return typ

#takes a list of strings and returns type size if availble
#will only work for valid c types that are listed below
def get_size(identifiers):
    typ = get_size_identifier(identifiers)
    return config.size_dict[typ]

#takes in a list of integer sizes and returns the size and needed alignment of the struct, nested structs should be converted to a list of sizes and added to the list rather than passing in a large number 
def get_struct_size_and_alignment(list_of_sizes):
   pass 

#this will be the size of any pointer
def get_word_size():
    return config.size_dict['word']

#calculate range
Range = namedtuple('Range', ['min','max'])
#only for integer values
def get_min_max(byte_width,number_rep,signed=True):
    if number_rep == Number_Representation.ONES_COMPLEMENT:
        if signed:
            min_val = - (2**(byte_width-1) - 1)
            max_val = 2**(byte_width-1) - 1
        else:
            min_val = 0
            max_val = 2**byte_width - 1
    elif number_rep == Number_Representation.TWOS_COMPLEMENT:
        if signed:
            min_val = - (2**(byte_width-1))
            max_val = 2**(byte_width-1) - 1
        else:
            min_val = 0
            max_val = 2**byte_width - 1
    return Range(min_val, max_val)

RANGES = {
    "char": get_min_max(config.size_dict['char'],config.num_rep,config.char_sign),
    "unsigned char": get_min_max(config.size_dict['char'],config.num_rep,False),
    "signed char": get_min_max(config.size_dict['char'],config.num_rep,True),
    "short": get_min_max(config.size_dict['short'],config.num_rep),
    "unsigned short": get_min_max(config.size_dict['short'],config.num_rep,False),
    "int": get_min_max(config.size_dict['int'],config.num_rep),
    "unsigned int": get_min_max(config.size_dict['int'],config.num_rep,False),
    "long": get_min_max(config.size_dict['long'],config.num_rep),
    "long int": get_min_max(config.size_dict['long'],config.num_rep),
    "unsigned long int": get_min_max(config.size_dict['long'],config.num_rep,False),
    "long long int": get_min_max(config.size_dict['long long'],config.num_rep),
    "unsigned long long int": get_min_max(config.size_dict['long long'],config.num_rep,False)
}
"""Concrete values for macros that would be accesed through <limits.h> in C.
From the C99 standard: "Their implementation-defined values shall be equal or
greater in magnitude (absolute value) to those shown, with the same sign."""

CHAR_BIT = config.size_dict['char']*8
SCHAR_MIN, SCHAR_MAX = get_min_max(config.size_dict['char'],config.num_rep)
UCHAR_MIN, UCHAR_MAX = get_min_max(config.size_dict['char'],config.num_rep,False)
CHAR_MIN, CHAR_MAX = get_min_max(config.size_dict['char'],config.num_rep,config.char_sign)
MB_LEN_MAX = config.size_dict['char']
SHRT_MIN, SHRT_MAX = get_min_max(config.size_dict['short'],config.num_rep)
USHRT_MIN, USHRT_MAX = get_min_max(config.size_dict['short'],config.num_rep,False)
INT_MIN, INT_MAX = get_min_max(config.size_dict['int'],config.num_rep)
UINT_MIN, UINT_MAX = get_min_max(config.size_dict['int'],config.num_rep,False)
LONG_MIN, LONG_MAX = get_min_max(config.size_dict['long'],config.num_rep)
ULONG_MIN, ULONG_MAX = get_min_max(config.size_dict['long'],config.num_rep,False)
LLONG_MIN, LLONG_MAX = get_min_max(config.size_dict['long long'],config.num_rep)
ULLONG_MIN, ULLONG_MAX = get_min_max(config.size_dict['long long'],config.num_rep,False) 

"""
Possible integer types (groups are equivalent)

char

signed char

unsigned char

short
short int
signed short
signed short int

unsigned short
unsigned short int

int
signed
signed int

unsigned
unsigned int

long
long int
signed long
signed long int

unsigned long
unsigned long int

long long
long long int
signed long long
signed long long int

unsigned long long
unsigned long long int

float

double

long double

"""

