#ifndef GLOB_H
#define GLOB_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

int glob(const char *pattern, int flags,
                int (*errfunc) (const char *epath, int eerrno),
                glob_t *pglob);
void globfree(glob_t *pglob);

#endif
