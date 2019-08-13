'''Registry'''

class Registry():
    '''Abstract class for registering events in an AST'''

    def embed_definitions(self, file_ast):
        '''Return AST with the declarations and definitions needed'''
        raise NotImplementedError

    def register_memory_access(self, mode, var):
        '''Return code to register memory access'''
        raise NotImplementedError

    def register_post(self):
        '''Return code to register post of task'''
        raise NotImplementedError

    def register_isolated(self):
        '''Return code to register isolated region'''
        raise NotImplementedError

    def register_await(self):
        '''Return code to register await'''
        raise NotImplementedError

    def register_ewait(self):
        '''Return code to register ewait'''
        raise NotImplementedError

    def make_task_ids(self):
        '''Return code to generate new task ids'''
        raise NotImplementedError
