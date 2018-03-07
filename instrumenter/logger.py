"""AST function definitions for logging inserted when instrumenting"""

from os import path
import pycparser

LOGGER_C_FILE = 'logger.c'

class Logger():
    """Class to provide AST function definitions for logging to be inserted when instrumenting"""

    def __init__(self):
        ast = pycparser.parse_file(path.dirname(__file__) + '/' + LOGGER_C_FILE)
        self.log_heap_def = ast.ext[0]
        self.log_omp_def = ast.ext[1]

    def log_heap_access(self, mode, var):
        """Insert a function call AST for yeti_log_heap_access"""
        return pycparser.c_ast.FuncCall(
            pycparser.c_ast.ID(self.log_heap_def.decl.name),
            pycparser.c_ast.ExprList([
                pycparser.c_ast.Constant('string', '"' + mode + '"'),
                pycparser.c_ast.ID(var),
                pycparser.c_ast.FuncCall(
                    pycparser.c_ast.ID('omp_get_thread_num'),
                    None
                ),
                pycparser.c_ast.Constant('string', '"' + var + '"'),
            ])
        )

    def log_omp(self, action, construct):
        """Insert a function call AST for yeti_log_omp"""
        return pycparser.c_ast.FuncCall(
            pycparser.c_ast.ID(self.log_omp_def.decl.name),
            pycparser.c_ast.ExprList([
                pycparser.c_ast.Constant('string', '"' + action + '"'),
                pycparser.c_ast.Constant('string', '"' + construct + '"'),
            ])
        )

    def log_read(self, var):
        """Insert a function call AST to log a read heap access"""
        return self.log_heap_access('read', var)

    def log_write(self, var):
        """Insert a function call AST to log a write heap access"""
        return self.log_heap_access('write', var)

    def log_omp_enter(self, construct):
        """Insert a function call AST for entering an omp construct"""
        return self.log_omp('enter', construct)

    def log_omp_exit(self, construct):
        """Insert a function call AST for exiting an omp construct"""
        return self.log_omp('exit', construct)
