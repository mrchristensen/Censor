//#ifndef STDIO_H
//#define STDIO_H

#include "_fake_defines.h"
#include "_fake_typedefs.h"

int fprintf (FILE * __stream, const char * __format, ...);
int printf (const char * __format, ...);
int sprintf (char * __s, const char * __format, ...);

//#endif
