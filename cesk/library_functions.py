""" Set of cstd library functions with a CESK specific implementation:
need the state and an array containing the values of the arguements passed """
import re
#import logging
import random
import cesk.values as values
import cesk.values.base_values as BV
import cesk.config as cnf
import cesk.limits as limits
from cesk.values.base_values import SizedSet
#from cesk.values.abstract_literals import AbstractLiterals as AL

#pylint: disable=line-too-long
def mocked_function(state, args, return_address):#pylint: disable=unused-argument
    '''returns two values to the store, 1 and 2, in orderto test the weak store functionality'''
    errs = set()
    value = SizedSet(4)
    value.update({values.generate_constant_value(str(2), 'int'), values.generate_constant_value(str(4), 'int')})
    if return_address is not None:
        errs = state.stor.write(return_address, value)
    return {state.get_next()}, errs

def netlink_notify_kernel(state, args, return_address):#pylint: disable=unused-argument
    '''mocks void netlink_notify_kernel(tls_daemon_ctx_t* ctx, unsigned long id, int response)'''
    return {state.get_next()}, {}

def tls_opts_create(state, args, return_address):#pylint: disable=unused-argument
    '''mocks tls_opts_t* tls_opts_create(char* path)'''
    return {state.get_next()}, {}

def memcpy(state, args, return_address):#pylint: disable=unused-argument
    '''void* __cdecl memcpy(...)'''
    return {state.get_next()}, {}

def nla_get_u64(state, args, return_address):#pylint: disable=unused-argument
    '''mocks uint64_t nla_get_u64(struct nlattr *);'''
    return {state.get_next()}, {}

def nla_data(state, args, return_address):#pylint: disable=unused-argument
    '''mocks void *	nla_data(const struct nlattr *)'''
    return {state.get_next()}, {}

def event_base_new(state, args, return_address):#pylint: disable=unused-argument
    '''mocks struct event_base *event_base_new(void)'''
    return {state.get_next()}, {}

def hashmap_create(state, args, return_address):#pylint: disable=unused-argument
    '''mock hmap_t* hashmap_create(int num_buckets)'''
    #Return: "struct hmap" with "num_buckets = arg[0]" - at also malloc'ed up some stuff
    return {state.get_next()}, {}

def hashmap_get(state, args, return_address):#pylint: disable=unused-argument
    '''mocks void* hashmap_get(hmap_t* map, unsigned long key)'''
    value = values.generate_null_pointer()
    errs = state.stor.write(return_address, value)
    return {state.get_next()}, errs

def hashmap_add(state, args, return_address):#pylint: disable=unused-argument
    '''mocks int hashmap_add(hmap_t* map, unsigned long key, void* value)'''
    value = SizedSet(4)
    value.update({values.generate_constant_value(str(0), 'int'), values.generate_constant_value(str(1), 'int')})
    errs = set()
    if return_address is not None:
        errs = state.stor.write(return_address, value)
    return {state.get_next()}, errs

def socket(state, args, return_address):#pylint: disable=unused-argument
    '''mocks socket(int domain, int type, int protocol)'''
    #TODO make this top
    value = values.generate_constant_value(str(random.randint(0, 2)), 'int')
    errs = state.stor.write(return_address, value)
    return {state.get_next()}, errs

def nla_len(state, args, return_address):#pylint: disable=unused-argument
    '''mocks nla_len()'''
    errs = set()
    # value = str(args[0].nla_len)
    # logging.debug("%%% " + value)
    # errs = state.stor.write(return_address, value)
    return {state.get_next()}, errs

def evutil_make_socket_nonblocking(state, args, return_address):#pylint: disable=unused-argument
    '''mocks evutil_make_socket_nonblocking(evutil_socket_t sock)'''
    value = values.generate_constant_value(str(random.randint(0, 2)), 'int')
    errs = state.stor.write(return_address, value)
    return {state.get_next()}, errs

def tls_server_wrapper_setup(state, args, return_address):#pylint: disable=unused-argument
    '''mocks tls_conn_ctx_t* tls_server_wrapper_setup(evutil_socket_t efd, evutil_socket_t ifd, tls_daemon_ctx_t* daemon_ctx,
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
        # MARKER
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

def __VERIFIER_error(state, args, return_address): #pylint: disable=invalid-name,unused-argument
    return set(), set()

#def alloca(state, args, return_address):#pylint: disable=unused-argument,invalid-name
