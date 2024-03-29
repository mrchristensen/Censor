/* Copyright (C) 2002-2017 Free Software Foundation, Inc.
      This file is part of the GNU C Library.
   
      The GNU C Library is free software; you can redistribute it and/or
      modify it under the terms of the GNU Lesser General Public
      License as published by the Free Software Foundation; either
      version 2.1 of the License, or (at your option) any later version.
   
      The GNU C Library is distributed in the hope that it will be useful,
       but WITHOUT ANY WARRANTY; without even the implied warranty of
       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
       Lesser General Public License for more details.
    
       You should have received a copy of the GNU Lesser General Public
       License along with the GNU C Library; if not, see
       <http://www.gnu.org/licenses/>.  */
    
    #ifndef        _SYS_EPOLL_H
    #define        _SYS_EPOLL_H        1
    
    #include <stdint.h>
    #include <sys/types.h>
    
    //#include <bits/types/sigset_t.h>
    
    /* Get the platform-dependent flags.  */
    //#include <bits/epoll.h>
    
    #ifndef __EPOLL_PACKED
    # define __EPOLL_PACKED
    #endif
    
    
    enum EPOLL_EVENTS
      {
        EPOLLIN = 0x001,
    #define EPOLLIN EPOLLIN
        EPOLLPRI = 0x002,
    #define EPOLLPRI EPOLLPRI
        EPOLLOUT = 0x004,
    #define EPOLLOUT EPOLLOUT
        EPOLLRDNORM = 0x040,
    #define EPOLLRDNORM EPOLLRDNORM
        EPOLLRDBAND = 0x080,
    #define EPOLLRDBAND EPOLLRDBAND
        EPOLLWRNORM = 0x100,
    #define EPOLLWRNORM EPOLLWRNORM
        EPOLLWRBAND = 0x200,
    #define EPOLLWRBAND EPOLLWRBAND
        EPOLLMSG = 0x400,
    #define EPOLLMSG EPOLLMSG
        EPOLLERR = 0x008,
    #define EPOLLERR EPOLLERR
        EPOLLHUP = 0x010,
    #define EPOLLHUP EPOLLHUP
        EPOLLRDHUP = 0x2000,
    #define EPOLLRDHUP EPOLLRDHUP
        EPOLLEXCLUSIVE = 1u << 28,
    #define EPOLLEXCLUSIVE EPOLLEXCLUSIVE
        EPOLLWAKEUP = 1u << 29,
    #define EPOLLWAKEUP EPOLLWAKEUP
        EPOLLONESHOT = 1u << 30,
    #define EPOLLONESHOT EPOLLONESHOT
        EPOLLET = 1u << 31
    #define EPOLLET EPOLLET
      };
    
    
    /* Valid opcodes ( "op" parameter ) to issue to epoll_ctl().  */
    #define EPOLL_CTL_ADD 1        /* Add a file descriptor to the interface.  */
    #define EPOLL_CTL_DEL 2        /* Remove a file descriptor from the interface.  */
    #define EPOLL_CTL_MOD 3        /* Change file descriptor epoll_event structure.  */
    
    
    typedef union epoll_data
    {
      void *ptr;
      int fd;
      uint32_t u32;
      uint64_t u64;
    } epoll_data_t;
    
    struct epoll_event
    {
      uint32_t events;        /* Epoll events */
      epoll_data_t data;        /* User data variable */
    } __EPOLL_PACKED;
    
    
    
    extern int epoll_create (int __size);
    
    extern int epoll_create1 (int __flags);
    
    extern int epoll_ctl (int __epfd, int __op, int __fd,
                          struct epoll_event *__event);
    extern int epoll_wait (int __epfd, struct epoll_event *__events,
                           int __maxevents, int __timeout);
     
    extern int epoll_pwait (int __epfd, struct epoll_event *__events,
                            int __maxevents, int __timeout,
                            const __sigset_t *__ss);
    
    
    #endif /* sys/epoll.h */
