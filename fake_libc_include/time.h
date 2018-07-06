#ifndef TIME_H
#define TIME_H

#include "_fake_defines.h"
#include "_fake_typedefs.h"

struct tm
{
    int tm_sec;                   /* Seconds.     [0-60] (1 leap second) */
    int tm_min;                   /* Minutes.     [0-59] */
    int tm_hour;                  /* Hours.       [0-23] */
    int tm_mday;                  /* Day.         [1-31] */
    int tm_mon;                   /* Month.       [0-11] */
    int tm_year;                  /* Year - 1900.  */
    int tm_wday;                  /* Day of week. [0-6] */
    int tm_yday;                  /* Days in year.[0-365] */
    int tm_isdst;                 /* DST.         [-1/0/1]*/

    int tm_mon_length;
    int tm_year_length;
};

/* Return the current time and put it in *TIMER if TIMER is not NULL.  */
time_t time(time_t *__timer);

/* Return the `struct tm' representation of *TIMER in local time,
   using *TP to store the result.  */
struct tm *localtime_r(const time_t * __timer,
        struct tm * __tp);

void udelay (unsigned long usec);


#endif
