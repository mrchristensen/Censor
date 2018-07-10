#ifndef DLFCN_H
#define DLFCN_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

int    dlclose(void *);
char  *dlerror(void);
void  *dlopen(const char *, int);
void  *dlsym(void *restrict, const char *restrict);

#endif
