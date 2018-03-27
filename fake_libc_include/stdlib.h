#include "_fake_defines.h"
#include "_fake_typedefs.h"

extern void *malloc (size_t __size);
extern void *calloc (size_t __nmemb, size_t __size);
extern void *realloc (void *__ptr, size_t __size);

extern void free (void *__ptr);
