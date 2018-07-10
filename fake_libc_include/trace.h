#ifndef TRACE_H
#define TRACE_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"

struct {
        trace_event_id_t posix_event_id;
        pid_t posix_pid;
        void *posix_prog_address;
        pthread_t posix_thread_id;
        struct timespec posix_timestamp;
        int posix_truncation_status;
} posix_trace_event_info;

struct {
        int posix_stream_full_status;
        int posix_stream_overrun_status;
        int posix_stream_status;
        int posix_log_full_status;
        int posix_log_overrun_status;
        int posix_stream_flush_error;
        int posix_stream_flush_status;
} posix_trace_status_info;

int  posix_trace_attr_destroy(trace_attr_t *);
int  posix_trace_attr_getclockres(const trace_attr_t *,
                struct timespec *);
int  posix_trace_attr_getcreatetime(const trace_attr_t *,
                struct timespec *);
int  posix_trace_attr_getgenversion(const trace_attr_t *, char *);
int  posix_trace_attr_getinherited(const trace_attr_t *restrict,
                int *restrict);
int  posix_trace_attr_getlogfullpolicy(const trace_attr_t *restrict,
                int *restrict);
int  posix_trace_attr_getlogsize(const trace_attr_t *restrict,
                size_t *restrict);
int  posix_trace_attr_getmaxdatasize(const trace_attr_t *restrict,
                size_t *restrict);
int  posix_trace_attr_getmaxsystemeventsize(const trace_attr_t *restrict,
                size_t *restrict);
int  posix_trace_attr_getmaxusereventsize(const trace_attr_t *restrict,
                size_t, size_t *restrict);
int  posix_trace_attr_getname(const trace_attr_t *, char *);
int  posix_trace_attr_getstreamfullpolicy(const trace_attr_t *restrict,
                int *restrict);
int  posix_trace_attr_getstreamsize(const trace_attr_t *restrict,
                size_t *restrict);
int  posix_trace_attr_init(trace_attr_t *);
int  posix_trace_attr_setinherited(trace_attr_t *, int);
int  posix_trace_attr_setlogfullpolicy(trace_attr_t *, int);
int  posix_trace_attr_setlogsize(trace_attr_t *, size_t);
int  posix_trace_attr_setmaxdatasize(trace_attr_t *, size_t);
int  posix_trace_attr_setname(trace_attr_t *, const char *);
int  posix_trace_attr_setstreamfullpolicy(trace_attr_t *, int);
int  posix_trace_attr_setstreamsize(trace_attr_t *, size_t);
int  posix_trace_clear(trace_id_t);
int  posix_trace_close(trace_id_t);
int  posix_trace_create(pid_t, const trace_attr_t *restrict,
                trace_id_t *restrict);
int  posix_trace_create_withlog(pid_t, const trace_attr_t *restrict,
                int, trace_id_t *restrict);
void posix_trace_event(trace_event_id_t, const void *restrict, size_t);
int  posix_trace_eventid_equal(trace_id_t, trace_event_id_t,
                trace_event_id_t);
int  posix_trace_eventid_get_name(trace_id_t, trace_event_id_t, char *);
int  posix_trace_eventid_open(const char *restrict,
                trace_event_id_t *restrict);
int  posix_trace_eventset_add(trace_event_id_t, trace_event_set_t *);
int  posix_trace_eventset_del(trace_event_id_t, trace_event_set_t *);
int  posix_trace_eventset_empty(trace_event_set_t *);
int  posix_trace_eventset_fill(trace_event_set_t *, int);
int  posix_trace_eventset_ismember(trace_event_id_t,
                const trace_event_set_t *restrict, int *restrict);
int  posix_trace_eventtypelist_getnext_id(trace_id_t,
                trace_event_id_t *restrict, int *restrict);
int  posix_trace_eventtypelist_rewind(trace_id_t);
int  posix_trace_flush(trace_id_t);
int  posix_trace_get_attr(trace_id_t, trace_attr_t *);
int  posix_trace_get_filter(trace_id_t, trace_event_set_t *);
int  posix_trace_get_status(trace_id_t,
                struct posix_trace_status_info *);
int  posix_trace_getnext_event(trace_id_t,
                struct posix_trace_event_info *restrict, void *restrict,
                size_t, size_t *restrict, int *restrict);
int  posix_trace_open(int, trace_id_t *);
int  posix_trace_rewind(trace_id_t);
int  posix_trace_set_filter(trace_id_t, const trace_event_set_t *, int);
int  posix_trace_shutdown(trace_id_t);
int  posix_trace_start(trace_id_t);
int  posix_trace_stop(trace_id_t);
int  posix_trace_timedgetnext_event(trace_id_t,
                struct posix_trace_event_info *restrict, void *restrict,
                size_t, size_t *restrict, int *restrict,
                const struct timespec *restrict);
int  posix_trace_trid_eventid_open(trace_id_t, const char *restrict,
                trace_event_id_t *restrict);
int  posix_trace_trygetnext_event(trace_id_t,
                struct posix_trace_event_info *restrict, void *restrict, size_t,
                size_t *restrict, int *restrict);

#endif
