#ifndef SIGNAL_H
#define SIGNAL_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

typedef union
{
        int sival_int;
        void *sival_ptr;
} sigval;

typedef struct {
        int sigev_notify;
        int sigev_signo;
        union sigval sigev_value;
        void (*sigev_notify_function)(union sigval);
        pthread_attr_t *sigev_notify_attributes;
} sigevent;

struct sigaction{
        void (*sa_handler)(int);
        sigset_t sa_mask;
        int sa_flags;
        void (*sa_sigaction)(int, siginfo_t *, void *);
} sigaction;

typedef struct {
        void *ss_sp;
        size_t ss_size;
        int ss_flags;
} stack_t;

typedef struct {
        int si_signo;
        int si_code;
        int si_errno;
        pid_t si_pid;
        uid_t si_uid;
        void *si_addr;
        int si_status;
        long si_band;
        union sigval si_value;
} siginfo_t;

int    kill(pid_t, int);
int    killpg(pid_t, int);
void   psiginfo(const siginfo_t *, const char *);
void   psignal(int, const char *);
int    pthread_kill(pthread_t, int);
int    pthread_sigmask(int, const sigset_t *restrict,
                sigset_t *restrict);
int    raise(int);
int    sigaction(int, const struct sigaction *restrict,
                struct sigaction *restrict);
int    sigaddset(sigset_t *, int);
int    sigaltstack(const stack_t *restrict, stack_t *restrict);
int    sigdelset(sigset_t *, int);
int    sigemptyset(sigset_t *);
int    sigfillset(sigset_t *);
int    sighold(int);
int    sigignore(int);
int    siginterrupt(int, int);
int    sigismember(const sigset_t *, int);
void (*signal(int, void (*)(int)))(int);
int    sigpause(int);
int    sigpending(sigset_t *);
int    sigprocmask(int, const sigset_t *restrict, sigset_t *restrict);
int    sigqueue(pid_t, int, const union sigval);
int    sigrelse(int);
void (*sigset(int, void (*)(int)))(int);
int    sigsuspend(const sigset_t *);
int    sigtimedwait(const sigset_t *restrict, siginfo_t *restrict,
                const struct timespec *restrict);
int    sigwait(const sigset_t *restrict, int *restrict);
int    sigwaitinfo(const sigset_t *restrict, siginfo_t *restrict);
#endif
