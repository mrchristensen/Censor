""" Analysis tool for compiling a set of c_ast objects that we need to know how
    to handle to cover a file.
"""

from pycparser.c_ast import NodeVisitor

class Observer(NodeVisitor):
    """ Observer: takes note as c_ast objects go by...
        Stores seen node types in set.
    """
    def __init__(self):
        self.seen = set()
        self.counts = dict()

    def generic_visit(self, node):
        """ Recursively visit and record
        """
        name = node.__class__.__name__
        self.seen.add(name)
        if name not in self.counts:
            self.counts[name] = 1
        else:
            self.counts[name] += 1

        if hasattr(node, '__iter__'):
            for child in node:
                self.visit(child)

    def report(self):
        """ Report findings.
        """
        print('Observed AST objects')
        print('--------------------')
        print('{:<15}'.format('Observed') + '{:>5}'.format('Count'))
        print('--------------------')
        for elem in self.seen:
            print('{:<15}'.format(elem) + '{:>5}'.format(self.counts[elem]))

    def coverage(self, implemented_set):
        """ Using a set of implemented objects returned from cesk,
            calculate a coverage report.

            This function must be called after processing the ast.
        """
        diff_set = self.seen.difference(implemented_set)
        print('\n--------------------')
        print('{:^20}'.format('Coverage Report'))
        print('--------------------')
        if not diff_set:
            print('100% Coverage')
            return

        total = sum(self.counts.values())
        covered = total
        for elem in diff_set:
            if elem not in self.counts:
                pass
            else:
                covered -= self.counts[elem]

        print('  {: 4.1f}% Coverage'.format((covered/total) * 100))
        print('--------------------\n')
        print('--------------------')
        print('{:^20}'.format('Uncovered Objects'))
        print('--------------------')
        for elem in diff_set:
            print('{:<15}'.format(elem) + '{:>5}'.format(self.counts[elem]))
