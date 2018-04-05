"""OmpNotImplemented Transform"""

import re
from .node_transformer import NodeTransformer

OMP = re.compile(r'^omp\s.*')

class OmpNotImplemented(NodeTransformer):
    """
    Transform that throws an error when it sees 'pragma omp'
    This transform should be run after the other Omp transforms
    to catch ones in the benchmarks that we haven't handled
    """

    def visit_Pragma(self, node): # pylint: disable=invalid-name
        """Throw an error if it 'pragma omp' is in the string"""
        if OMP.match(node.string):
            raise NotImplementedError
        return self.generic_visit(node)
