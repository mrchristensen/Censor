#ifndef SIGNAL_H
#define SIGNAL_H

#include "_fake_defines.h"
#include "_fake_typedefs.h"

struct sigaction {
    void (*sa_handler)(int);
    void (*sa_sigaction)(int, siginfo_t *, void *);
    sigset_t sa_mask;
    int sa_flags;
    void (*sa_restorer)(void);
};

int    sigaction(int, const struct sigaction *restrict,
           struct sigaction *restrict);

#endif
