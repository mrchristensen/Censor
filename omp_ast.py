#-----------------------------------------------------------------
# ** ATTENTION **
# This code was automatically generated from the file:
# _omp_ast.cfg
#
# Do not modify it directly. Modify the configuration file and
# run the generator again.
# ** ** *** ** **
#
# pycparser: c_ast.py
#
# AST Node classes.
#
# Eli Bendersky [http://eli.thegreenplace.net]
# License: BSD
#-----------------------------------------------------------------


import sys


class Node(object):
    __slots__ = ()
    """ Abstract base class for AST nodes.
    """
    def children(self):
        """ A sequence of all children that are Nodes
        """
        pass

    def show(self, buf=sys.stdout, offset=0, attrnames=False, nodenames=False, showcoord=False, _my_node_name=None):
        """ Pretty print the Node and all its attributes and
            children (recursively) to a buffer.

            buf:
                Open IO buffer into which the Node is printed.

            offset:
                Initial offset (amount of leading spaces)

            attrnames:
                True if you want to see the attribute names in
                name=value pairs. False to only see the values.

            nodenames:
                True if you want to see the actual node names
                within their parents.

            showcoord:
                Do you want the coordinates of each Node to be
                displayed.
        """
        lead = ' ' * offset
        if nodenames and _my_node_name is not None:
            buf.write(lead + self.__class__.__name__+ ' <' + _my_node_name + '>: ')
        else:
            buf.write(lead + self.__class__.__name__+ ': ')

        if self.attr_names:
            if attrnames:
                nvlist = [(n, getattr(self,n)) for n in self.attr_names]
                attrstr = ', '.join('%s=%s' % nv for nv in nvlist)
            else:
                vlist = [getattr(self, n) for n in self.attr_names]
                attrstr = ', '.join('%s' % v for v in vlist)
            buf.write(attrstr)

        if showcoord:
            buf.write(' (at %s)' % self.coord)
        buf.write('\n')

        for (child_name, child) in self.children():
            child.show(
                buf,
                offset=offset + 2,
                attrnames=attrnames,
                nodenames=nodenames,
                showcoord=showcoord,
                _my_node_name=child_name)


class NodeVisitor(object):
    """ A base NodeVisitor class for visiting c_ast nodes.
        Subclass it and define your own visit_XXX methods, where
        XXX is the class name you want to visit with these
        methods.

        For example:

        class ConstantVisitor(NodeVisitor):
            def __init__(self):
                self.values = []

            def visit_Constant(self, node):
                self.values.append(node.value)

        Creates a list of values of all the constant nodes
        encountered below the given node. To use it:

        cv = ConstantVisitor()
        cv.visit(node)

        Notes:

        *   generic_visit() will be called for AST nodes for which
            no visit_XXX method was defined.
        *   The children of nodes for which a visit_XXX was
            defined will not be visited - if you need this, call
            generic_visit() on the node.
            You can use:
                NodeVisitor.generic_visit(self, node)
        *   Modeled after Python's own AST visiting facilities
            (the ast module of Python 3.0)
    """

    _method_cache = None

    def visit(self, node):
        """ Visit a node.
        """

        if self._method_cache is None:
            self._method_cache = {}

        visitor = self._method_cache.get(node.__class__.__name__, None)
        if visitor is None:
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            self._method_cache[node.__class__.__name__] = visitor

        return visitor(node)

    def generic_visit(self, node):
        """ Called if no explicit visitor function exists for a
            node. Implements preorder visiting of the node.
        """
        for c in node:
            self.visit(c)

class OmpParallel(Node):
    __slots__ = ('clauses', 'block', 'coord', '__weakref__')
    def __init__(self, clauses, block, coord=None):
        self.clauses = clauses
        self.block = block
        self.coord = coord

    def children(self):
        nodelist = []
        if self.block is not None: nodelist.append(("block", self.block))
        return tuple(nodelist)

    def __iter__(self):
        if self.block is not None:
            yield self.block

    attr_names = ('clauses', )

class OmpFor(Node):
    __slots__ = ('clauses', 'loops', 'coord', '__weakref__')
    def __init__(self, clauses, loops, coord=None):
        self.clauses = clauses
        self.loops = loops
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.loops or []):
            nodelist.append(("loops[%d]" % i, child))
        return tuple(nodelist)

    def __iter__(self):
        for child in (self.loops or []):
            yield child

    attr_names = ('clauses', )

class OmpSections(Node):
    __slots__ = ('clauses', 'sections', 'coord', '__weakref__')
    def __init__(self, clauses, sections, coord=None):
        self.clauses = clauses
        self.sections = sections
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.sections or []):
            nodelist.append(("sections[%d]" % i, child))
        return tuple(nodelist)

    def __iter__(self):
        for child in (self.sections or []):
            yield child

    attr_names = ('clauses', )

class OmpSection(Node):
    __slots__ = ('block', 'coord', '__weakref__')
    def __init__(self, block, coord=None):
        self.block = block
        self.coord = coord

    def children(self):
        nodelist = []
        if self.block is not None: nodelist.append(("block", self.block))
        return tuple(nodelist)

    def __iter__(self):
        if self.block is not None:
            yield self.block

    attr_names = ()

class OmpSingle(Node):
    __slots__ = ('clauses', 'block', 'coord', '__weakref__')
    def __init__(self, clauses, block, coord=None):
        self.clauses = clauses
        self.block = block
        self.coord = coord

    def children(self):
        nodelist = []
        if self.block is not None: nodelist.append(("block", self.block))
        return tuple(nodelist)

    def __iter__(self):
        if self.block is not None:
            yield self.block

    attr_names = ('clauses', )

class OmpSimd(Node):
    __slots__ = ('clauses', 'loops', 'coord', '__weakref__')
    def __init__(self, clauses, loops, coord=None):
        self.clauses = clauses
        self.loops = loops
        self.coord = coord

    def children(self):
        nodelist = []
        if self.loops is not None: nodelist.append(("loops", self.loops))
        return tuple(nodelist)

    def __iter__(self):
        if self.loops is not None:
            yield self.loops

    attr_names = ('clauses', )

class OmpDeclareSimd(Node):
    __slots__ = ('clauses', 'func', 'coord', '__weakref__')
    def __init__(self, clauses, func, coord=None):
        self.clauses = clauses
        self.func = func
        self.coord = coord

    def children(self):
        nodelist = []
        if self.func is not None: nodelist.append(("func", self.func))
        return tuple(nodelist)

    def __iter__(self):
        if self.func is not None:
            yield self.func

    attr_names = ('clauses', )

class OmpForSimd(Node):
    __slots__ = ('clauses', 'loops', 'coord', '__weakref__')
    def __init__(self, clauses, loops, coord=None):
        self.clauses = clauses
        self.loops = loops
        self.coord = coord

    def children(self):
        nodelist = []
        if self.loops is not None: nodelist.append(("loops", self.loops))
        return tuple(nodelist)

    def __iter__(self):
        if self.loops is not None:
            yield self.loops

    attr_names = ('clauses', )

class OmpTask(Node):
    __slots__ = ('clauses', 'block', 'coord', '__weakref__')
    def __init__(self, clauses, block, coord=None):
        self.clauses = clauses
        self.block = block
        self.coord = coord

    def children(self):
        nodelist = []
        if self.block is not None: nodelist.append(("block", self.block))
        return tuple(nodelist)

    def __iter__(self):
        if self.block is not None:
            yield self.block

    attr_names = ('clauses', )

class OmpTaskloop(Node):
    __slots__ = ('clauses', 'loops', 'coord', '__weakref__')
    def __init__(self, clauses, loops, coord=None):
        self.clauses = clauses
        self.loops = loops
        self.coord = coord

    def children(self):
        nodelist = []
        if self.loops is not None: nodelist.append(("loops", self.loops))
        return tuple(nodelist)

    def __iter__(self):
        if self.loops is not None:
            yield self.loops

    attr_names = ('clauses', )

class OmpTaskloopSimd(Node):
    __slots__ = ('clauses', 'loops', 'coord', '__weakref__')
    def __init__(self, clauses, loops, coord=None):
        self.clauses = clauses
        self.loops = loops
        self.coord = coord

    def children(self):
        nodelist = []
        if self.loops is not None: nodelist.append(("loops", self.loops))
        return tuple(nodelist)

    def __iter__(self):
        if self.loops is not None:
            yield self.loops

    attr_names = ('clauses', )

class OmpTaskyield(Node):
    __slots__ = ('coord', '__weakref__')
    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        return ()

    def __iter__(self):
        return
        yield

    attr_names = ()

class OmpMaster(Node):
    __slots__ = ('block', 'coord', '__weakref__')
    def __init__(self, block, coord=None):
        self.block = block
        self.coord = coord

    def children(self):
        nodelist = []
        if self.block is not None: nodelist.append(("block", self.block))
        return tuple(nodelist)

    def __iter__(self):
        if self.block is not None:
            yield self.block

    attr_names = ()

class OmpCritical(Node):
    __slots__ = ('name', 'hint', 'block', 'coord', '__weakref__')
    def __init__(self, name, hint, block, coord=None):
        self.name = name
        self.hint = hint
        self.block = block
        self.coord = coord

    def children(self):
        nodelist = []
        if self.block is not None: nodelist.append(("block", self.block))
        return tuple(nodelist)

    def __iter__(self):
        if self.block is not None:
            yield self.block

    attr_names = ('name', 'hint', )

class OmpBarrier(Node):
    __slots__ = ('coord', '__weakref__')
    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        return ()

    def __iter__(self):
        return
        yield

    attr_names = ()

class OmpTaskwait(Node):
    __slots__ = ('coord', '__weakref__')
    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        return ()

    def __iter__(self):
        return
        yield

    attr_names = ()

class OmpTaskgroup(Node):
    __slots__ = ('block', 'coord', '__weakref__')
    def __init__(self, block, coord=None):
        self.block = block
        self.coord = coord

    def children(self):
        nodelist = []
        if self.block is not None: nodelist.append(("block", self.block))
        return tuple(nodelist)

    def __iter__(self):
        if self.block is not None:
            yield self.block

    attr_names = ()

class OmpAtomic(Node):
    __slots__ = ('seq_cst', 'atomic_clause', 'block', 'coord', '__weakref__')
    def __init__(self, seq_cst, atomic_clause, block, coord=None):
        self.seq_cst = seq_cst
        self.atomic_clause = atomic_clause
        self.block = block
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    def __iter__(self):
        return
        yield

    attr_names = ('seq_cst', 'atomic_clause', 'block', )

class OmpFlush(Node):
    __slots__ = ('id_list', 'coord', '__weakref__')
    def __init__(self, id_list, coord=None):
        self.id_list = id_list
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.id_list or []):
            nodelist.append(("id_list[%d]" % i, child))
        return tuple(nodelist)

    def __iter__(self):
        for child in (self.id_list or []):
            yield child

    attr_names = ()

class OmpOrdered(Node):
    __slots__ = ('clauses', 'block', 'coord', '__weakref__')
    def __init__(self, clauses, block, coord=None):
        self.clauses = clauses
        self.block = block
        self.coord = coord

    def children(self):
        nodelist = []
        if self.block is not None: nodelist.append(("block", self.block))
        return tuple(nodelist)

    def __iter__(self):
        if self.block is not None:
            yield self.block

    attr_names = ('clauses', )

class OmpCancel(Node):
    __slots__ = ('construct_type', 'if_clause', 'coord', '__weakref__')
    def __init__(self, construct_type, if_clause, coord=None):
        self.construct_type = construct_type
        self.if_clause = if_clause
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    def __iter__(self):
        return
        yield

    attr_names = ('construct_type', 'if_clause', )

class OmpCancellationPoint(Node):
    __slots__ = ('construct_type', 'coord', '__weakref__')
    def __init__(self, construct_type, coord=None):
        self.construct_type = construct_type
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    def __iter__(self):
        return
        yield

    attr_names = ('construct_type', )

class OmpThreadprivate(Node):
    __slots__ = ('vars', 'coord', '__weakref__')
    def __init__(self, vars, coord=None):
        self.vars = vars
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.vars or []):
            nodelist.append(("vars[%d]" % i, child))
        return tuple(nodelist)

    def __iter__(self):
        for child in (self.vars or []):
            yield child

    attr_names = ()

class OmpDeclareReduction(Node):
    __slots__ = ('reduction_id', 'types', 'combiner', 'initializer', 'coord', '__weakref__')
    def __init__(self, reduction_id, types, combiner, initializer, coord=None):
        self.reduction_id = reduction_id
        self.types = types
        self.combiner = combiner
        self.initializer = initializer
        self.coord = coord

    def children(self):
        nodelist = []
        if self.reduction_id is not None: nodelist.append(("reduction_id", self.reduction_id))
        if self.combiner is not None: nodelist.append(("combiner", self.combiner))
        for i, child in enumerate(self.types or []):
            nodelist.append(("types[%d]" % i, child))
        return tuple(nodelist)

    def __iter__(self):
        if self.reduction_id is not None:
            yield self.reduction_id
        if self.combiner is not None:
            yield self.combiner
        for child in (self.types or []):
            yield child

    attr_names = ('initializer', )

