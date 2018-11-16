""" File to store global options for CESK """

CONFIG = {
    'values'       : 'concrete',
    'store_update' : 'strong',   # {strong, weak}
    'limits'       : 'CESK',     # {cesk, gcc, std}
    'allocK'       : 'concrete',    # {concrete, 0-cfa, p4f}
    'allocF'       : 'concrete',    # {concrete, 0-cfa}
    'allocH'       : 'concrete'  # {concrete, abstract}
    }


"""

store_update
    strong: all updates to the store are replaced with the new value
    weak:   uses abstraction of value types to update
"""
