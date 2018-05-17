"""Concrete values for macros that would be accesed through <limits.h> in C.
From the C99 standard: "Their implementation-defined values shall be equal or
greater in magnitude (absolute value) to those shown, with the same sign."""
from collections import namedtuple

SCHAR_MIN = -128
SCHAR_MAX = 127
UCHAR_MAX = 255
CHAR_MIN = 0 # can also be UCHAR_MIN, depending on implementation
CHAR_MAX = SCHAR_MAX # can also be UCHAR_MAX, depending on implementation
MB_LEN_MAX = 1
SHRT_MIN = -32768
SHRT_MAX = 32767
USHRT_MAX = 65535
INT_MIN = -32768
INT_MAX = 32767
UINT_MAX = 65535
LONG_MIN = -2147483648
LONG_MAX = 2147483647
ULONG_MAX = (2 ** 32) - 1
LLONG_MIN = -(2 ** 63)
LLONG_MAX = (2 ** 63) - 1
ULLONG_MAX = (2 ** 64) - 1


Range = namedtuple('Range', ['min', 'max'])

RANGES = {
    "char": Range(CHAR_MIN, CHAR_MAX),
    "unsigned char": Range(0, UCHAR_MAX),
    "signed char": Range(SCHAR_MIN, SCHAR_MAX),
    "short": Range(SHRT_MIN, SHRT_MAX),
    "unsigned short": Range(0, USHRT_MAX),
    "int": Range(INT_MIN, INT_MAX),
    "unsigned int": Range(0, UINT_MAX),
    "long": Range(LONG_MIN, LONG_MAX),
    "long int": Range(LONG_MIN, LONG_MAX),
    "unsigned long int": Range(0, ULONG_MAX),
    "long long int": Range(LLONG_MIN, LLONG_MAX),
    "unsigned long long int": Range(0, ULLONG_MAX)
}
