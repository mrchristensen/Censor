#ifndef STRINGS_H
#define STRINGS_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

int    bcmp(const void *, const void *, size_t);
void   bcopy(const void *, void *, size_t);
void   bzero(void *, size_t);
int    ffs(int);
char   *index(const char *, int);
char   *rindex(const char *, int);
int    strcasecmp(const char *, const char *);
int    strncasecmp(const char *, const char *, size_t);

#endif
