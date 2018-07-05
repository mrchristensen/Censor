#ifndef ARGZ_H
#define ARGZ_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

error_t argz_add(char **argz, size_t *argz_len, const char *str);

error_t argz_add_sep(char **argz, size_t *argz_len,
                             const char *str, int delim);

error_t argz_append(char **argz, size_t *argz_len,
                             const char *buf, size_t buf_len);

size_t argz_count(const char *argz, size_t argz_len);

error_t argz_create(char * const argv[], char **argz,
                             size_t *argz_len);

error_t argz_create_sep(const char *str, int sep, char **argz,
                             size_t *argz_len);

error_t argz_delete(char **argz, size_t *argz_len, char *entry);

void argz_extract(char *argz, size_t argz_len, char  **argv);

error_t argz_insert(char **argz, size_t *argz_len, char *before,
                             const char *entry);

char *argz_next(char *argz, size_t argz_len, const char *entry);

error_t argz_replace(char **argz, size_t *argz_len, const char *str,
                             const char *with, unsigned int *replace_count);

void argz_stringify(char *argz, size_t len, int sep);

#endif
