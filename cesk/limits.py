""" Stores and generates necessary run time environment information
Concrete values for macros that would be accesed through <limits.h> in C.
From the C99 standard: "Their implementation-defined values shall be equal or
greater in magnitude (absolute value) to those shown, with the same sign."""
from enum import Enum
from collections import namedtuple

#This file acts as a configuration to match complier needs/wants

class NumberRepresentation(Enum):
    """ enum to represent different number configurations"""
    ONES_COMPLEMENT = 1
    TWOS_COMPLEMENT = 2

class StructPackingScheme(Enum):
    """ Enum to represent diferent packing schemes """
    PACT_COMPACT = 1
    GCC_STD = 2

#actual min size of floats and doubles are unspecified, but this matches
# the min requirements with IEEE standard for floating point representation
STD_MIN_BYTE_WIDTHS = {'char':1, 'short':2, 'int':2, 'long':4,
                       'long long':8, 'float':4, 'double':8,
                       'long double':8, 'void':1, 'word':4}
GCC_SPICEY_BYTE_WIDTHS = {'char':1, 'short':2, 'int':4, 'long':8,
                          'long long':8, 'float':4, 'double':8,
                          'long double':16, 'void':1, 'word':8}

#defualt char could be either signed or unsigned
std_char_sign = True #pylint: disable=invalid-name
gcc_char_sign = True #pylint: disable=invalid-name

class ConfigTypes(Enum):
    """ Enum to save desired run time environments """
    GCC = 'gcc'
    STD = 'std'
    CESK = 'cesk'

#Constants in limits.h
#Declared here defined below
CHAR_BIT = 0, 0
SCHAR_MIN, SCHAR_MAX = 0, 0
UCHAR_MIN, UCHAR_MAX = 0, 0
CHAR_MIN, CHAR_MAX = 0, 0
MB_LEN_MAX = 0, 0
SHRT_MIN, SHRT_MAX = 0, 0
USHRT_MIN, USHRT_MAX = 0, 0
INT_MIN, INT_MAX = 0, 0
UINT_MIN, UINT_MAX = 0, 0
LONG_MIN, LONG_MAX = 0, 0
ULONG_MIN, ULONG_MAX = 0, 0
LLONG_MIN, LLONG_MAX = 0, 0
ULLONG_MIN, ULLONG_MAX = 0, 0
RANGES = {}

def get_size_identifier(identifiers):
    """ returns the combined string to look up in the size_dict """
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

#only for integer values
def get_min_max(byte_width, number_rep, signed=True):
    """ Returns min and max value given the parameters """
    byte_width *= 8
    if number_rep == NumberRepresentation.ONES_COMPLEMENT:
        if signed:
            min_val = - (2**(byte_width-1) - 1)
            max_val = 2**(byte_width-1) - 1
        else:
            min_val = 0
            max_val = 2**byte_width - 1
    elif number_rep == NumberRepresentation.TWOS_COMPLEMENT:
        if signed:
            min_val = - (2**(byte_width-1))
            max_val = 2**(byte_width-1) - 1
        else:
            min_val = 0
            max_val = 2**byte_width - 1
    return min_val, max_val

Range = namedtuple('Range', ['min', 'max'])
def set_ranges():
    """ Sets values for RANGES based on constants """
    #calculate range
    RANGES["char"] = Range(CHAR_MIN, CHAR_MAX)
    RANGES["unsigned char"] = Range(UCHAR_MIN, UCHAR_MAX)
    RANGES["signed char"] = Range(SCHAR_MIN, SCHAR_MAX)
    RANGES["short"] = Range(SHRT_MIN, SHRT_MAX)
    RANGES["unsigned short"] = Range(USHRT_MIN, USHRT_MAX)
    RANGES["int"] = Range(INT_MIN, INT_MAX)
    RANGES["unsigned int"] = Range(UINT_MIN, UINT_MAX)
    RANGES["long"] = Range(LONG_MIN, LONG_MAX)
    RANGES["unsigned long"] = Range(ULONG_MIN, ULONG_MAX)
    RANGES["long long"] = Range(LLONG_MIN, LLONG_MAX)
    RANGES["unsigned long long"] = Range(ULLONG_MIN, ULLONG_MAX)

class Config:
    """ Groups the necessary information to simulate
             different run time environments """
    def __init__(self, config_type):
        if config_type == ConfigTypes.GCC:
            self.num_rep = NumberRepresentation.TWOS_COMPLEMENT
            self.size_dict = GCC_SPICEY_BYTE_WIDTHS
            self.char_sign = gcc_char_sign
            self.packing_scheme = StructPackingScheme.GCC_STD
        elif config_type == ConfigTypes.STD:
            self.num_rep = NumberRepresentation.ONES_COMPLEMENT
            self.size_dict = STD_MIN_BYTE_WIDTHS
            self.char_sign = std_char_sign
            self.packing_scheme = StructPackingScheme.GCC_STD
        elif config_type == ConfigTypes.CESK:
            self.num_rep = NumberRepresentation.TWOS_COMPLEMENT
            self.size_dict = GCC_SPICEY_BYTE_WIDTHS
            self.char_sign = std_char_sign
            self.packing_scheme = StructPackingScheme.PACT_COMPACT

        self.set_constants()

    #takes a list of strings and returns type size if availble
    #will only work for valid c types that are listed below
    def get_size(self, identifiers):
        """ return the size based on a list of identifiers """
        typ = get_size_identifier(identifiers)
        return self.size_dict[typ]

    #this will be the size of any pointer
    def get_word_size(self):
        """ returns the word size for the set configuration """
        return self.size_dict['word']

    def set_constants(self):
        """ Declares contants to match choosen configuration
            Also sets RANGES to match as well """
        global CHAR_BIT, SCHAR_MIN, SCHAR_MAX, UCHAR_MIN, UCHAR_MAX #pylint: disable=global-statement
        global CHAR_MIN, CHAR_MAX, MB_LEN_MAX, SHRT_MIN, SHRT_MAX #pylint: disable=global-statement
        global USHRT_MIN, USHRT_MAX, INT_MIN, INT_MAX, UINT_MIN #pylint: disable=global-statement
        global UINT_MAX, LONG_MIN, LONG_MAX, ULONG_MIN, ULONG_MAX #pylint: disable=global-statement
        global LLONG_MIN, LLONG_MAX, ULLONG_MIN, ULLONG_MAX #pylint: disable=global-statement
        CHAR_BIT = self.size_dict['char']*8
        SCHAR_MIN, SCHAR_MAX = get_min_max(self.size_dict['char'],
                                           self.num_rep)
        UCHAR_MIN, UCHAR_MAX = get_min_max(self.size_dict['char'],
                                           self.num_rep, False)
        CHAR_MIN, CHAR_MAX = get_min_max(self.size_dict['char'],
                                         self.num_rep, self.char_sign)
        MB_LEN_MAX = self.size_dict['char']
        SHRT_MIN, SHRT_MAX = get_min_max(self.size_dict['short'],
                                         self.num_rep)
        USHRT_MIN, USHRT_MAX = get_min_max(self.size_dict['short'],
                                           self.num_rep, False)
        INT_MIN, INT_MAX = get_min_max(self.size_dict['int'],
                                       self.num_rep)
        UINT_MIN, UINT_MAX = get_min_max(self.size_dict['int'],
                                         self.num_rep, False)
        LONG_MIN, LONG_MAX = get_min_max(self.size_dict['long'],
                                         self.num_rep)
        ULONG_MIN, ULONG_MAX = get_min_max(self.size_dict['long'],
                                           self.num_rep, False)
        LLONG_MIN, LLONG_MAX = get_min_max(self.size_dict['long long'],
                                           self.num_rep)
        ULLONG_MIN, ULLONG_MAX = get_min_max(self.size_dict['long long'],
                                             self.num_rep, False)
        set_ranges()

#---------------------------------------------------------------------
# Change this line to change default configuration
CONFIG = Config(ConfigTypes.STD)
#---------------------------------------------------------------------
def set_config(config_string):
    """ Take a string and sets global CONFIG and types appropriately """
    global CONFIG #pylint: disable=global-statement
    config_string = config_string.lower()
    if config_string == 'gcc':
        CONFIG = Config(ConfigTypes.GCC)
    elif config_string == 'std':
        CONFIG = Config(ConfigTypes.STD)
    elif config_string == 'cesk':
        CONFIG = Config(ConfigTypes.CESK)
    else:
        raise Exception("Unknown configuration "+config_string)

#Possible integer types (groups are equivalent)
#Make sure all are available in ranges
#char

#signed char

#unsigned char

#short
#short int
#signed short
#signed short int
RANGES["short int"] = RANGES["short"]
RANGES["signed short"] = RANGES["short"]
RANGES["signed short int"] = RANGES["short"]

#unsigned short
#unsigned short int
RANGES["unsigned short int"] = RANGES["unsigned short"]

#int
#signed
#signed int
RANGES["signed"] = RANGES["int"]
RANGES["signed int"] = RANGES["int"]

#unsigned
#unsigned int
RANGES["unsigned"] = RANGES["unsigned int"]

#long
#long int
#signed long
#signed long int
RANGES["long int"] = RANGES["long"]
RANGES["signed long"] = RANGES["long"]
RANGES["signed long int"] = RANGES["long"]

#unsigned long
#unsigned long int
RANGES["unsigned long int"] = RANGES["unsigned long"]

#long long
#long long int
#signed long long
#signed long long int
RANGES["long long int"] = RANGES["long long"]
RANGES["signed long long"] = RANGES["long long"]
RANGES["signed long long int"] = RANGES["long long"]

#unsigned long long
#unsigned long long int
RANGES["unsigned long long int"] = RANGES["unsigned long long"]

#float

#double

#long double
