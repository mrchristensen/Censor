"""
Base NodeTransformer class that every transform implements

Based on python's NodeTransformer class

https://github.com/python/cpython/blob/3.0/Lib/ast.py
"""

from pycparser.c_ast import Node, NodeVisitor

class NodeTransformer(NodeVisitor): #pylint: disable=too-few-public-methods
    """Base abstract NodeTransformer class"""

    def generic_visit(self, node):
        """Generic visit function"""
        for field in node.__class__.__slots__:
            old_value = getattr(node, field, None)
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, Node):
                        value = self.visit(value)
                        if value is None:
                            continue
                        elif not isinstance(value, Node):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, Node):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node
