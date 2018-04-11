"""Instrumenting Strategy"""

class InstrumentingStrategy():
    """Abstract class for instrumenting an AST"""

    def embed_definitions(self, file_ast):
        """Return AST with the declarations and definitions needed"""
        raise NotImplementedError

    def register_heap_access(self, mode, var):
        """Register heap access"""
        raise NotImplementedError

    def register_omp(self, mode, construct):
        """Register entering and exiting an omp construct"""
        raise NotImplementedError

    def register_read(self, var):
        """Insert a function call AST to register a read heap access"""
        return self.register_heap_access('read', var)

    def register_write(self, var):
        """Insert a function call AST to register a write heap access"""
        return self.register_heap_access('write', var)

    def register_omp_enter(self, construct):
        """Insert a function call AST for entering an omp construct"""
        return self.register_omp('enter', construct)

    def register_omp_exit(self, construct):
        """Insert a function call AST for exiting an omp construct"""
        return self.register_omp('exit', construct)
