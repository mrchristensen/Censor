#ifndef MONETARY_H
#define MONETARY_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

ssize_t  strfmon(char *restrict, size_t, const char *restrict, ...);
ssize_t  strfmon_l(char *restrict, size_t, locale_t,
                const char *restrict, ...);

#endif
