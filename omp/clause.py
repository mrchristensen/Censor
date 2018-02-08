""" OMP Clauses """
#pylint: disable=too-few-public-methods,invalid-name
class Private():
    """ Private
        list of identifiers

        Syntax: private(a, b, c, ...)
    """

    def __init__(self, *ids):
        self.ids = ids

    def __iter__(self):
        if self.ids is not None:
            yield self.ids

class FirstPrivate():
    """ FirstPrivate
        list of identifiers

        Syntax: private(a, b, c, ...)
    """

    def __init__(self, *ids):
        self.ids = ids

    def __iter__(self):
        if self.ids is not None:
            yield self.ids

class LastPrivate():
    """ LastPrivate
        list of identifiers

        Syntax: private(a, b, c, ...)
    """

    def __init__(self, *ids):
        self.ids = ids

    def __iter__(self):
        if self.ids is not None:
            yield self.ids

class Reduction():
    """ Reduction
        operator
        list of identifiers

        Syntax: reduction(+: a, b, c, ...)
    """

    def __init__(self, op, *ids):
        self.op = op
        self.ids = ids

    def __iter__(self):
        if self.ids is not None:
            yield self.ids

class Schedule():
    """ Schedule
        kind
        chunk size

        Syntax: schedule(kind, chunk_size)
    """

    def __init__(self, kind, chunk):
        self.kind = kind
        self.chunk = chunk

class Collapse():
    """ Collapse
        n
        Syntax: collapse(1)
    """

    def __init__(self, n):
        self.n = n

class Ordered():
    """ Ordered
        No parameters

        Syntax: ordered
    """
    def __init__(self):
        pass

class NoWait():
    """ NoWait
        No Parameters

        Syntax: nowait
    """
    def __init__(self):
        pass
