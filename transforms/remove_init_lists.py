"""
Both for implementing certain transforms (e.g. inserting explicit type casts)
and for doing the interpreting, dealing with initializer lists like

int a[3] = {1, 3, 7};

will be difficult, especially in cases of array and struct initializer lists
arbitrarily nested inside of one another. This transfrom will take the above to

int a[3];
a[0] = 1;
a[1] = 3;
a[2] = 7;

This is great, but we can't do it for globally declared arrays/structs because
a[0] = 1; can't exist at the global scope. So a program with globally
initialized objects, like this:

int a[2] = {1,3};
int main() {
    .
    .
}
int b[2] = {2,4};
.

will be transformed into this:

int a[2] = {1,3};
void censorXXINIT_GLOBALS();
int main() {
    censorXXINIT_GLOBALS();
    .
    .
}

int b[2] = {2,4};
.
.
void censorXXINIT_GLOBALS() {
    a[0] = 1;
    a[1] = 3;
    b[0] = 2;
    b[1] = 4;
}
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
