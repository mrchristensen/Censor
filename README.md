# Censor

Censor static analyzer that attempts to disprove the existence of data races in OpenMP programs. It uses ideas from Abstracting Abstract Machines, SP-bags, computation graphs, and other research.

### Table of Contents
[TOC]

# Pre-requisites

This tool depends on pycparser 2.15 or later (2.15 added support for pragmas, which are essential to OpenMP). Pycparser is available through standard package managers, including pip. However, Ubuntu LTS's version is currently behind this version and pip only includes the source, not the fake headers.

As a temporary fix, we cloned the pycparser master branch from [github](https://github.com/eliben/pycparser.git "Github.com - pycparser repository"). You can notify main.py of the location of pycparser in one of two ways:

1. create a symbolic link _inside_ the censor repository named *pycparser* to the pycparser directory

2. Pass the path to pycparser while running main.py with the -p flag (i.e. `./main.py -p /path/to/pycparser my_code.c`).

# Running the Tool

There are two major ways to run the tool:

## main.py

The first option is to use main.py, which will parse, transform, and interpret concretely (using the concrete cesk interpreter found in *cesk/__init__.py*) a given file (see [cesk_main.py](#cesk_main.py) to run an abstract interpretation).

Arguments | Example | Description
--------- | ------- | -----------
*--sanitize* or *-s* | `` | Remove typedefs added by fake includes
*--includes* or *-i* | `` | Comma separated includes for preprocessing use
*--configuration* or *-c* | `./main.py -c gcc my_code.c` | Choose between 'gcc' or 'std' modes of configuration
*--pycparser* or *-p* | `./main.py -p /path/to/pycparser my_code.c` | The path to pycparser (instead of a symbolic link, pass in the path of pycparser) %%%
*--tool* or *-t* | `./main.py -t transform my_code.c` | Select a tool for the type of analysis: *censor* - produces an untransformed AST, *observer* - %%%, *ssl* - %%%, *print* - produces an untransformed and transformed AST,*transform* - produces the desugared and transformed code, *instrumenter* - %%%
[//]: # it's an option, but I'm not sure what it does: "filenames" | `` | nargs='+'

- to run similar to gcc use the config flag ex:(-c cesk) or (-c gcc)

### print
- (Ex: `./main.py -st print my_code.c`)

- Parses the c file, prints the resulting ast, transforms the ast, then prints the resulting ast

- run with the --sanitize(-s) flag to clean the stdlib includes

### transform
- (Ex: `./main.py -st transform my_code.c`)

- Parses the c file, transforms the ast, converts it back to c code, then prints the result

- run with the --sanitize(-s) flag to clean the stdlib includes


## cesk_main.py
Preprocessing is automatically on. Default config mode. Running cesk_main.py will parse, transform, and interpret the given file concretely.

Arguments | Example | Description
--------- | ------- | -----------
*--no_preprocess* or *-n* | `` | Skips preprocessing during - Do not preprocess the file (this is because cesk_main defaults on running preprocessing)
*--pycparser* or *-p* | `./cesk_main.py -p /path/to/pycparser my_code.c` | The path to pycparser (instead of a symbolic link, pass in the path of pycparser) %%%
*--graph* or *-g* | `./cesk_main.py -g my_graph.dot my_code.c` | Provide the flag and the name of your graph to generate an abstract state graph
*--configuration* or *-c* | `./cesk_main.py -c CONCRETE my_code.c` | Include the flag and declare the configuration for the interpreter. Configuration options include:  *CONCRETE*, *ABSTRACT*, or *TRIVIAL* (see *cesk/config.py* for more information about each configuration and to create custom configurations).
includes* or *-I* | `` | Comma separated includes for preprocessing %%%
*--inject* or *-j* | `./cesk_main -j my_function my_code.c` | Give the name of a function where you want to inject the analysis
*--serialize_ast_parsing* or *-sp* | `` | Add serialized pickle option argument %%% Skip parsing by passing in a pickle file or Skip parsing and transforming by passing in a pickle file%%%
*--serialize_ast_transform* or *-st* | `` | Add serialized pickle option argument %%% Skip parsing by passing in a pickle file or Skip parsing and transforming by passing in a pickle file%%%

### Preprocessing
 - Skip preprocessing %%%

### Pycparser
 - something with pycparser (instead of a symbolic link, pass in the path of pycparser) %%%

### Include Files
 - includes (like, -c) %%%

### %%% Configuration
 - Add configuration options argument (like, -c) %%%

### Injection Point
 - Add injection argument %%%

### Serialization
 - Add serialized pickle option argument %%%


# Testing
- To run all regression tests run *all_tests.py* in the *tests/* directory to run regression suite

- The cesk interpreter is the exception. Its tests can be found in *cesk/tests/*. Run *all_tests.py* to test %%%

- You can easily test just one c interpreted file by running `run_one_file.py <cfile>` (in both the *tests/* and *cesk/tests/* directories)


[//]: # (## yeti todo)

[//]: # (## ssl todo)

[//]: # (## observer todo)

[//]: # (## censor todo)

# Planned Features
 - The ability to read in multiple files

# Resources

### Censor Documentation
- [A more formal documentation](https://docs.google.com/document/d/1c4LMd-DxPy1ntg60aG3siy1Rk_qRbrXNaJbwxlEBjZI/edit?usp=sharing "Google Docs") detailing specs of the C99 Standard, including what is and is not supported. A brief overview of the project is also included.

### Tool Paper
- [A tool paper](https://faculty.cs.byu.edu/~pdiddy/papers/c-aam.pdf "cs.byu.edu") explaining what Censor aims to be and how it meets those needs. This paper focuses specifically on memory safety and includes semantics of the project. The conclusion is drawn that this tool is reasons precisely and soundly about pointer arithmetic and can be used also as a general purpose analyzer.

### Slides
- [An overview](https://docs.google.com/presentation/d/1SiNiSmVXSTOX46d7Ub0krtgvWtgjmZa1mFTKfofiVXQ/edit?usp=sharing "Google Slides") of the abstract interpretation model of YAAM (BYU's Abstracting Abstract Machine) which covers the different types of allocation, arithmetic values, and memory model. Emphasis is placed on understanding the memory model, the virtual store and how it updates, and the address model that was implemented.

### Diagram
- [A simple diagram](https://www.lucidchart.com/invitations/accept/931a0544-c973-4a39-9e32-8a884f57f445 "Lucid Charts") of the major parts of the Censor codebase and a sequence diagram.



[//]: # (## talk about list)
[//]: # (## get rid of all double spaces)
[//]: # (## talk about how to insert the pycparser hook)