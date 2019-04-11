""" File to store global options for CESK """

CONFIG = {#default values for when cesk main in run
    'values'       : 'abstract', # {concrete, abstract, trivial}
    'store_update' : 'strong',   # {strong, weak} #nill
    'limits'       : 'CESK',     # {cesk, gcc, std}
    'allocK'       : '0-cfa', # {concrete, 0-cfa, p4f, trivial}
    'allocF'       : '0-cfa', # {concrete, 0-cfa, 1-cfa, trivial}
    'allocH'       : 'abstract', # {concrete, abstract, trivial}
    'tick'         : 'abstract'  # {concrete, abstract, trivial}
    }


"""

store_update
    strong: all updates to the store are replaced with the new value
    weak:   stores values that the store could possibly be

allocF
    uses m-cfa allocation not k-cfa
"""

#Groups of configuration types for different analysis
CONCRETE = {
    'values'       : 'concrete', # {concrete, abstract}
    'store_update' : 'strong',   # {strong, weak}
    'limits'       : 'CESK',     # {cesk, gcc, std}
    'allocK'       : 'concrete', # {concrete, 0-cfa, p4f, trivial}
    'allocF'       : 'concrete', # {concrete, 0-cfa, trivial}
    'allocH'       : 'concrete', # {concrete, abstract, trivial}
    'tick'         : 'concrete'  # {concrete, abstract, trivial}
    }
ABSTRACT = {
    'values'       : 'abstract', # {concrete, abstract}
    'store_update' : 'weak',   # {strong, weak}
    'limits'       : 'CESK',     # {cesk, gcc, std}
    'allocK'       : '0-cfa', # {concrete, 0-cfa, p4f, trivial}
    'allocF'       : '0-cfa', # {concrete, 0-cfa, trivial}
    'allocH'       : 'abstract', # {concrete, abstract, trivial}
    'tick'         : 'abstract'  # {concrete, abstract, trivial}
    }
TRIVIAL = {
    'values'       : 'trivial', # {concrete, abstract}
    'store_update' : 'weak',   # {strong, weak} nill
    'limits'       : 'CESK',     # {cesk, gcc, std}
    'allocK'       : 'trivial', # {concrete, 0-cfa, p4f, trivial}
    'allocF'       : '0-cfa', # {concrete, 0-cfa, trivial}
    'allocH'       : 'trivial', # {concrete, abstract, trivial}
    'tick'         : 'abstract'  # {concrete, abstract, trivial}
    }
