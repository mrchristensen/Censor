"""The information flow analysis, packaged in the InfoFlow class."""

class InfoFlow:
    """A class that performs information flow analysis. It requires a graph to
        create the EPG and branching map. It also requires the writes map."""

    none = lambda state: frozenset()
    if_branches = lambda state: state.get_addresses(state.ctrl.stmt.cond)
    id_addresses = lambda state: \
        frozenset([state.get_address(state.ctrl.stmt)[0]])
    expr_addresses = lambda state: state.get_address(state.ctrl.stmt.expr)
    binop_addresses = lambda state: (state.get_address(state.ctrl.stmt.left) |
                                     state.get_address(state.ctrl.stmt.right))
    assign_addresses = lambda state: state.get_address(state.ctrl.stmt.rvalue)

    branch_funs = {
        'Label' : none,
        'If' : if_branches,
        'ID' : none,
        'Goto' : none,
        'FuncCall' : none,
        'EmptyStatement' : none,
        'Decl' : none,
        'Constant' : none,
        'Compound' : none,
        'Cast' : none,
        'BinaryOp' : none,
        'Assignment' : none,
        'UnaryOp' : none,
        'Return' : none,
    }

    address_funs = {
        'Label' : none,
        'If' : if_branches,
        'ID' : id_addresses,
        'Goto' : none,
        'FuncCall' : none,
        'EmptyStatement' : none,
        'Decl' : none,
        'Constant' : none,
        'Compound' : none,
        'Cast' : expr_addresses,
        'BinaryOp' : binop_addresses,
        'Assignment' : assign_addresses,
        'UnaryOp' : expr_addresses,
        'Return' : expr_addresses,
    }

    def __init__(self, graph, writes):
        self.writes = writes
        self.epg = self.make_epg(graph)
        self.branches = {}
        self.get_branches(graph)
        self.eps = {}
        self.shs = {}

    def stack_height(self, kont_addr, stor, seen=frozenset()):
        """Get the stack height of an abstract state."""
        key = (kont_addr, stor)
        if key in self.shs:
            return self.shs[key]
        if kont_addr in seen:
            return None
        # TODO is this how to check for halt?
        if kont_addr == 0:
            result = 0
        else:
            height = None
            konts = stor.read_kont(kont_addr)
            for kont in konts:
                s_h = self.stack_height(kont.kont_addr, stor, seen + kont_addr)
                if s_h is None:
                    return None
                if height:
                    if s_h is height:
                        # the stack height matches what we've seen before
                        pass
                    else:
                        return None
                else:
                    height = s_h
            result = height + 1
        self.shs[key] = result
        return result

    def get_ep(self, state):
        """Get the execution point for a state."""
        if state in self.eps:
            return self.eps[state]
        result = (state.ctrl, self.stack_height(state.kont_addr, state.stor))
        self.eps[state] = result
        return result

    def make_epg(self, graph):
        """Create an execution point graph from an abstract state graph."""
        result = {}
        for (state, succs) in graph.items():
            kep = self.get_ep(state)
            succ_eps = map(self.get_ep, succs)
            if kep in result:
                result[kep] = result[kep] | succ_eps
            else:
                result[kep] = succ_eps
        return result

    def get_branch(self, state):
        """Create a binding from a branch to the addresses that affect it."""
        if state in self.branches:
            return self.branches[state]
        # TODO
        result = None
        self.branches[state] = result
        return result

    def get_branches(self, graph):
        """Create a branches map from an abstract state graph."""
        for (state, succs) in graph.items():
            self.get_branch(state)
            for succ in succs:
                self.get_branch(succ)

    def run(self):
        """Perform an information flow analysis."""
