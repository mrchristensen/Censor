
def doms(succ, r, n):
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
    print("parent: %s" % str(parent))
    print("pred:   %s" % str(pred))
    print("vertex: %s" % str(vertex))
    print("semi: %s" % to_dict(list(map(lambda i: vertex[i], semi))))

    while i >= 2:
        print("i: %i" % i)
        w = vertex[i]
        print("w: %s" % to_char(w))
        # The problem seems to be in here. Semidominators aren't being computed
        # correctly. The only other lines of code that affect semi are obvious.
        # It could be an error in ev() or something downstream from it.
        for v in pred[w]:
            u = ev(v)
            if semi[u] < semi[w]:
                semi[w] = semi[u]
        # this next line may be confusing; semi seems to record pre-order numbers, not vertex names
        print("semi[%s] = %s" % (to_char(w), to_char(vertex[semi[w]])))
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

    print("semi: %s" % to_dict(list(map(lambda i: vertex[i], semi))))
    for i in range(2, n+1):
        w = vertex[i]
        # print("finalizing vertex #%i: %s" % (i, to_char(w)))
        # print("doms: %s" % str(list(map(to_char, dom))))
        if dom[w] != vertex[semi[w]]:
            dom[w] = dom[dom[w]]
    dom[r] = 0

    return dom

def to_char(i):
    if i is None:
        return 'None'
    if i == 0:
        return 'z'
    if i == 13:
        return 'r'
    return chr(96 + i)

def to_dict(m):
    def binding(i):
        if m[i] is None:
            v = 'None'
        elif isinstance(m[i], int):
            v = to_char(m[i])
        elif m[i]:
            v = sorted(list(map(to_char, m[i])))
        else:
            v = '[]'
        return (to_char(i), v)
    return dict([binding(i) for i in range(len(m))])

succs = [None, set([4]), set([1, 4, 5]), set([6, 7]), set([12]), set([8]), set([9]), set([9, 10]), set([5, 11]), set([11]), set([9]), set([9, 13]), set([8]), set([1, 2, 3])]
# succs = [None, set([2]), set([3, 4]), set([1]), set()]
# print("succs: %s" % to_dict(succs))
ds = doms(succs, 13, 13)
# ds = doms(succs, 1, 4)
print(to_dict(ds))
expected = [None, 13, 13, 13, 13, 13, 3, 3, 13, 13, 7, 13, 4, 0]
for (ex, act) in zip(expected, ds):
    if ex != act:
        print("expected %d but got %d" % (ex, act))
print(ds)
