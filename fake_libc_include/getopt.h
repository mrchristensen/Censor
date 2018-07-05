#ifndef GETOPT_H
#define GETOPT_H
#include "_fake_defines.h"
#include "_fake_typedefs.h"


int getopt(int argc, char * const argv[],
                const char *optstring);
int getopt_long(int argc, char * const argv[],
                const char *optstring,
                const struct option *longopts, int *longindex);

int getopt_long_only(int argc, char * const argv[],
                const char *optstring,
                const struct option *longopts, int *longindex);

#endif
