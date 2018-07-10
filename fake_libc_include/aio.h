#ifndef AIO_H_
#define AIO_H_
#include "_fake_defines.h"
#include "_fake_typedefs.h"

int aio_cancel(int, struct aiocb *);
int aio_error(const struct aiocb *);
int aio_fsync(int, struct aiocb *);
int aio_read(struct aiocb *);
ssize_t aio_return(struct aiocb *);
int aio_suspend(const struct aiocb *const[], int const struct timespec *);
int aio_write(struct aiocb *);
int lio_listio(int, struct aiocb *restrict const[restrict], int struct sigevent *restrict);
#endif
