"""Base class for Pragma to OMP Node transforms"""

import re
from pycparser.c_ast import Pragma
from .node_transformer import NodeTransformer
from .helpers import ensure_compound

class PragmaToOmp(NodeTransformer):
    """ Base class for Pragma to OMP Node transforms, defining commonly used.
    """

    def __init__(self, construct, pattern, str_to_clause_type,
                 structured_block=True):
        self.construct = construct
        self.has_clauses = len(str_to_clause_type) > 0
        self.pattern = pattern
        self.str_to_clause_type = str_to_clause_type
        self.structured_block = structured_block
        pattern = r'(\w+\((?:[\w+-\\*\\|\\^&]+:\s*)?\w+(?:,\s*\w+)*\)|\w+)'
        self.clause_pattern = re.compile(pattern)

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
        """ Parse individual clause into lists where first element is clause
        name and following are arguments.
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
        clause_strs = self.clause_pattern.findall(pragma_string)
        clauses = self.parse_clauses(clause_strs)
        return clauses

    def visit_Compound(self, node): #pylint: disable=invalid-name
        """ Visit each compound node and check it's children for the Pragma
            nodes we want to change. Recursively alter, if found.
        """

        # Recur
        node = self.generic_visit(node)

        # No children so no pragmas to find
        if node.block_items is None:
            return node

        for index, child in enumerate(node.block_items):
            if isinstance(child, Pragma) and self.pragma_matches(child.string):
                if not self.structured_block:
                    # No block of code to subsume. Just check if we need to
                    # parse clauses
                    if self.has_clauses:
                        node.block_items[index] = self.construct(
                            child.string,
                            self.clause_nodes_from_pragma_string(child.string),
                            child.coord
                        )
                    else:
                        node.block_items[index] = self.construct(child.string,
                                                                 child.coord)
                elif index + 1 < len(node.block_items):
                    # Get structured block for this omp construct and check
                    # for clauses
                    next_sibling = node.block_items[index+1]
                    if 'omp for' not in child.string:
                        next_sibling = ensure_compound(next_sibling)
                    if self.has_clauses:
                        node.block_items[index] = self.construct(
                            child.string,
                            self.clause_nodes_from_pragma_string(child.string),
                            next_sibling,
                            child.coord
                            )
                    else:
                        node.block_items[index] = self.construct(
                            child.string,
                            next_sibling,
                            child.coord
                            )
                    node.block_items.pop(index+1)
        return node
