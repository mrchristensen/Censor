""" OMP Clauses """
#pylint: disable=too-few-public-methods,invalid-name
class Private():
    """ Private
        list of identifiers

        Syntax: private(a, b, c, ...)
    """

    def __init__(self, *ids):
        self.ids = list(ids)

    def __iter__(self):
        if self.ids is not None:
            yield self.ids

class FirstPrivate():
    """ FirstPrivate
        list of identifiers

        Syntax: firstprivate(a, b, c, ...)
    """

    def __init__(self, *ids):
        self.ids = list(ids)

    def __iter__(self):
        if self.ids is not None:
            yield self.ids

class LastPrivate():
    """ LastPrivate
        list of identifiers

        Syntax: lastprivate(a, b, c, ...)
    """

    def __init__(self, *ids):
        self.ids = list(ids)

    def __iter__(self):
        if self.ids is not None:
            yield self.ids

class CopyPrivate():
    """ CopyPrivate
        list of identifiers

        Syntax: copyprivate(a, b, c, ...)
    """

    def __init__(self, *ids):
        self.ids = list(ids)

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
        self.ids = list(ids)

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

class Critical():
    """ Critical
        string-expression

        Syntax: critical(name)
    """
    def __init__(self, name=None):
        self.name = name

class Hint():
    """ Hint
        integer-expression

        Syntax: hint(integer)
    """
    def __init__(self, hint):
        self.hint = hint

class If():
    """ If
        scalar-expression

        Syntax: if(scalar)
    """
    def __init__(self, scalar):
        self.scalar = scalar

class NumThreads():
    """ NumThreads
        integer-expression

        Syntax: num_threads(integer)
    """
    def __init__(self, num):
        self.num = num

class Default():
    """ Default
        shared|none

        Syntax: default(shared|none)
    """
    def __init__(self, state):
        self.state = state

class Shared():
    """ Shared
        list of identifiers

        Syntax: shared(a, b, c, ...)
    """
    def __init__(self, *ids):
        self.ids = list(ids)

class CopyIn():
    """ CopyIn
        list of identifiers

        Syntax: copyin(a, b, c, ...)
    """
    def __init__(self, *ids):
        self.ids = list(ids)

class Final():
    """ Final
        scalar-expression

        Syntax: final(scalar)
    """
    def __init__(self, scalar):
        self.scalar = scalar

class Untied():
    """ Untied
        No Parameters

        Syntax: untied
    """
    def __init__(self):
        pass

class Mergeable():
    """ Mergeable
        No Parameters

        Syntax: mergeable
    """
    def __init__(self):
        pass

class Depend():
    """ Depend
        dependency-type: list

        Syntax: depend(dependency-type: list)
    """
    def __init__(self, typ, *lst):
        self.typ = typ
        self.lst = list(lst)

class Priority():
    """ Priority
        priority-value

        Syntax: priority(priority-value)
    """
    def __init__(self, value):
        self.value = value

class Flush():
    """ Flush
        ids

        Syntax: flush(ids)
    """
    def __init__(self, *ids):
        self.ids = list(ids)
