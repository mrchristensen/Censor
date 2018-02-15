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

class NodeTransformer(pycparser.c_ast.NodeVisitor):
    """Base abstract NodeTransformer class"""

    def skip(self, node): #pylint: disable=no-self-use
        """Override to not scan past certain types of nodes"""
        return node is None

    def generic_visit(self, node):
        """Generic visit function"""
        for field in node.__class__.__slots__:
            old_value = getattr(node, field, None)
            if self.skip(old_value):
                continue
            elif isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if self.skip(value):
                        new_values.append(value)
                        continue
                    elif isinstance(value, (pycparser.c_ast.Node, omp.omp_ast.Node)):
                        value = self.visit(value)
                        if value is None:
                            continue
                        elif not isinstance(value, (pycparser.c_ast.Node, omp.omp_ast.Node)):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, (pycparser.c_ast.Node, omp.omp_ast.Node)):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node
