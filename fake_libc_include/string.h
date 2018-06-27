#include "_fake_defines.h"
#include "_fake_typedefs.h"
#ifndef STRING_H
#define STRING_H

extern int strcmp (const char *__s1, const char *__s2);
extern void *memset (void *__s, int __c, size_t __n);

//typedef unsigned int size_t;
//#define NULL 0

size_t strlen(const char *str);

#endif
