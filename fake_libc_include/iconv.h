#ifndef ICONV_H
#define ICONV_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

iconv_t iconv_open(const char *, const char *);
size_t  iconv(iconv_t, char **restrict, size_t *restrict,
                char **restrict, size_t *restrict);
int     iconv_close(iconv_t);

#endif
