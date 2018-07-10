#ifndef UTIME_H
#define UTIME_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

int utime(const char *filename, const struct utimbuf *times);

#endif
