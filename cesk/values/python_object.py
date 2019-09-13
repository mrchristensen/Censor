'''Container of a Python Object, should only be accessed as a pointer'''
import cesk.limits as limits

class PythonObject:  #pylint:disable=too-few-public-methods
    '''contains a python object'''
    def __init__(self, python_object):
        self.size = limits.CONFIG.get_word_size()
        self.python_object = python_object
