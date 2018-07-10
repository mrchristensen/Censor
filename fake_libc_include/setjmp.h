#ifndef SETJMP_H
#define SETJMP_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

void   _longjmp(jmp_buf, int);
void   longjmp(jmp_buf, int);
void   siglongjmp(sigjmp_buf, int);
int    _setjmp(jmp_buf);
int    setjmp(jmp_buf);
int    sigsetjmp(sigjmp_buf, int);

#endif
