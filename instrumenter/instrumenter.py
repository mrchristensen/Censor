'''Instrumenter class for instrumenting an AST'''

from pycparser.c_ast import * # pylint: disable=wildcard-import, unused-wildcard-import
from omp.clause import * # pylint: disable=wildcard-import, unused-wildcard-import
from transforms.lift_node import LiftNode
from transforms.type_helpers import get_type
from transforms.simplify_omp_for import get_iter_var
from instrumenter.logger import Logger, is_yeti

NOT_IMPLEMENTED = (
    If,
    Schedule,
    NumThreads,
    CopyIn,
    CopyPrivate,
    Final,
    Linear
)

def implicit_reference(clause):
    '''Return true if clause makes implicit reference'''
    if isinstance(clause, (CopyIn, CopyPrivate, Linear)):
        # These clauses either always make an implicit reference
        # or are not correctly parsed in every case yet
        return True
    test = None
    if isinstance(clause, If):
        test = str(clause.scalar)
    elif isinstance(clause, Schedule):
        test = str(clause.chunk)
    elif isinstance(clause, NumThreads):
        test = str(clause.num)
    elif isinstance(clause, Final):
        test = str(clause.scalar)
    return test is None or (test.isalnum() and not test.isdigit())

def has_clause(node, clause):
    '''Return true if node has clause'''
    return any(isinstance(c, clause) for c in node.clauses)

def array_ref(name, subscript):
    '''Return an ArrayRef AST object'''
    return ArrayRef(ID(name), Constant('int', str(subscript)))

def node_to_address(node):
    '''Return an AST node that represents the address accessed'''
    if isinstance(node, UnaryOp):
        if node.op == '&':
            return node
        else:
            return node.expr
    elif isinstance(node, str):
        return UnaryOp('&', ID(node))
    else:
        return UnaryOp('&', node)


class Instrumenter(LiftNode): #pylint: disable=too-many-public-methods
    '''InstrumentReadsAndWrites'''
    def __init__(self, id_generator, environments):
        super().__init__(id_generator, environments)
        self.registry = Logger()

    def register_node_accesses(self, mode, node, append=False): # pylint: disable=too-many-branches
        '''Register accesses for node'''
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
        '''Log reads and writes in Assignment node'''
        self.register_node_accesses('read', node.rvalue)
        self.register_node_accesses('write', node.lvalue)
        return node

    def visit_BinaryOp(self, node): #pylint: disable=invalid-name
        '''Log reads and writes in BinaryOp node'''
        self.register_node_accesses('read', node)
        return node

    def visit_UnaryOp(self, node): # pylint: disable=invalid-name
        '''Log reads and writes in UnaryOp node'''
        if node.op in ['++', '--', 'p--', 'p++']:
            self.register_node_accesses('write', node.expr)
        return node

    def visit_Decl(self, node): # pylint: disable=invalid-name
        '''Log reads and writes in Decl node'''
        if node.init is not None:
            self.register_node_accesses('read', node.init)
        return node

    def visit_If(self, node): # pylint: disable=invalid-name
        '''Log reads and writes in If conditions'''
        self.register_node_accesses('read', node.cond)
        return self.generic_visit(node)

    def clause_ids_to_nodes(self, id_strs):
        '''Convert a list of clause ids to a list of AST nodes expanding
        Array ids to a node for every element'''
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
        '''Instrument AST with function calls to register implicit
        reads and writes made by clauses'''
        if hasattr(omp_node, 'clauses'):
            for clause in omp_node.clauses:
                if isinstance(clause, clauses):
                    for node in self.clause_ids_to_nodes(clause.ids):
                        self.register_node_accesses(mode, node, append)
                elif isinstance(clause, NOT_IMPLEMENTED) and \
                        implicit_reference(clause):
                    raise NotImplementedError("Unimplemented clause "
                                              + clause.__class__.__name__)

    def register_clause_reads(self, omp_node):
        '''Instrument AST with a list of AST objects to register implicit
        reads made by OpenMP clauses on the omp node'''
        self.register_clauses(
            mode='clause read',
            omp_node=omp_node,
            clauses=(Reduction, FirstPrivate)
            )

    def register_clause_writes(self, omp_node):
        '''Instrument AST with a list of AST objects to register implicit
        writes made by OpenMP clauses on the omp node'''
        self.register_clauses(
            mode='clause write',
            omp_node=omp_node,
            clauses=(Reduction, LastPrivate),
            append=True
            )

    def visit_FileAST(self, node):
        '''visit_FileAST'''
        node = self.generic_visit(node)
        return self.registry.embed_definitions(node)

    def visit_FuncDef(self, node): #pylint: disable=invalid-name
        '''Skip tool inserted functions'''
        if is_yeti(node):
            return node
        return self.generic_visit(node)

    def visit_OmpParallel(self, node): #pylint: disable=invalid-name
        '''visit_OmpParallel'''
        node = self.generic_visit(node)
        task_ids = self.registry.make_task_ids()
        post = self.registry.register_post()
        node.block.block_items.insert(0, post)
        node.block.block_items[0:0] = task_ids
        self.append_to_scope(self.registry.register_await())
        return node

    def visit_OmpFor(self, node): #pylint: disable=invalid-name
        '''visit_OmpFor'''
        iter_var = get_iter_var(node.loops, [])
        # We don't register the initial read of the iteration variable
        # because it is made private and we do not have access to the
        # private address in this scope
        # We don't register the reads and writes of the loop header
        # variables at the end of the loop body because they are
        # loop invariant expressions and pre-calculated by OpenMP
        self.register_clause_reads(node)
        node.loops.init.rvalue = self.visit(node.loops.init.rvalue)
        cond_right = node.loops.cond.right
        cond_left = node.loops.cond.left
        if isinstance(cond_left, ID) and cond_left.name != iter_var:
            self.register_node_accesses("read", node.loops.cond.left)
        elif isinstance(cond_right, ID):
            self.register_node_accesses("read", node.loops.cond.right)
        node.loops.stmt = self.visit(node.loops.stmt)
        self.register_clause_writes(node)
        if not has_clause(node, NoWait):
            self.append_to_scope(self.registry.register_await())
        return node

    def visit_OmpSections(self, node): #pylint: disable=invalid-name
        '''visit_OmpSections'''
        #node = self.generic_visit(node)
        #if not has_clause(node, NoWait):
        #    self.append_to_scope(self.registry.register_await())
        #return node
        raise NotImplementedError

    def visit_OmpSection(self, node): #pylint: disable=invalid-name
        '''visit_OmpSection'''
        raise NotImplementedError

    def visit_OmpSingle(self, node): #pylint: disable=invalid-name
        '''visit_OmpSingle'''
        #node = self.generic_visit(node)
        #if not has_clause(node, NoWait):
        #    self.append_to_scope(self.registry.register_await())
        #return node
        raise NotImplementedError

    def visit_OmpTask(self, node): #pylint: disable=invalid-name
        '''visit_OmpTask'''
        #node = self.generic_visit(node)
        #node.block.block_items = [
        #    *self.registry.make_task_ids(),
        #    self.registry.register_post(),
        #    *node.block.block_items
        #    ]
        #return node
        raise NotImplementedError

    def visit_OmpCritical(self, node): #pylint: disable=invalid-name
        '''visit_OmpCritical'''
        #node = self.generic_visit(node)
        #node.block.block_items = [
        #    *self.registry.make_task_ids(),
        #    self.registry.register_isolated(),
        #    *node.block.block_items
        #    ]
        #return node
        raise NotImplementedError

    def visit_OmpMaster(self, node): #pylint: disable=invalid-name
        '''visit_OmpMaster'''
        raise NotImplementedError

    def visit_OmpBarrier(self, node): #pylint: disable=invalid-name
        '''visit_OmpBarrier'''
        raise NotImplementedError

    def visit_OmpSimd(self, node): #pylint: disable=invalid-name
        '''visit_OmpSimd'''
        raise NotImplementedError

    def visit_OmpFlush(self, node): #pylint: disable=invalid-name
        '''visit_OmpFlush'''
        raise NotImplementedError('Instrumenter: OmpFlush')

    def visit_OmpTaskloop(self, node): #pylint: disable=invalid-name
        '''visit_OmpTaskloop'''
        raise NotImplementedError('Instrumenter: OmpTaskloop')

    def visit_OmpTaskwait(self, node): #pylint: disable=invalid-name
        '''visit_OmpTaskwait'''
        raise NotImplementedError('Instrumenter: OmpTaskwait')

    def visit_OmpTaskgroup(self, node): #pylint: disable=invalid-name
        '''visit_OmpTaskgroup'''
        raise NotImplementedError('Instrumenter: OmpTaskgroup')

    def visit_OmpAtomic(self, node): #pylint: disable=invalid-name
        '''visit_OmpAtomic'''
        raise NotImplementedError('Instrumenter: OmpAtomic')

    def visit_OmpCancel(self, node): #pylint: disable=invalid-name
        '''visit_OmpCancel'''
        raise NotImplementedError('Instrumenter: OmpCancel')

    def visit_OmpCancellationPoint(self, node): #pylint: disable=invalid-name
        '''visit_OmpCancellationPoint'''
        raise NotImplementedError('Instrumenter: OmpCancellationPoint')

    def visit_OmpThreadprivate(self, node): #pylint: disable=invalid-name
        '''visit_OmpThreadprivate'''
        raise NotImplementedError('Instrumenter: ' + node.pragma)
