#ifndef PWD_H
#define PWD_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

struct passwd *getpwnam(const char *);
struct passwd *getpwuid(uid_t);
int            getpwnam_r(const char *, struct passwd *, char *,
                                   size_t, struct passwd **);
int            getpwuid_r(uid_t, struct passwd *, char *,
                                   size_t, struct passwd **);
void           endpwent(void);
struct passwd *getpwent(void);
void           setpwent(void);

#endif
