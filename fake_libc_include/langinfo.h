#ifndef LANGINFO_H
#define LANGINFO_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

char *nl_langinfo(nl_item);
char *nl_langinfo_l(nl_item, locale_t);

#endif
