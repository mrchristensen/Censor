#ifndef SPAWN_H
#define SPAWN_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

int   posix_spawn(pid_t *restrict, const char *restrict,
                const posix_spawn_file_actions_t *,
                const posix_spawnattr_t *restrict, char *const [restrict],
                char *const [restrict]);
int   posix_spawn_file_actions_addclose(posix_spawn_file_actions_t *,
                int);
int   posix_spawn_file_actions_adddup2(posix_spawn_file_actions_t *,
                int, int);
int   posix_spawn_file_actions_addopen(posix_spawn_file_actions_t *restrict,
                int, const char *restrict, int, mode_t);
int   posix_spawn_file_actions_destroy(posix_spawn_file_actions_t *);
int   posix_spawn_file_actions_init(posix_spawn_file_actions_t *);
int   posix_spawnattr_destroy(posix_spawnattr_t *);
int   posix_spawnattr_getflags(const posix_spawnattr_t *restrict,
                short *restrict);
int   posix_spawnattr_getpgroup(const posix_spawnattr_t *restrict,
                pid_t *restrict);
int   posix_spawnattr_getschedparam(const posix_spawnattr_t *restrict,
                struct sched_param *restrict);
int   posix_spawnattr_getschedpolicy(const posix_spawnattr_t *restrict,
                int *restrict);
int   posix_spawnattr_getsigdefault(const posix_spawnattr_t *restrict,
                sigset_t *restrict);
int   posix_spawnattr_getsigmask(const posix_spawnattr_t *restrict,
                sigset_t *restrict);
int   posix_spawnattr_init(posix_spawnattr_t *);
int   posix_spawnattr_setflags(posix_spawnattr_t *, short);
int   posix_spawnattr_setpgroup(posix_spawnattr_t *, pid_t);
int   posix_spawnattr_setschedparam(posix_spawnattr_t *restrict,
                const struct sched_param *restrict);
int   posix_spawnattr_setschedpolicy(posix_spawnattr_t *, int);
int   posix_spawnattr_setsigdefault(posix_spawnattr_t *restrict,
                const sigset_t *restrict);
int   posix_spawnattr_setsigmask(posix_spawnattr_t *restrict,
                const sigset_t *restrict);
int   posix_spawnp(pid_t *restrict, const char *restrict,
                const posix_spawn_file_actions_t *,
                const posix_spawnattr_t *restrict,
                char *const [restrict], char *const [restrict]);

#endif
