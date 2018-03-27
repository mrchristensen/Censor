A static analyzer that attempts to disprove the existence of data races in OpenMP programs. It uses ideas from Abstracting Abstract Machines, SP-bags, computation graphs, and other research.

It depends on pycparser 2.15 or later (2.15 added support for pragmas, which are essential to OpenMP). pycparser is available through standard package managers, including pip. However, Ubuntu LTS's version is currently behind this version and pip only includes the source, not the fake headers.

As a temporary fix, we cloned the pycparser master branch from github (https://github.com/eliben/pycparser.git). You can notify main.py of the locatoin of pycparser in one of two ways:

1. create a symlink _inside_ the censor repository named `pycparser` to the pycparser directory

2. pass "-p /path/to/pycparser" to main.py as a command line argument.

