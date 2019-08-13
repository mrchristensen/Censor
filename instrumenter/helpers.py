'''Instrumenter helpers'''

from pycparser.c_ast import Pragma
from transforms.node_transformer import NodeTransformer
from utils import preserve_include_find_end

def is_include(node, lib):
    '''Return true if node is a #pragma BEGIN #include<lib>'''
    return isinstance(node, Pragma) and \
            'include' in node.string and \
            lib in node.string

def find_end_include(node, lib):
    '''Return the index of the #pragma END that matches with
    #pragma BEGIN #include<lib>
    If no match is found then return -1'''
    for i, child in enumerate(node.children()):
        if is_include(child, lib):
            return preserve_include_find_end(node, i)
    return -1

class IncludeDependencies(NodeTransformer):
    '''Include OMP transform'''

    def __init__(self, deps):
        '''Make sure file includes all dependencies'''
        self.deps = deps

    def visit_FileAST(self, node): # pylint:disable=invalid-name,no-self-use
        '''Include dependencies if not already included'''
        has_dep = {}
        for dep in self.deps:
            has_dep[dep] = False
        for child in node.children():
            for dep in self.deps:
                if is_include(child, dep):
                    has_dep[dep] = True
        for dep in self.deps:
            if not has_dep[dep]:
                node.ext.insert(0, Pragma("BEGIN #include<"+dep+">"))
                node.ext.insert(1, Pragma("END"))
        return node
