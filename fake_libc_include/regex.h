#ifndef REGEX_H
#define REGEX_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

int regcomp(regex_t *preg, const char *regex, int cflags);

int regexec(const regex_t *preg, const char *string, size_t nmatch,
                regmatch_t pmatch[], int eflags);

size_t regerror(int errcode, const regex_t *preg, char *errbuf,
                size_t errbuf_size);

void regfree(regex_t *preg);

#endif
