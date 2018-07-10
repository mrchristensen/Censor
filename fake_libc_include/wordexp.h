#ifndef WORDEXP_H
#define WORDEXP_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

int wordexp(const char *s, wordexp_t *p, int flags);

void wordfree(wordexp_t *p);

#endif
