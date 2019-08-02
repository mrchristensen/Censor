"""An implementation of Tarjan's algorithm. This code is intended to be
incorporated into master."""
#pylint: disable=invalid-name

def doms(succ, r, n):
    #pylint: disable=too-many-locals
    #pylint: disable=too-many-statements
    """Calculate the dominators in the graph defined by succ. r is the entry
       node (the root of the tree) and n is the number of nodes in the graph."""
    def dfs(v):
        nonlocal n
        n = n+1
        semi[v] = n
        vertex[n] = v
        for w in succ[v]:
            if semi[w] == 0:
                parent[w] = v
                dfs(w)
            pred[w].add(v)

    def compress(v):
        if ancestor[ancestor[v]] != 0:
            compress(ancestor[v])
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
                s = child[s]
                ancestor[s] = child[s]
        label[s] = label[w]
        size[v] = size[v] + size[w]
        if size[v] < 2*size[w]:
            temp = s
            s = child[v]
            child[v] = temp
        while s != 0:
            ancestor[s] = v
            s = child[s]

    dom = [None] * (n + 1)
    parent = [None] * (n + 1)
    ancestor = [0] * (n + 1)
    child = [0] * (n + 1)
    vertex = [None] * (n + 1)
    pred = [set() for i in range(n+1)]
    bucket = [set() for i in range(n+1)]
    label = [i for i in range(n+1)]
    semi = [0] * (n + 1)
    size = [1] * (n + 1)

    n = 0
    dfs(r)
    size[0] = 0
    label[0] = 0
    semi[0] = 0
    i = n

    while i >= 2:
        w = vertex[i]
        for v in pred[w]:
            u = ev(v)
            if semi[u] < semi[w]:
                semi[w] = semi[u]
        bucket[vertex[semi[w]]].add(w)
        link(parent[w], w)

        for v in bucket[parent[w]]:
            u = ev(v)
            if semi[u] < semi[v]:
                dom[v] = u
            else:
                dom[v] = parent[w]
        bucket[parent[w]].clear()
        i = i-1

    for i in range(2, n+1):
        w = vertex[i]
        if dom[w] != vertex[semi[w]]:
            dom[w] = dom[dom[w]]
    dom[r] = 0

    return dom

def to_char(i):
    """Make a human-readable version of the node number - for debugging the
       example in the Lengauer and Tarjan paper."""
    if i is None:
        return 'None'
    if i == 0:
        return 'z'
    if i == 13:
        return 'r'
    return chr(96 + i)

def to_dict(m):
    """Also for debugging. This takes a list and prints it as a map from
       indices to values."""
    def rhs(i):
        if m[i] is None:
            return 'None'
        elif isinstance(m[i], int):
            return to_char(m[i])
        elif m[i]:
            return sorted(list(map(to_char, m[i])))
        else:
            return '[]'
    return {i: rhs(i) for i in range(len(m))}

succs = [None, set([4]), set([1, 4, 5]), set([6, 7]), set([12]), set([8]),
         set([9]), set([9, 10]), set([5, 11]), set([11]), set([9]),
         set([9, 13]), set([8]), set([1, 2, 3])]
ds = doms(succs, 13, 13)
print(to_dict(ds))
expected = [None, 13, 13, 13, 13, 13, 3, 3, 13, 13, 7, 13, 4, 0]
for (ex, act) in zip(expected, ds):
    if ex != act:
        print("expected %d but got %d" % (ex, act))
