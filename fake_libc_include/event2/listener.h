 /*
  * Copyright (c) 2000-2007 Niels Provos <provos@citi.umich.edu>
  * Copyright (c) 2007-2012 Niels Provos and Nick Mathewson
  *
  * Redistribution and use in source and binary forms, with or without
  * modification, are permitted provided that the following conditions
  * are met:
  * 1. Redistributions of source code must retain the above copyright
  *    notice, this list of conditions and the following disclaimer.
  * 2. Redistributions in binary form must reproduce the above copyright
  *    notice, this list of conditions and the following disclaimer in the
  *    documentation and/or other materials provided with the distribution.
  * 3. The name of the author may not be used to endorse or promote products
  *    derived from this software without specific prior written permission.
  *
  * THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
  * IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
  * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
  * IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
  * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
  * NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
  * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
  * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
  * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
  * THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
  */
 #ifndef _EVENT2_LISTENER_H_
 #define _EVENT2_LISTENER_H_
 
 #ifdef __cplusplus
 extern "C" {
 #endif
 
 #include <event2/event.h>
 
 struct sockaddr;
 struct evconnlistener;
 
 typedef void (*evconnlistener_cb)(struct evconnlistener *, evutil_socket_t, struct sockaddr *, int socklen, void *);
 
 typedef void (*evconnlistener_errorcb)(struct evconnlistener *, void *);
 
 #define LEV_OPT_LEAVE_SOCKETS_BLOCKING  (1u<<0)
 
 #define LEV_OPT_CLOSE_ON_FREE       (1u<<1)
 
 #define LEV_OPT_CLOSE_ON_EXEC       (1u<<2)
 
 #define LEV_OPT_REUSEABLE       (1u<<3)
 
 #define LEV_OPT_THREADSAFE      (1u<<4)
 
 struct evconnlistener *evconnlistener_new(struct event_base *base,
     evconnlistener_cb cb, void *ptr, unsigned flags, int backlog,
     evutil_socket_t fd);
 struct evconnlistener *evconnlistener_new_bind(struct event_base *base,
     evconnlistener_cb cb, void *ptr, unsigned flags, int backlog,
     const struct sockaddr *sa, int socklen);
 void evconnlistener_free(struct evconnlistener *lev);
 int evconnlistener_enable(struct evconnlistener *lev);
 int evconnlistener_disable(struct evconnlistener *lev);
 
 struct event_base *evconnlistener_get_base(struct evconnlistener *lev);
 
 evutil_socket_t evconnlistener_get_fd(struct evconnlistener *lev);
 
 void evconnlistener_set_cb(struct evconnlistener *lev,
     evconnlistener_cb cb, void *arg);
 
 void evconnlistener_set_error_cb(struct evconnlistener *lev,
     evconnlistener_errorcb errorcb);
 
 #ifdef __cplusplus
 }
 #endif
 
 #endif