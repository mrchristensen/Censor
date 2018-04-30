"""Instrumenter that registers every read and write"""

from copy import deepcopy
from pycparser.c_ast import * # pylint: disable=wildcard-import, unused-wildcard-import
from omp.clause import * # pylint: disable=wildcard-import, unused-wildcard-import
from omp.clause import Reduction, FirstPrivate, LastPrivate
from transforms.lift_node import LiftNode
from transforms.type_helpers import get_type
from transforms.helpers import ensure_compound, append_statement

def has_clause(node, clause):
    """Return true if node has clause"""
    return any(isinstance(c, clause) for c in node.clauses)

def array_ref(name, subscript):
    """Return an ArrayRef AST object"""
    return ArrayRef(ID(name), Constant('int', str(subscript)))

def node_to_address(node):
    """Return an AST node that represents the address accessed"""
    if isinstance(node, UnaryOp):
        if node.op == '&':
            return node
        else:
            return node.expr
    elif isinstance(node, str):
        return UnaryOp('&', ID(node))
    else:
        return UnaryOp('&', node)

class NaiveInstrumenter(LiftNode): #pylint: disable=too-many-public-methods
    """InstrumentReadsAndWrites"""
    def __init__(self, id_generator, environments, envr, registry):
        super().__init__(id_generator, environments)
        self.envr = envr
        self.registry = registry

    def register_node_accesses(self, mode, node, append=False): # pylint: disable=too-many-branches
        """Register accesses for node"""
        read_mode = mode.replace('write', 'read')
        if isinstance(node, BinaryOp):
            self.register_node_accesses(mode, node.left, append)
            self.register_node_accesses(mode, node.right, append)
            return
        elif isinstance(node, FuncCall):
            if node.args is not None:
                for expr in node.args.exprs:
                    self.register_node_accesses(mode, expr, append)
            return
        elif isinstance(node, Cast):
            self.register_node_accesses(mode, node.expr, append)
            return
        elif isinstance(node, Constant):
            return
        elif isinstance(node, UnaryOp):
            if node.op == 'sizeof' or isinstance(node.expr, Constant):
                return
            elif node.op == '*':
                self.register_node_accesses(read_mode, node.expr, append)
            elif node.op == '&':
                self.register_node_accesses(mode, node.expr, append)
                return
        elif isinstance(node, StructRef):
            self.register_node_accesses(read_mode, node.name, append)
        elif isinstance(node, ArrayRef):
            self.register_node_accesses(read_mode, node.name, append)
            self.register_node_accesses(read_mode, node.subscript, append)

        address = node_to_address(node)
        func_call = self.registry.register_memory_access(mode, address)
        if append:
            self.append_to_scope(func_call)
        else:
            self.insert_into_scope(func_call)

    def visit_Assignment(self, node): #pylint: disable=invalid-name
        """Log reads and writes in Assignment node"""
        self.register_node_accesses('read', node.rvalue)
        self.register_node_accesses('write', node.lvalue)
        return node

    def visit_BinaryOp(self, node): #pylint: disable=invalid-name
        """Log reads and writes in BinaryOp node"""
        self.register_node_accesses('read', node)
        return node

    def visit_UnaryOp(self, node): # pylint: disable=invalid-name
        """Log reads and writes in UnaryOp node"""
        if node.op in ['++', '--', 'p--', 'p++']:
            self.register_node_accesses('write', node.expr)
        return node

    def visit_Decl(self, node): # pylint: disable=invalid-name
        """Log reads and writes in Decl node"""
        if node.init is not None:
            self.register_node_accesses('read', node.init)
        return node

    def visit_If(self, node): # pylint: disable=invalid-name
        """Log reads and writes in If conditions"""
        self.register_node_accesses('read', node.cond)
        return self.generic_visit(node)

    def clause_ids_to_nodes(self, id_strs):
        """Convert a list of clause ids to a list of AST nodes expanding
        Array ids to a node for every element"""
        nodes = []
        for id_str in id_strs:
            typ = get_type(id_str, self.envr)
            if isinstance(typ, ArrayDecl):
                indexes = range(0, int(typ.dim.value))
                nodes.extend([array_ref(id_str, i) for i in indexes])
            else:
                nodes.append(ID(id_str))
        return nodes

    def register_clauses(self, mode, omp_node, clauses, append=False):
        """Instrument AST with function calls to register implicit
        reads and writes made by clauses"""
        # TODO throw errors for clauses we don't handle yet
        # TODO handle all clauses that make implicit references to variables
        # schedule
        # if
        # copyin
        # copyprivate
        # num_threads
        if hasattr(omp_node, 'clauses'):
            for clause in omp_node.clauses:
                if isinstance(clause, clauses):
                    for node in self.clause_ids_to_nodes(clause.ids):
                        self.register_node_accesses(mode, node, append)

    def register_clause_reads(self, omp_node):
        """Instrument AST with a list of AST objects to register implicit
        reads made by OpenMP clauses on the omp node"""
        self.register_clauses(
            mode='clause read',
            omp_node=omp_node,
            clauses=(Reduction, FirstPrivate)
            )

    def register_clause_writes(self, omp_node):
        """Instrument AST with a list of AST objects to register implicit
        writes made by OpenMP clauses on the omp node"""
        self.register_clauses(
            mode='clause write',
            omp_node=omp_node,
            clauses=(Reduction, LastPrivate),
            append=True
            )

    def instrument_omp(self, block, construct):
        """Add sandwiching log statements at the beginning and end of an omp
        structured block"""
        block = ensure_compound(block)
        block.block_items.insert(0, self.registry.register_omp_enter(construct))
        block.block_items.append(self.registry.register_omp_exit(construct))
        return block

    def visit_OmpParallel(self, node): #pylint: disable=invalid-name
        """visit_OmpParallel"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'parallel')
        return node

    def visit_OmpFor(self, node): #pylint: disable=invalid-name
        """visit_OmpFor"""
        construct = 'for'
        if has_clause(node, NoWait):
            construct += ' nowait'
        # Hacky way of instrumenting for loop header.
        # Visit the loop header once
        # Copy the nodes to the bottom of the loop body temporarily
        # Visit them there
        # Delete the temp nodes
        # Because of SimplifyOmpFor we can assume a certain format
        # for (Assignment, BinaryOp, Assignment)
        self.register_clause_reads(node)
        self.insert_into_scope(self.registry.register_omp_enter(construct))
        node.loops.init.rvalue = self.visit(node.loops.init.rvalue)
        node.loops.cond = self.visit(node.loops.cond)
        cond = deepcopy(node.loops.cond)
        inc = deepcopy(node.loops.next)
        node.loops.stmt = append_statement(node.loops.stmt, inc)
        node.loops.stmt = append_statement(node.loops.stmt, cond)
        node.loops.stmt = self.visit(node.loops.stmt)
        items = []
        for item in node.loops.stmt.block_items:
            if item != cond and item != inc:
                items.append(item)
        node.loops.stmt.block_items = items
        self.append_to_scope(self.registry.register_omp_exit(construct))
        self.register_clause_writes(node)
        return node

    def visit_OmpSections(self, node): #pylint: disable=invalid-name
        """visit_OmpSections"""
        node = self.generic_visit(node)
        construct = 'sections'
        if has_clause(node, NoWait):
            construct += ' nowait'
        node.block = self.instrument_omp(node.sections, construct)
        return node

    def visit_OmpSection(self, node): #pylint: disable=invalid-name
        """visit_OmpSection"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'section')
        return node

    def visit_OmpSingle(self, node): #pylint: disable=invalid-name
        """visit_OmpSingle"""
        node = self.generic_visit(node)
        construct = 'single'
        if has_clause(node, NoWait):
            construct += ' nowait'
        node.block = self.instrument_omp(node.block, construct)
        return node

    def visit_OmpTask(self, node): #pylint: disable=invalid-name
        """visit_OmpTask"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'task')
        return node

    def visit_OmpMaster(self, node): #pylint: disable=invalid-name
        """visit_OmpMaster"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'master')
        return node

    def visit_OmpCritical(self, node): #pylint: disable=invalid-name
        """visit_OmpCritical"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'critical')
        return node

    def visit_OmpBarrier(self, node): #pylint: disable=invalid-name
        """visit_OmpBarrier"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node, 'barrier')
        return node

    def visit_OmpFlush(self, node): #pylint: disable=invalid-name
        """visit_OmpFlush"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'flush')
        return node

    def visit_OmpTaskloop(self, node): #pylint: disable=invalid-name
        """visit_OmpTaskloop"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.loops, 'taskloop')
        return node

    def visit_OmpTaskwait(self, node): #pylint: disable=invalid-name
        """visit_OmpTaskwait"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node, 'taskwait')
        return node

    def visit_OmpTaskgroup(self, node): #pylint: disable=invalid-name
        """visit_OmpTaskgroup"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'taskgroup')
        return node

    def visit_OmpAtomic(self, node): #pylint: disable=invalid-name
        """visit_OmpAtomic"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'atomic')
        return node

    def visit_OmpCancel(self, node): #pylint: disable=invalid-name
        """visit_OmpCancel"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'cancel')
        return node

    def visit_OmpCancellationPoint(self, node): #pylint: disable=invalid-name
        """visit_OmpCancellationPoint"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'cancellationpoint')
        return node

    def visit_OmpThreadprivate(self, node): #pylint: disable=invalid-name
        """visit_OmpThreadprivate"""
        raise NotImplementedError('Instrumenter: ' + node.pragma)
