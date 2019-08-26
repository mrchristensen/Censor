"""An implementation of Tarjan's algorithm. This code is intended to be
incorporated into master."""
#pylint: disable=invalid-name

def doms(succ, r):
    #pylint: disable=too-many-locals
    #pylint: disable=too-many-statements
    """Calculate the dominators in the graph defined by succ. r is the entry
       node (the root of the tree). succ should have a mapping for every node
       in the graph."""
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

    n = len(succ.keys())
    dom = {i: None for i in succ.keys()}
    parent = {i: None for i in succ.keys()}
    ancestor = {i: 0 for i in succ.keys()}
    child = {i: 0 for i in succ.keys()}
    vertex = [None] * (n + 1)
    pred = {i: set() for i in succ.keys()}
    bucket = {i: set() for i in succ.keys()}
    label = {i: i for i in succ.keys()}
    semi = {i: 0 for i in succ.keys()}
    size = {i: 1 for i in succ.keys()}

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
