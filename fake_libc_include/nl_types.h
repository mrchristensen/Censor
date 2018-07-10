#ifndef NL_TYPES_H
#define NL_TYPES_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

int       catclose(nl_catd);
char     *catgets(nl_catd, int, int, const char *);
nl_catd   catopen(const char *, int);

#endif
