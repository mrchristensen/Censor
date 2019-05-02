""" Set of cstd library functions with a CESK specific implementation:
need the state and an array containing the values of the arguements passed """
import logging
import re
import random
import cesk.values as values
import cesk.values.base_values as BV
import cesk.config as cnf
import cesk.limits as limits
#from cesk.values.abstract_literals import AbstractLiterals as AL

def mocked_function(state, args, return_address):#pylint: disable=unused-argument
    '''returns two values to the store, 1 and 2, in order to test the weak store functionality'''
    value = values.generate_constant_value(str(1), 'int')
    state.stor.write(return_address, value)
    value = values.generate_constant_value(str(2), 'int')
    state.stor.write(return_address, value)
    return {state.get_next()}, {}

def hashmap_get(state, args, return_address):#pylint: disable=unused-argument
    '''mocks the functionality of void* hashmap_get(hmap_t* map, unsigned long key)'''
    value = values.generate_null_pointer()
    state.stor.write(return_address, value)
    return {state.get_next()}, {}

def hashmap_add(state, args, return_address):#pylint: disable=unused-argument
    '''mocks the functionality of int hashmap_add(hmap_t* map, unsigned long key, void* value)'''
    value = values.generate_constant_value(str(0), 'int')
    state.stor.write(return_address, value)
    value = values.generate_constant_value(str(1), 'int')
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

def evutil_make_socket_nonblocking(state, args, return_address):
    '''mocks the functionality of evutil_make_socket_nonblocking(evutil_socket_t sock)'''
    value = values.generate_constant_value(str(random.randint(0, 2)), 'int')
    state.stor.write(return_address, value)
    return {state.get_next()}, {}

def tls_server_wrapper_setup(state, args, return_address):
    '''mocks the functionality of tls_conn_ctx_t* tls_server_wrapper_setup(evutil_socket_t efd, evutil_socket_t ifd, tls_daemon_ctx_t* daemon_ctx,
	tls_opts_t* tls_opts, struct sockaddr* internal_addr, int internal_addrlen)'''
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

def __VERIFIER_nondet(state, return_address,#pylint: disable=invalid-name
                      low, high, type_str):
    #The first branch limits the random values that can be produced
    #The second allows all values
    if cnf.CONFIG['values'] == 'concrete':
        rand_value = values.generate_constant_value(
            str(random.randint(low, high)), 'int')
        byte_value = rand_value.get_byte_value()
    else:
        type_size = limits.CONFIG.get_size(type_str.split())
        byte_value = BV.ByteValue(type_size)
    value = values.generate_value(byte_value, type_str)
    errs = set()
    if return_address is not None:
        errs = state.stor.write(return_address, value)
    return {state.get_next()}, errs
def __VERIFIER_nondet_int(state, args, return_address):#pylint: disable=invalid-name,unused-argument
    return __VERIFIER_nondet(state, return_address,
                             -1, 9, 'int')
def __VERIFIER_nondet_char(state, args, return_address):#pylint: disable=invalid-name,unused-argument
    return __VERIFIER_nondet(state, return_address,
                             0, 255, 'char')
def __VERIFIER_nondet_ulong(state, args, return_address):#pylint: disable=invalid-name,unused-argument
    return __VERIFIER_nondet(state, return_address,
                             0, 10, 'unsigned long')



#def alloca(state, args, return_address):#pylint: disable=unused-argument,invalid-name
