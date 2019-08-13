'''Container of a function definition, should only be accessed as a pointer'''
import cesk.limits as limits

class FunctionDefinition:  #pylint:disable=too-few-public-methods
    '''Contains a function node'''
    def __init__(self, node):
        self.size = limits.CONFIG.get_word_size()
        self.node = node
