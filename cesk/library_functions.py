""" Set of cstd library functions with a CESK specific implementation:
need the state and an array containing the values of the arguements passed """
import re


def printf(state, args):
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
    return state.get_next()

def free(state, args):#pylint: disable=unused-argument
    """ Completes a free operation """
    return state.get_next()
