#ifndef DIRENT_H
#define DIRENT_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

int            closedir(DIR *);
DIR           *opendir(const char *);
struct dirent *readdir(DIR *);
int            readdir_r(DIR *, struct dirent *, struct dirent **);
void           rewinddir(DIR *);
void           seekdir(DIR *, long int);
long int       telldir(DIR *);

#endif
