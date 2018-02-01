"""Base class for Pragma to OMP Node transforms"""

import omp_ast
from .node_transformer import NodeTransformer

class PragmaToOmp(NodeTransformer):
    """ Base class for Pragma to OMP Node transforms, defining commonly used.
    """

    def __init__(self):
        self.clause_lookup = {
            "private":	    omp_ast.OmpClausePrivate,
            "firstprivate": omp_ast.OmpClauseFirstPrivate,
            "lastprivate":  omp_ast.OmpClauseLastPrivate,
            "reduction":    omp_ast.OmpClauseReduction,
            "schedule":     omp_ast.OmpClauseSchedule,
            "collapse":	    omp_ast.OmpClauseCollapse,
            "ordered":	    omp_ast.OmpClauseOrdered,
            "nowait":	    omp_ast.OmpClauseNoWait,
            }

    def parse_clauses(self, clause_strs):
        """ Parse pragma strings to generate Omp Clause Nodes.
        """

        clause_nodes = []
        for clause in clause_strs:
            parts = self.parse_clause(clause)
            if parts[0] in self.clause_lookup.keys():
                clause_nodes.append(
                    self.clause_lookup[parts[0]](None, *parts[1:])
                    )
        return clause_nodes

    @staticmethod
    def parse_clause(clause):
        """ Parse individual clause into lists where first element is clause name
            and following are arguments.
        """
        clause = "".join(clause.split()) # Removes whitespace
        delimiters = "():,"
        parts = []
        start = 0
        for index, char in enumerate(clause):
            if char in delimiters:
                part = clause[start:index]
                if part.isdecimal():
                    part = int(part)
                parts.append(part)
                start = index + 1 # Skip delimiter
        if not parts:
            parts = [clause]
        return parts
