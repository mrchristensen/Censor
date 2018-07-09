#ifndef STDARG_H
#define STDARG_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

void va_start(va_list ap, argN);
void va_copy(va_list dest, va_list src);
type va_arg(va_list ap, type);
void va_end(va_list ap);

#endif
