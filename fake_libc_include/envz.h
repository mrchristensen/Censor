#ifndef ENVZ_H
#define ENVZ_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

error_t envz_add(char **envz, size_t *envz_len,
                const char *name, const char *value);

char *envz_entry(const char *envz, size_t *envz_len, const char *name);

char *envz_get(const char *envz, size_t *envz_len, const char *name);

error_t envz_merge(char **envz, size_t *envz_len,
                const char *envz2, size_t envz2_len, int override);

void envz_remove(char **envz, size_t *envz_len, const char *name);

void envz_strip(char **envz, size_t *envz_len);

#endif
