"""AST function definitions for logging inserted when instrumenting"""

from os import path
import pycparser
from instrumenter.registry import Registry
from instrumenter.helpers import IncludeOMP, find_end_include

LOGGER_C_FILE = 'logger.c'

class Logger(Registry):
    """Class to provide AST function definitions for logging to be inserted
    when instrumenting"""

    def __init__(self):
        ast = pycparser.parse_file(path.dirname(__file__) + '/' + LOGGER_C_FILE)
        self.log_memory_def = ast.ext[0]
        self.log_omp_def = ast.ext[1]

    def embed_definitions(self, file_ast):
        """Return AST with the declarations and definitions needed"""
        file_ast = IncludeOMP().visit(file_ast)
        io_index = find_end_include(file_ast, 'stdio')
        file_ast.ext.insert(io_index+1, self.log_omp_def)
        file_ast.ext.insert(io_index+1, self.log_memory_def)
        return file_ast

    def register_memory_access(self, mode, var):
        """Insert a function call AST for yeti_log_memory_access"""
        return pycparser.c_ast.FuncCall(
            pycparser.c_ast.ID(self.log_memory_def.decl.name),
            pycparser.c_ast.ExprList([
                pycparser.c_ast.Constant('string', '"' + mode + '"'),
                var
            ])
        )

    def register_omp(self, mode, construct):
        """Insert a function call AST for yeti_log_omp"""
        return pycparser.c_ast.FuncCall(
            pycparser.c_ast.ID(self.log_omp_def.decl.name),
            pycparser.c_ast.ExprList([
                pycparser.c_ast.Constant('string', '"' + mode + '"'),
                pycparser.c_ast.Constant('string', '"' + construct + '"')
            ])
        )
