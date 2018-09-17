A static analyzer that attempts to disprove the existence of data races in OpenMP programs. It uses ideas from Abstracting Abstract Machines, SP-bags, computation graphs, and other research.

It depends on pycparser 2.15 or later (2.15 added support for pragmas, which are essential to OpenMP). pycparser is available through standard package managers, including pip. However, Ubuntu LTS's version is currently behind this version and pip only includes the source, not the fake headers.

As a temporary fix, we cloned the pycparser master branch from github (https://github.com/eliben/pycparser.git). You can notify main.py of the locatoin of pycparser in one of two ways:

1. create a symbolic link _inside_ the censor repository named `pycparser` to the pycparser directory

2. pass "-p /path/to/pycparser" to main.py as a command line argument.

# Description of tool choices in main

## cesk

- (Ex: ./main.py -st cesk my_code.c) or (Ex: ./cesk_main.py my_code.c)

- Parses the c file, transforms the ast, then runs the concrete cesk interpreter found in cesk/\_\_init\_\_.py

- to run similar to gcc use the config flag ex:(-c cesk) or (-c gcc)

## print

- (Ex: ./main.py -st print my_code.c)

- Parses the c file, prints the resulting ast, transforms the ast, then prints the resulting ast

- run with the --sanitize(-s) flag to clean the stdlib includes

## transform

- (Ex: ./main.py -st transform my_code.c)

- Parses the c file, transforms the ast, converts it back to c code, then prints the result

- run with the --sanitize(-s) flag to clean the stdlib includes

# Testing

- To run all regression tests run `all_tests.py` in the tests directory to run regression suite

- The cesk interpreter is the exception. Its tests can be found in cesk/tests. Run `all_tests.py` to test

- You can easily test just one c interpreted file by running `run_one_file.py <cfile>`

[//]: # (## yeti todo)

[//]: # (## ssl todo)

[//]: # (## observer todo)

[//]: # (## censor todo)
- Tests can be found in /tests, /cesk/tests, and /regression/tests.
- Execute `python3 all_tests.py` to run the tests.
