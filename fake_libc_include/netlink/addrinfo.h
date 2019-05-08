#include <stdio.h>

struct addrinfo {
    int ai_flags;
    struct addrinfo *ai_next;
};