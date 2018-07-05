#ifndef GRP_H
#define GRP_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

struct group  *getgrgid(gid_t);
struct group  *getgrnam(const char *);
int            getgrgid_r(gid_t, struct group *, char *,
                size_t, struct group **);
int            getgrnam_r(const char *, struct group *, char *,
                size_t , struct group **);
struct group  *getgrent(void);
void           endgrent(void);
void           setgrent(void);

#endif
