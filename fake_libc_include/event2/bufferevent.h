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
 #ifndef _EVENT2_BUFFEREVENT_H_
 #define _EVENT2_BUFFEREVENT_H_
 
 #ifdef __cplusplus
 extern "C" {
 #endif
 
 #include <event2/event-config.h>
 #ifdef _EVENT_HAVE_SYS_TYPES_H
 #include <sys/types.h>
 #endif
 #ifdef _EVENT_HAVE_SYS_TIME_H
 #include <sys/time.h>
 #endif
 
 /* For int types. */
 #include <event2/util.h>
 
 #define BEV_EVENT_READING   0x01    
 #define BEV_EVENT_WRITING   0x02    
 #define BEV_EVENT_EOF       0x10    
 #define BEV_EVENT_ERROR     0x20    
 #define BEV_EVENT_TIMEOUT   0x40    
 #define BEV_EVENT_CONNECTED 0x80    
 struct bufferevent
 #ifdef _EVENT_IN_DOXYGEN
 {}
 #endif
 ;
 struct event_base;
 struct evbuffer;
 //struct sockaddr;
 
 typedef void (*bufferevent_data_cb)(struct bufferevent *bev, void *ctx);
 
 typedef void (*bufferevent_event_cb)(struct bufferevent *bev, short what, void *ctx);
 
 enum bufferevent_options {
     BEV_OPT_CLOSE_ON_FREE = (1<<0),
 
     BEV_OPT_THREADSAFE = (1<<1),
 
     BEV_OPT_DEFER_CALLBACKS = (1<<2),
 
     BEV_OPT_UNLOCK_CALLBACKS = (1<<3)
 };
 
 struct bufferevent *bufferevent_socket_new(struct event_base *base, evutil_socket_t fd, int options);
 
 int bufferevent_socket_connect(struct bufferevent *, struct sockaddr *, int);
 
 struct evdns_base;
 int bufferevent_socket_connect_hostname(struct bufferevent *,
     struct evdns_base *, int, const char *, int);
 
 int bufferevent_socket_get_dns_error(struct bufferevent *bev);
 
 int bufferevent_base_set(struct event_base *base, struct bufferevent *bufev);
 
 struct event_base *bufferevent_get_base(struct bufferevent *bev);
 
 int bufferevent_priority_set(struct bufferevent *bufev, int pri);
 
 
 void bufferevent_free(struct bufferevent *bufev);
 
 
 void bufferevent_setcb(struct bufferevent *bufev,
     bufferevent_data_cb readcb, bufferevent_data_cb writecb,
     bufferevent_event_cb eventcb, void *cbarg);
 
 int bufferevent_setfd(struct bufferevent *bufev, evutil_socket_t fd);
 
 evutil_socket_t bufferevent_getfd(struct bufferevent *bufev);
 
 struct bufferevent *bufferevent_get_underlying(struct bufferevent *bufev);
 
 int bufferevent_write(struct bufferevent *bufev,
     const void *data, size_t size);
 
 
 int bufferevent_write_buffer(struct bufferevent *bufev, struct evbuffer *buf);
 
 
 size_t bufferevent_read(struct bufferevent *bufev, void *data, size_t size);
 
 int bufferevent_read_buffer(struct bufferevent *bufev, struct evbuffer *buf);
 
 struct evbuffer *bufferevent_get_input(struct bufferevent *bufev);
 
 struct evbuffer *bufferevent_get_output(struct bufferevent *bufev);
 
 int bufferevent_enable(struct bufferevent *bufev, short event);
 
 int bufferevent_disable(struct bufferevent *bufev, short event);
 
 short bufferevent_get_enabled(struct bufferevent *bufev);
 
 int bufferevent_set_timeouts(struct bufferevent *bufev,
     const struct timeval *timeout_read, const struct timeval *timeout_write);
 
 void bufferevent_setwatermark(struct bufferevent *bufev, short events,
     size_t lowmark, size_t highmark);
 
 void bufferevent_lock(struct bufferevent *bufev);
 
 void bufferevent_unlock(struct bufferevent *bufev);
 
 enum bufferevent_flush_mode {
     BEV_NORMAL = 0,
 
     BEV_FLUSH = 1,
 
     BEV_FINISHED = 2
 };
 
 int bufferevent_flush(struct bufferevent *bufev,
     short iotype,
     enum bufferevent_flush_mode mode);
 
 enum bufferevent_filter_result {
     BEV_OK = 0,
 
     BEV_NEED_MORE = 1,
 
     BEV_ERROR = 2
 };
 
 typedef enum bufferevent_filter_result (*bufferevent_filter_cb)(
     struct evbuffer *src, struct evbuffer *dst, ev_ssize_t dst_limit,
     enum bufferevent_flush_mode mode, void *ctx);
 
 struct bufferevent *
 bufferevent_filter_new(struct bufferevent *underlying,
                bufferevent_filter_cb input_filter,
                bufferevent_filter_cb output_filter,
                int options,
                void (*free_context)(void *),
                void *ctx);
 int bufferevent_pair_new(struct event_base *base, int options,
     struct bufferevent *pair[2]);
 
 struct bufferevent *bufferevent_pair_get_partner(struct bufferevent *bev);
 
 struct ev_token_bucket_cfg;
 
 struct bufferevent_rate_limit_group;
 
 #define EV_RATE_LIMIT_MAX EV_SSIZE_MAX
 
 struct ev_token_bucket_cfg *ev_token_bucket_cfg_new(
     size_t read_rate, size_t read_burst,
     size_t write_rate, size_t write_burst,
     const struct timeval *tick_len);
 
 void ev_token_bucket_cfg_free(struct ev_token_bucket_cfg *cfg);
 
 int bufferevent_set_rate_limit(struct bufferevent *bev,
     struct ev_token_bucket_cfg *cfg);
 
 struct bufferevent_rate_limit_group *bufferevent_rate_limit_group_new(
     struct event_base *base,
     const struct ev_token_bucket_cfg *cfg);
 int bufferevent_rate_limit_group_set_cfg(
     struct bufferevent_rate_limit_group *,
     const struct ev_token_bucket_cfg *);
 
 int bufferevent_rate_limit_group_set_min_share(
     struct bufferevent_rate_limit_group *, size_t);
 
 void bufferevent_rate_limit_group_free(struct bufferevent_rate_limit_group *);
 
 int bufferevent_add_to_rate_limit_group(struct bufferevent *bev,
     struct bufferevent_rate_limit_group *g);
 
 int bufferevent_remove_from_rate_limit_group(struct bufferevent *bev);
 
 ev_ssize_t bufferevent_get_read_limit(struct bufferevent *bev);
 ev_ssize_t bufferevent_get_write_limit(struct bufferevent *bev);
 ev_ssize_t bufferevent_get_max_to_read(struct bufferevent *bev);
 ev_ssize_t bufferevent_get_max_to_write(struct bufferevent *bev);
 
 ev_ssize_t bufferevent_rate_limit_group_get_read_limit(
     struct bufferevent_rate_limit_group *);
 ev_ssize_t bufferevent_rate_limit_group_get_write_limit(
     struct bufferevent_rate_limit_group *);
 int bufferevent_decrement_read_limit(struct bufferevent *bev, ev_ssize_t decr);
 int bufferevent_decrement_write_limit(struct bufferevent *bev, ev_ssize_t decr);
 int bufferevent_rate_limit_group_decrement_read(
     struct bufferevent_rate_limit_group *, ev_ssize_t);
 int bufferevent_rate_limit_group_decrement_write(
     struct bufferevent_rate_limit_group *, ev_ssize_t);
 void bufferevent_rate_limit_group_get_totals(
     struct bufferevent_rate_limit_group *grp,
     ev_uint64_t *total_read_out, ev_uint64_t *total_written_out);
 
 void
 bufferevent_rate_limit_group_reset_totals(
     struct bufferevent_rate_limit_group *grp);
 
 #ifdef __cplusplus
 }
 #endif
 
 #endif /* _EVENT2_BUFFEREVENT_H_ */