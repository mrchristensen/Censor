"""Verifies the correctness of function calling order."""
from pycparser import c_ast
from .funccall_order import FuncCallOrder

def verify_openssl_correctness(ast):
    """Verifies the correctness of function calling order. For an OpenSSL
    Program"""
    ssl_ordering = {
        'some_SSL_funcion': ['some_SSL_funcion',
                             'other_SSL_function',
                             'another_other_SSL_function']
    }
    return verify_correctness(ast, ssl_ordering)

def verify_correctness(ast, defined_orders):
    """Verifies the correctness of function calling order."""
    actual_orders = FuncCallOrder().get_call_order(ast)

    for funcdef in actual_orders:
        a_order = list(map(_get_name, actual_orders[funcdef]))
        for i, funcname in enumerate(a_order):
            if funcname in defined_orders:
                d_order = defined_orders[funcname]
                if not a_order[i:i + len(d_order)] == defined_orders[funcname]:
                    return False
    return True

def _get_name(node):
    """Takes in a FuncCall node and returns the name as a string."""
    if isinstance(node.name, c_ast.ID):
        return node.name.name
    else:
        raise NotImplementedError("Currently we only support calling a " \
        + "function using an identifier, not through a pointer.")
