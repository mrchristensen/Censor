"""The information flow analysis, packaged in the InfoFlow class."""

import functools

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

    def calc_ipds(self, ex): #pylint: disable=too-many-locals,too-many-statements
        #pylint: disable=invalid-name
        """Calculate the immediate postdominator of each node in the graph."""
        def dfs(v):
            vertex.append(v)
            semi[v] = len(vertex)
            v.index = len(vertex)
            for w in succ[v]:
                if semi[w] == 0:
                    parent[w] = v
                    dfs(w)
        def compress(v):
            if ancestor[u] in ancestor:
                compress(ancestor[u])
                if semi[label[ancestor[v]]] < semi[label[v]]:
                    label[v] = label[ancestor[v]]
                ancestor[v] = ancestor[ancestor[v]]
        def ev(v):
            if ancestor[v] == 0:
                return label[v]
            else:
                compress(v)
                if semi[label[ancestor[v]]] >= semi[label[v]]:
                    return label[v]
                else:
                    return label[ancestor[v]]
        def link(v, w):
            s = w
            while semi[label[w]] < semi[label[child[s]]]:
                if size[s] + size[child[child[s]]] >= 2*size[child[s]]:
                    ancestor[child[s]] = s
                    child[s] = child[child[s]]
                else:
                    size[child[s]] = size[s]
                    ancestor[s] = child[s]
                    s = child[s]
                label[s] = label[w]
                size[v] = size[v] + size[w]
                if size[v] < 2*size[w]:
                    temp = s
                    s = child[v]
                    child[v] = temp
                while s != 0:
                    ancestor[s] = v
                    s = child[s]
        pred = self # TODO just an alias
        succ = self.reverse()
        semi = {}
        parent = {}
        vertex = [None]
        dom = {}
        dfs(ex)
        label = [i for i in range(len(vertex))]
        print(vertex)
        ancestor = [0] * len(vertex)
        child = [0] * len(vertex)
        size = [1] * len(vertex)
        size[0] = 0
        bucket = [set()] * len(vertex)
        for w in vertex[:1:-1]:
            print("w: %s" % w)
            for v in pred[w]:
                u = ev(v)
                semi[w] = min(semi[w], semi[u])
            print("semi[w]: %s" % semi[w])
            bucket[semi[w]] = w
            link(parent[w], w)
            if parent[w] in bucket:
                print("bucket: %s" % bucket[parent[w]])
            else:
                print("empty bucket")
            for v in bucket[parent[w]]:
                u = ev(v)
                if semi[u] < semi[v]:
                    dom[v] = u
                else:
                    dom[v] = parent[w]
            print("parent[w]: %s" % parent[w])
            if parent[w] in bucket:
                bucket.pop(parent[w])
        for w in vertex[2:]:
            print("dom: %s" % dom)
            print("vertex: %s" % vertex)
            print("semi: %s" % semi)
            if dom[w] != vertex[semi[w]]:
                dom[w] = dom[dom[w]]
        dom[ex] = 0
        print("pred: %s" % pred)
        print("succ: %s" % succ)
        print("semi: %s" % semi)
        print("parent: %s" % parent)
        print("vertex: %s" % vertex)
        return dom

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
        self._make_epg(graph)
        self._serialize(start, graph)
        self.epg = None
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

    def ipd(self, e_p):
        """Compute the immediate postdominator of e_p, if necessary, and return
           it."""
        # TODO

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
                        if succ != self.ipd(branch):
                            cts[succ] = taints
        # TODO go through sinks and report flows from sources

    def flows(self):
        """Run the analysis if necessary and return the information flows."""
        if not self.flows:
            self._run()
        return self.flows

class Node:
    """A simple Node class for a test."""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "n(%s)" % self.value
    def __repr__(self):
        return "n(%s)" % self.value

def test_ipds():
    """Run a quick test case to see if IPDs are found correctly."""
    cfg = WeakMap()
    nodes = [Node(i) for i in range(7)]
    cfg[nodes[1]] = nodes[2]
    cfg[nodes[1]] = nodes[3]
    cfg[nodes[2]] = nodes[6]
    cfg[nodes[3]] = nodes[4]
    cfg[nodes[3]] = nodes[5]
    cfg[nodes[4]] = nodes[6]
    cfg[nodes[5]] = nodes[6]
    cfg[nodes[5]] = nodes[3]
    pds = cfg.calc_ipds(6)
    print(pds)

if __name__ == "__main__":
    test_ipds()
