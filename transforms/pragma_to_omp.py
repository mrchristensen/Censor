"""Base class for Pragma to OMP Node transforms"""

from .node_transformer import NodeTransformer

class PragmaToOmp(NodeTransformer):
    """ Base class for Pragma to OMP Node transforms, defining commonly used.
    """

    def __init__(self):
        self.pattern = None
        self.str_to_clause_type = {}

    def parse_clauses(self, clause_strs):
        """ Parse pragma strings to generate Omp Clause Nodes.
        """
        clause_nodes = []
        for clause in clause_strs:
            parts = self.parse_clause(clause)
            if parts[0] in self.str_to_clause_type.keys():
                clause_nodes.append(
                    self.str_to_clause_type[parts[0]](*parts[1:])
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

    def pragma_matches(self, pragma_string):
        """ Test that a pragma string matches this node types pattern.
        """
        if not self.pattern:
            raise ValueError("self.pattern must be set by child class")
        return self.pattern.match(pragma_string) != None

    def clause_nodes_from_pragma_string(self, pragma_string):
        """ Generate OmpClause nodes from a pragma string.
        """
        clause_strs = pragma_string.split()[2:]
        clauses = self.parse_clauses(clause_strs)
        return clauses
