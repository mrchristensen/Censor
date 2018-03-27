#include "_fake_defines.h"
#include "_fake_typedefs.h"

extern int fprintf (FILE * __stream, const char * __format, ...);
extern int printf (const char * __format, ...);
extern int sprintf (char * __s, const char * __format, ...);

extern int fgetc (FILE *__stream);
extern int getc (FILE *__stream);
extern int getchar (void);
extern int fputc (int __c, FILE *__stream);
extern int putc (int __c, FILE *__stream);
extern int putchar (int __c);