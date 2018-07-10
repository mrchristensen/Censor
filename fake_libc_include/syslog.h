#ifndef SYSLOG_H
#define SYSLOG_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

void openlog(const char *ident, int option, int facility);
void syslog(int priority, const char *format, ...);
void closelog(void);

void vsyslog(int priority, const char *format, va_list ap);

#endif
