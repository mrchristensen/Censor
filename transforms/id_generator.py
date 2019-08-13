'''IDGenerator produces identifiers for tranforms to use when they need to
declare an extra variable or label as part of a transform. They are guaranteed
to be unique because they use a counter. They are also guaranteed
not to collide with any valid identifier in the input program because they all
have a prefix not shared by any .

NOTE: If you are chaining multiple transforms that need to generate IDs, you
should give them the same instance of IDGenerator() to ensure that the
transforms use different IDs.
'''

from .node_transformer import NodeTransformer

class IDCollector(NodeTransformer):
    '''Collects all identifers in the given AST and stores them in a set'''

    def __init__(self):
        self.ids = set()

    def visit_ID(self, node): # pylint: disable=invalid-name
        '''Whenever it sees an ID, it adds it to the set as a string.'''
        if node.name is not None:
            self.ids.add(node.name)
        return node

    def visit_Decl(self, node): # pylint: disable=invalid-name
        '''Whenever it sees an Decl, it adds the identifier to the set as
         a string.'''
        if node.name is not None:
            self.ids.add(node.name)
        return node

    def visit_Label(self, node): # pylint: disable=invalid-name
        '''Whenever it sees a Label, it adds the identifier to the set as
        a string.'''
        if node.name is not None:
            self.ids.add(node.name)
        return node

    def get_unique_prefix(self, ast):
        '''Returns a string that is not a prefix of ANY identifiers in the
        given AST.'''
        self.visit(ast)
        prefix = "censor"
        counter = 0
        while True:
            if not is_a_prefix(prefix + str(counter), self.ids):
                break
            counter += 1

        self.ids = set()
        return prefix + str(counter)

def is_a_prefix(prefix, ids):
    '''Checks if prefix is a prefix of any of the strings in IDs'''
    for ident in ids:
        if ident.startswith(prefix):
            return True
    return False

class IDGenerator(object): #pylint:disable=too-few-public-methods
    '''Generates unique IDs to use as labels and variable names.'''
    def __init__(self, ast):
        self.id_count = 0
        self.unique_prefix = IDCollector().get_unique_prefix(ast)

    def get_unique_id(self):
        '''Generates a unique id.'''
        self.id_count += 1
        return self.unique_prefix + str(self.id_count)
