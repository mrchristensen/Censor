#ifndef SEARCH_H
#define SEARCH_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

int    hcreate(size_t);
void   hdestroy(void);
ENTRY *hsearch(ENTRY, ACTION);
void   insque(void *, void *);
void  *lfind(const void *, const void *, size_t *,
                size_t, int (*)(const void *, const void *));
void  *lsearch(const void *, void *, size_t *,
                size_t, int (*)(const void *, const void *));
void   remque(void *);
void  *tdelete(const void *restrict, void **restrict,
                int(*)(const void *, const void *));
void  *tfind(const void *, void *const *,
                int(*)(const void *, const void *));
void  *tsearch(const void *, void **,
                int(*)(const void *, const void *));
void   twalk(const void *,
                void (*)(const void *, VISIT, int ));

#endif
