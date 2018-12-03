""" File to store global options for CESK """

CONFIG = {
    'values'       : 'abstract', #{concrete, abstract}
    'store_update' : 'strong',   # {strong, weak}
    'limits'       : 'CESK',     # {cesk, gcc, std}
    'allocK'       : '0-cfa',    # {concrete, 0-cfa, p4f}
    'allocF'       : '0-cfa',    # {concrete, 0-cfa}
    'allocH'       : 'abstract'  # {concrete, abstract}
    }


"""

store_update
    strong: all updates to the store are replaced with the new value
    weak:   uses abstraction of value types to update
"""
