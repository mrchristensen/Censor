""" Set of cstd library functions with a CESK specific implementation:
need the state and an array containing the values of the arguements passed """
import logging
import re
import random
import cesk.values as values

def hashmap_get(state, args, return_address):#pylint: disable=unused-argument
    '''mocks the functionality of hashmap_get()'''
    value = values.generate_null_pointer()
    state.stor.write(return_address, value)
    return {state.get_next()}, {}

def socket(state, args, return_address):#pylint: disable=unused-argument
    '''mocks the functionality of socket(int domain, int type, int protocol)'''
    #TODO make this top
    value = values.generate_constant_value(str(random.randint(0, 2)), 'int')
    state.stor.write(return_address, value)
    return {state.get_next()}, {}

def nla_len(state, args, return_address):
    '''mocks the functionality of nla_len()'''
    value = values.generate_constant_value(str(random.randint(0, 2)), 'int')
    state.stor.write(return_address, value)
    return {state.get_next()}, {}

def calloc(state, args, return_address):
    '''mocks the functionality of calloc(size_t num, size_t size)'''
    #TODO make calloc functionality like malloc
    value = values.generate_null_pointer()
    state.stor.write(return_address, value)
    return {state.get_next()},  {}

def evutil_make_socket_nonblocking(state, args, return_address):
    '''mocks the functionality of evutil_make_socket_nonblocking(evutil_socket_t sock)'''
    value = values.generate_constant_value(str(random.randint(0, 2)), 'int')
    state.stor.write(return_address, value)
    return {state.get_next()}, {}

def printf(state, args, return_address):#pylint: disable=unused-argument
    '''performs printf'''
    value_array = []
    for i in range(1, len(args)):
        value_array.append(str(args[i]))

    print_string = args[0]
    print_string = re.sub(r'((?:%%)*)(%[-+ #0]*[0-9]*(\.([0-9]*|\*))?[hlL]?[cdieEfgGosuxXpn])',#pylint: disable=line-too-long
                          r"\1%s", print_string)
    print_string = re.sub(r'%%', '%', print_string)
    print_string = print_string % tuple(value_array)
    print_string = print_string[1:][:-1] #drop quotes
    print_string = print_string.replace("\\n", "\n")
    print(print_string, end="") #convert newlines
    return {state.get_next()}, {}

def free(state, args, return_address):#pylint: disable=unused-argument
    """ Completes a free operation """
    errs = state.stor.free(args[0])
    return {state.get_next()}, errs

def __VERIFIER_nondet_int(state, args, return_address):#pylint: disable=unused-argument,invalid-name
    value = values.generate_constant_value(str(random.randint(0, 2)), 'int')
    errs = set()
    if return_address is not None:
        errs = state.stor.write(return_address, value)
    return {state.get_next()}, errs
