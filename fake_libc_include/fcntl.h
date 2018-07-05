#ifndef FCNTL_H
#define FCNTL_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

int  creat(const char *, mode_t);
int  fcntl(int, int, ...);
int  open(const char *, int, ...);

#endif
