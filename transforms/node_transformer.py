"""
Base NodeTransformer class that every transform implements

Based on python's NodeTransformer class

https://github.com/python/cpython/blob/3.0/Lib/ast.py
"""

# Importing both generated AST definitions to use in branch conditions
# We may want to have our omp AST definitions to inherit from pycparsers
# Node class if this causes any more problems.
import pycparser.c_ast
import omp.omp_ast


def is_node(node):
    """Return true if object is an instance of Node"""
    return isinstance(node, (pycparser.c_ast.Node, omp.omp_ast.Node))

class NodeTransformer(pycparser.c_ast.NodeVisitor):
    """
    Base abstract NodeTransformer class
    Subclasses should define 'visit_[__class__.__name__]' methods for any
    AST nodes they want to transform. Ex. 'visit_Compound(self, node)'

    Return None to delete the node
    Return a subclass of Node or a list of them to replace the node
    """

    def skip(self, node): #pylint: disable=no-self-use
        """Override to not scan past certain types of nodes"""
        return node is None

    def generic_visit(self, node):
        for field in node.__class__.__slots__:
            old_value = getattr(node, field, None)
            if self.skip(old_value):
                continue
            elif isinstance(old_value, list):
                old_value[:] = self.visit_list(old_value)
            elif is_node(old_value):
                node = self.visit_node(node, field, old_value)
        return node

    def visit_node(self, node, field, old_value):
        """Visit node. Wrap result in compound if necessary"""
        new_node = self.visit(old_value)
        if new_node is None:
            delattr(node, field)
        elif isinstance(new_node, list):
            # We could check to make sure that `node` can accept
            # a Compound at `field`. `node` should be a While, For, DoWhile etc
            setattr(node, field, pycparser.c_ast.Compound(new_node))
        else:
            setattr(node, field, new_node)
        return node

    def visit_list(self, old_value):
        """Visit each node in a list"""
        new_values = []
        for value in old_value:
            if self.skip(value):
                new_values.append(value)
                continue
            elif is_node(value):
                value = self.visit(value)
                if value is None:
                    continue
                elif isinstance(value, list):
                    new_values.extend(value)
                    continue
            new_values.append(value)
        return new_values
