"""AST function definitions for logging inserted when instrumenting"""

from os import path
import pycparser
from utils import is_main
from .strategy import InstrumentingStrategy

LOGGER_C_FILE = 'logger.c'

class Logger(InstrumentingStrategy):
    """Class to provide AST function definitions for logging to be inserted
    when instrumenting"""

    def __init__(self):
        ast = pycparser.parse_file(path.dirname(__file__) + '/' + LOGGER_C_FILE)
        self.log_heap_def = ast.ext[0]
        self.log_omp_def = ast.ext[1]

    def embed_definitions(self, file_ast):
        """Return AST with the declarations and definitions needed"""
        for i, block in enumerate(file_ast.ext):
            if is_main(block):
                file_ast.ext.insert(i, self.log_omp_def)
                file_ast.ext.insert(i, self.log_heap_def)
                break
        return file_ast

    def register_heap_access(self, mode, var):
        """Insert a function call AST for yeti_log_heap_access"""
        return pycparser.c_ast.FuncCall(
            pycparser.c_ast.ID(self.log_heap_def.decl.name),
            pycparser.c_ast.ExprList([
                pycparser.c_ast.Constant('string', '"' + mode + '"'),
                var,
                pycparser.c_ast.FuncCall(
                    pycparser.c_ast.ID('omp_get_thread_num'),
                    None
                )
            ])
        )

    def register_omp(self, mode, construct):
        """Insert a function call AST for yeti_log_omp"""
        return pycparser.c_ast.FuncCall(
            pycparser.c_ast.ID(self.log_omp_def.decl.name),
            pycparser.c_ast.ExprList([
                pycparser.c_ast.Constant('string', '"' + mode + '"'),
                pycparser.c_ast.Constant('string', '"' + construct + '"'),
                pycparser.c_ast.FuncCall(
                    pycparser.c_ast.ID('omp_get_thread_num'),
                    None
                ),
            ])
        )
