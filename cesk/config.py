""" File to store global options for CESK """

import logging

CONFIG = {
    'store_update' : 'strong',   # {strong, weak}
    'limits'       : 'CESK',     # {cesk, gcc, std}
    'allocK'       : 'concrete',    # {concrete, 0-cfa, p4f}
    'allocF'       : 'concrete',    # {concrete, 0-cfa}
    'allocH'       : 'concrete', # {concrete, abstract}
    'log'          : 'INFO'  # {INFO, DEBUG}
    }


"""

store_update
    strong: all updates to the store are replaced with the new value
    weak:   uses abstraction of value types to update
"""

def get_log_level():
    """Parse log level from config string"""
    if CONFIG['log'] == "DEBUG":
        return logging.DEBUG
    else:
        return logging.INFO
