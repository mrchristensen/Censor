#ifndef STRING_H
#define STRING_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

void *memchr(const void *str, int c, size_t n);
int memcmp(const void* str1, const void *str2, size_t n);
void *memcpy(void* dest, const void* src, size_t n);
void *memmove(void* dest, const void* src, size_t n);
void *memset(void *str, int c, size_t n);
int strcasecmp(const char *s1, const char *s2);
int strncasecmp(const char *s1, const char *s2, size_t n);
char *index(const char *s, int c);
char *rindex(const char *s, int c);
char *stpcpy(char *dest, const char *src);
char *strcat(char *dest, const char *src);
char *strchr(const char *s, int c);
int strcmp(const char *s1, const char *s2);
int strcoll(const char *s1, const char *s2);
char *strcpy(char *dest, const char *src);
size_t strcspn(const char *s, const char *reject);
char *strdup(const char *s);
char *strfry(char *string);
size_t strlen(const char *s);
char *strncat(char *dest, const char *src, size_t n);
int strncmp(const char *s1, const char *s2, size_t n);
char *strncpy(char *dest, const char *src, size_t n);
char *strpbrk(const char *s, const char *accept);
char *strrchr(const char *s, int c);
char *strsep(char **stringp, const char *delim);
size_t strspn(const char *s, const char *accept);
char *strstr(const char *haystack, const char *needle);
char *strtok(char *s, const char *delim);
size_t strxfrm(char *dest, const char *src, size_t n);

#endif
