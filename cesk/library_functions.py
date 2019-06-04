""" Set of cstd library functions with a CESK specific implementation:
need the state and an array containing the values of the arguements passed """
import re
import random
import cesk.values as values
import cesk.values.base_values as BV
import cesk.config as cnf
import cesk.limits as limits
#from cesk.values.abstract_literals import AbstractLiterals as AL


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
