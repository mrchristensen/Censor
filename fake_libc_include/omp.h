#ifndef OMP_H
#define OMP_H

#ifndef _LIBGOMP_OMP_LOCK_DEFINED
#define _LIBGOMP_OMP_LOCK_DEFINED 1
/* These two structures get edited by the libgomp build process to 
   reflect the shape of the two types.  Their internals are private
   to the library.  */
#define OMP_LOCK_SIZE 64
#define OMP_NEST_LOCK_SIZE 64
typedef struct
{
  unsigned char _x[OMP_LOCK_SIZE]; 
} omp_lock_t;

typedef struct
{
  unsigned char _x[OMP_NEST_LOCK_SIZE]; 
} omp_nest_lock_t;
#endif

typedef enum omp_sched_t
{
    omp_sched_static = 1,
    omp_sched_dynamic = 2,
    omp_sched_guided = 3,
    omp_sched_auto = 4
} omp_sched_t;

typedef enum omp_proc_bind_t
{
    omp_proc_bind_false = 0,
    omp_proc_bind_true = 1,
    omp_proc_bind_master = 2,
    omp_proc_bind_close = 3,
    omp_proc_bind_spread = 4
} omp_proc_bind_t;

typedef enum omp_lock_hint_t
{
    omp_lock_hint_none = 0,
    omp_lock_hint_uncontended = 1,
    omp_lock_hint_contended = 2,
    omp_lock_hint_nonspeculative = 4,
    omp_lock_hint_speculative = 8,
} omp_lock_hint_t;

     void omp_set_num_threads (int);
     int omp_get_num_threads (void);
     int omp_get_max_threads (void);
     int omp_get_thread_num (void);
     int omp_get_num_procs (void);

     int omp_in_parallel (void);

     void omp_set_dynamic (int);
     int omp_get_dynamic (void);

     void omp_set_nested (int);
     int omp_get_nested (void);

     void omp_init_lock (omp_lock_t *);
     void omp_init_lock_with_hint (omp_lock_t *, omp_lock_hint_t)
       ;
     void omp_destroy_lock (omp_lock_t *);
     void omp_set_lock (omp_lock_t *);
     void omp_unset_lock (omp_lock_t *);
     int omp_test_lock (omp_lock_t *);

     void omp_init_nest_lock (omp_nest_lock_t *);
     void omp_init_nest_lock_with_hint (omp_lock_t *, omp_lock_hint_t)
       ;
     void omp_destroy_nest_lock (omp_nest_lock_t *);
     void omp_set_nest_lock (omp_nest_lock_t *);
     void omp_unset_nest_lock (omp_nest_lock_t *);
     int omp_test_nest_lock (omp_nest_lock_t *);

     double omp_get_wtime (void);
     double omp_get_wtick (void);

     void omp_set_schedule (omp_sched_t, int);
     void omp_get_schedule (omp_sched_t *, int *);
     int omp_get_thread_limit (void);
     void omp_set_max_active_levels (int);
     int omp_get_max_active_levels (void);
     int omp_get_level (void);
     int omp_get_ancestor_thread_num (int);
     int omp_get_team_size (int);
     int omp_get_active_level (void);

     int omp_in_final (void);

     int omp_get_cancellation (void);
     omp_proc_bind_t omp_get_proc_bind (void);
     int omp_get_num_places (void);
     int omp_get_place_num_procs (int);
     void omp_get_place_proc_ids (int, int *);
     int omp_get_place_num (void);
     int omp_get_partition_num_places (void);
     void omp_get_partition_place_nums (int *);

     void omp_set_default_device (int);
     int omp_get_default_device (void);
     int omp_get_num_devices (void);
     int omp_get_num_teams (void);
     int omp_get_team_num (void);

     int omp_is_initial_device (void);
     int omp_get_initial_device (void);
     int omp_get_max_task_priority (void);

     void *omp_target_alloc (__SIZE_TYPE__, int);
     void omp_target_free (void *, int);
     int omp_target_is_present (void *, int);
     int omp_target_memcpy (void *, void *, __SIZE_TYPE__, __SIZE_TYPE__,
            __SIZE_TYPE__, int, int);
     int omp_target_memcpy_rect (void *, void *, __SIZE_TYPE__, int,
            const __SIZE_TYPE__ *,
            const __SIZE_TYPE__ *,
            const __SIZE_TYPE__ *,
            const __SIZE_TYPE__ *,
            const __SIZE_TYPE__ *, int, int)
       ;
     int omp_target_associate_ptr (void *, void *, __SIZE_TYPE__,
            __SIZE_TYPE__, int);
     int omp_target_disassociate_ptr (void *, int);

#endif
