#ifndef FTW_H
#define FTW_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

int ftw(const char *,
                int (*)(const char *, const struct stat *, int), int);
int nftw(const char *, int (*)
                (const char *, const struct stat *, int, struct FTW*),
                int, int);
#endif
