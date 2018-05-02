"""AST function definitions for logging inserted when instrumenting"""

from os import path
from pycparser.c_ast import * # pylint: disable=wildcard-import, unused-wildcard-import
from pycparser import parse_file
from instrumenter.registry import Registry
from instrumenter.helpers import IncludeDependencies, find_end_include
from transforms.node_transformer import NodeTransformer
from utils import is_main

LOGGER_C_FILE = 'logger.c'
YETI_LOG_MEMORY_ACCESS = 'yeti_log_memory_access'
YETI_LOG_POST = 'yeti_log_post'
YETI_LOG_AWAIT = 'yeti_log_await'
YETI_LOG_EWAIT = 'yeti_log_ewait'
YETI_MAKE_TASK_ID = 'yeti_make_task_id'
YETI_PARENT_TASK = 'yeti_parent_task_id'
YETI_TASK = 'yeti_task_id'
YETI_LOG_ISOLATED = 'yeti_log_isolated'
YETI_TASK_ID_GEN = Decl(
    'yeti_task_id_generator',
    [], [], [],
    TypeDecl(
        'yeti_task_id_generator',
        [],
        IdentifierType(['int'])
        ),
    Constant('int', '-1'),
    None
    )

def make_task_param(identifier):
    """Return task id parameter"""
    return Decl(
        identifier,
        [], [], [],
        PtrDecl(
            [],
            TypeDecl(
                identifier,
                [],
                IdentifierType(['char'])
                )
            ),
        None,
        None
        )

YETI_FUNCS = [
    YETI_LOG_MEMORY_ACCESS,
    YETI_LOG_POST,
    YETI_LOG_AWAIT,
    YETI_LOG_EWAIT,
    YETI_MAKE_TASK_ID,
    YETI_LOG_ISOLATED
    ]

def is_yeti(node):
    """Return true if AST is a FuncCall or FuncDef of this tool"""
    return any(f == node.decl.name for f in YETI_FUNCS) \
            or 'INIT_GLOBALS' in node.decl.name

class PropogateTaskIds(NodeTransformer):
    """
    Modify every function call and function definition to pass
    the current task id and parent task id
    """

    def __init__(self):
        self.user_funcs = []

    def visit_FuncDef(self, node): # pylint: disable=invalid-name
        """Make first two parameters task id and parent id"""
        node = self.generic_visit(node)
        if is_main(node) or is_yeti(node):
            return node
        self.user_funcs.append(node.decl.name)
        task_id = make_task_param(YETI_TASK)
        parent_task_id = make_task_param(YETI_PARENT_TASK)
        params = [task_id, parent_task_id]
        if node.decl.type.args is None:
            node.decl.type.args = ParamList(params)
        else:
            node.decl.type.args.params[0:0] = params

        return node

    def visit_FuncCall(self, node): # pylint: disable=invalid-name
        """Make first two arguments task id and parent id"""
        node = self.generic_visit(node)
        if node.name.name not in self.user_funcs:
            return node
        args = [ID(YETI_TASK), ID(YETI_PARENT_TASK)]
        if node.args is None:
            node.args = ExprList(args)
        else:
            node.args.exprs[0:0] = args
        return node


class Logger(Registry):
    """Class to provide AST function definitions for logging to be inserted
    when instrumenting"""

    def __init__(self):
        self.ast = parse_file(path.dirname(__file__) + '/' + LOGGER_C_FILE)

    def embed_definitions(self, file_ast):
        """Return AST with the declarations and definitions needed"""
        for item in file_ast.ext:
            if is_main(item):
                task_ids = self.make_task_ids()
                task_ids.reverse()
                item.body.block_items[0:0] = task_ids
        deps = ['omp.h', 'stdio.h', 'stdlib.h']
        file_ast = IncludeDependencies(deps).visit(file_ast)
        file_ast = PropogateTaskIds().visit(file_ast)
        io_index = find_end_include(file_ast, 'stdio')
        file_ast.ext[io_index+1:io_index+1] = self.ast.ext
        file_ast.ext.insert(0, YETI_TASK_ID_GEN)
        return file_ast

    def register_memory_access(self, mode, var):
        """Return code to register memory access"""
        return FuncCall(
            ID(YETI_LOG_MEMORY_ACCESS),
            ExprList([
                Constant('string', '"' + mode + '"'),
                var,
                ID(YETI_TASK)
            ])
        )

    def register_post(self):
        """Return code to register post of task"""
        return FuncCall(
            ID(YETI_LOG_POST),
            ExprList([
                ID(YETI_TASK),
                ID(YETI_PARENT_TASK),
            ])
        )

    def register_isolated(self):
        """Return code to register isolated region"""
        return FuncCall(
            ID(YETI_LOG_ISOLATED),
            ExprList([
                ID(YETI_TASK),
                ID(YETI_PARENT_TASK),
            ])
        )

    def register_await(self):
        """Return code to register await"""
        return FuncCall(ID(YETI_LOG_AWAIT), None)

    def register_ewait(self):
        """Return code to register ewait"""
        return FuncCall(ID(YETI_LOG_EWAIT), None)

    def make_task_id(self): # pylint: disable=no-self-use
        """Return code to generate new task id"""
        return Decl(
            YETI_TASK,
            [], [], [],
            PtrDecl(
                [],
                TypeDecl(
                    YETI_TASK,
                    [],
                    IdentifierType(['char'])
                    )
                ),
            FuncCall(ID(YETI_MAKE_TASK_ID), None),
            None
            )

    def make_task_ids(self): # pylint: disable=no-self-use
        """Return code to generate new task ids"""
        return [
            Decl(
                YETI_PARENT_TASK,
                [], [], [],
                PtrDecl(
                    [],
                    TypeDecl(
                        YETI_PARENT_TASK,
                        [],
                        IdentifierType(['char'])
                        )
                    ),
                ID(YETI_TASK),
                None
                ),
            self.make_task_id()
            ]
