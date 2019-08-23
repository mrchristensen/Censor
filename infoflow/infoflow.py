"""The information flow analysis, packaged in the InfoFlow class."""

import functools
from infoflow.doms import doms

class WeakMap(dict):
    """A specialized dictionary that keeps track of when it is modified."""
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.modified = True

    def reset(self):
        """Reset the modified bit on the weak map."""
        self.modified = False

    def __getitem__(self, key):
        if dict.__contains__(self, key):
            return dict.__getitem__(self, key)
        else:
            return frozenset()

    def __setitem__(self, key, val):
        """Perform a weak update. Also, set modified if anything changes."""
        if isinstance(val, frozenset) and not val:
            self.add_all(key, val)
        else:
            self.add_all(key, frozenset([val]))

    def add_all(self, key, values):
        """Perform a weak update with multiple values."""
        if self.__contains__(key):
            existing = self.__getitem__(key)
        else:
            existing = frozenset()
        if self.modified or not values.subsetof(existing):
            self.modified = True
            dict.__setitem__(self, key, existing | values)

    def reverse(self):
        """Create a new WeakMap with reversed bindings."""
        _reverse = WeakMap()
        for (key, values) in self.items():
            for value in values:
                _reverse[value] = key
        return _reverse

    def _binding_to_str(self, key):
        values = map(lambda v: str(v), self[key])
        v_str = ", ".join(values)
        return "%s: %s" % (key, v_str)

    def __str__(self):
        return "\n".join(map(self._binding_to_str, self.keys()))

    def __repr__(self):
        return "\n".join(map(self._binding_to_str, self.keys()))

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

    def __init__(self, graph, writes, start):
        self.writes = writes
        self.epg = None
        self._make_epg(graph)
        self._serialize(start, graph)
        self.eps = {}
        self.shs = {}
        self._flows = None

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

    def _make_epg(self, graph):
        """Create an execution point graph from an abstract state graph.
           Intended for internal use."""
        if not self.epg:
            self.epg = WeakMap()
            for (state, s_enum) in graph.items():
                kep = state.get_e_p()
                succs = s_enum.successors
                succ_eps = map(lambda state: state.get_e_p(), succs)
                self.epg[kep] = succ_eps
            r_epg = self.epg.reverse()
            exit_node = None
            self.doms = doms(r_epg, exit_node)

    def _serialize(self, start, graph):
        """Order the states in the graph and return them as a list. Currently a
           depth-first search. Intended for internal use."""
        seen = set()
        order = []
        def inner_serialize(node):
            if node not in seen:
                seen.add(node)
                order.append(node)
                for succ in graph[node].successors:
                    inner_serialize(succ)
        inner_serialize(start)
        self.state_list = order

    def origins(self, state, t_s):
        """Record any new taints at state in t_s."""
        # TODO

    def _run(self):
        """Perform an information flow analysis. Intended for internal use."""
        self._flows = WeakMap()
        cts = WeakMap()
        t_s = WeakMap()
        def taints(addr):
            if addr in t_s:
                return t_s[addr]
            else:
                return frozenset()
        def all_taints(addrs):
            _taints = map(taints, addrs)
            return functools.reduce(lambda a, b: a|b, _taints, frozenset())
        while t_s.modified or cts.modified:
            cts.reset()
            t_s.reset()
            for state in self.state_list:
                e_p = state.get_e_p()
                # TODO cts needs to map to maps, not sets - so we have to
                # extract and flatten
                from_context = cts[e_p]
                self.origins(state, t_s)
                writes = self.writes.writes_at(state.ctrl)
                for (dest, sources) in writes:
                    t_s[dest] = all_taints(sources) | from_context
                current_cts = WeakMap(cts[e_p]) # TODO this argument won't work
                current_cts[e_p] = all_taints(state.get_branches())
                for succ in self.epg[state]:
                    for (branch, taints) in current_cts:
                        if succ != self.doms[branch]:
                            cts[succ] = taints
        # TODO go through sinks and report flows from sources

    def flows(self):
        """Run the analysis if necessary and return the information flows."""
        if not self.flows:
            self._run()
        return self.flows
