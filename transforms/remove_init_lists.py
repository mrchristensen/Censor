"""
Both for implenting certain transforms (e.g. inserting explicit type casts)
and for doing the interpreting, dealing with initializer lists like

int a[3] = {1, 3, 7};

will be difficult, especially in cases of array and struct initializer lists
arbitrarily nested inside of one another. This transfrom will take the above to

int a[3];
a[0] = 1;
a[1] = 3;
a[2] = 7;

Compound initializers will also be removed. If the array is declared as a
global, it will be initialized at the begining of the main function. If is
declared global after the main function, the declaration will be moved to just
above the main function so that is can be initialized at the begining of the
main function. We don't need to worry about moving the declaration because
anything in the init list will be a compile time constant.
"""
# TODO: figure out what to do with cases like
# char wow[100] = "wow"; where an array is initialized
# from a string

from .node_transformer import NodeTransformer

class RemoveInitLists(NodeTransformer):
    """Transform for removing all initializer lists and compound
    initializers."""
    def __init__(self, environments):
        self.environments = environments
        self.env = environments["GLOBAL"]
