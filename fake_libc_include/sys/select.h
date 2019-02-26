#ifndef _SYS_SELECT_H
#define _SYS_SELECT_H

#include "_fake_defines.h"
#include "_fake_typedefs.h"

#include <sys/types.h>
#include <signal.h>
#include <time.h>

//The <sys/select.h> header shall define the timeval structure that includes at least the following members:
struct timeval{
time_t         tv_sec;//      Seconds. 
suseconds_t    tv_usec;//     Microseconds. 
};
//The time_t and suseconds_t types shall be defined as described in <sys/types.h>.
//The sigset_t type shall be defined as described in <signal.h>.
//The timespec structure shall be defined as described in <time.h>.
//The <sys/select.h> header shall define the fd_set type as a structure.
#define NBBY 8
#ifndef    FD_SETSIZE
#define    FD_SETSIZE    256
#endif

//typedef long    fd_mask;
#define NFDBITS    (sizeof(fd_mask) * NBBY)    /* bits per mask */

#ifndef howmany
#define    howmany(x, y)    (((x)+((y)-1))/(y))
#endif

typedef    struct fd_set {
    fd_mask    fds_bits[howmany(FD_SETSIZE, NFDBITS)];
} fd_set;
//Each of the following may be declared as a function, or defined as a macro, or both:
void FD_CLR(int fd, fd_set *fdset);
//Clears the bit for the file descriptor fd in the file descriptor set fdset.

int FD_ISSET(int fd, fd_set *fdset);
//Returns a non-zero value if the bit for the file descriptor fd is set in the file descriptor set by fdset, and 0 otherwise.

void FD_SET(int fd, fd_set *fdset);
//Sets the bit for the file descriptor fd in the file descriptor set fdset.

void FD_ZERO(fd_set *fdset);
//Initializes the file descriptor set fdset to have zero bits for all file descriptors.
//If implemented as macros, these may evaluate their arguments more than once, so applications should ensure that the arguments they supply are never expressions with side effects.

//The following shall be defined as a macro:

//Maximum number of file descriptors in an fd_set structure.
//The following shall be declared as functions and may also be defined as macros. Function prototypes shall be provided.

int  pselect(int, fd_set *restrict, fd_set *restrict, fd_set *restrict,
         const struct timespec *restrict, const sigset_t *restrict);
int  select(int, fd_set *restrict, fd_set *restrict, fd_set *restrict,
         struct timeval *restrict);

#endif
