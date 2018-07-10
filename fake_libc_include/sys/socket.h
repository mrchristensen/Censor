#ifndef SOCKET_H
#define SOCKET_H

#include "_fake_defines.h"
#include "_fake_typedefs.h"

typedef unsigned long socklen_t;

struct addrinfo {
               int              ai_flags;
               int              ai_family;
               int              ai_socktype;
               int              ai_protocol;
               socklen_t        ai_addrlen;
               struct sockaddr *ai_addr;
               char            *ai_canonname;
               struct addrinfo *ai_next;
           };

    int getaddrinfo(const char *node, const char *service,
                       const struct addrinfo *hints,
                       struct addrinfo **res);

   void freeaddrinfo(struct addrinfo *res);

   const char *gai_strerror(int errcode);

#endif
