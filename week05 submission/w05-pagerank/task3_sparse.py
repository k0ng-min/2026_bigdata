#!/usr/bin/env python3
"""Week 5 · Task 3 — PageRank on a graph that will not fit as a matrix.

Textbook §5.2 (efficient PageRank), §5.2.1 - §5.2.3.

`DenseMatrix` is PageRank written the way the equations are written: build the
transition matrix M, multiply. It is correct, it is easy to read, and it stores
n^2 numbers for a graph with almost no edges.

The web's matrix is about 99.9999% zeros. Storing them is the problem, and
§5.2 is the chapter about not doing that.

    python3 bench.py
    python3 bench.py --yours

Correctness first: the harness compares your ranks against the dense version
element by element. A fast PageRank that ranks pages differently is a different
algorithm, not a faster one.
"""


class DenseMatrix:
    """PageRank as written in the equations. Stores n^2 floats."""

    def __init__(self, beta=0.85, tol=1e-10, max_iter=100):
        self.beta, self.tol, self.max_iter = beta, tol, max_iter

    def run(self, graph):
        nodes = list(graph)
        n = len(nodes)
        index = {v: i for i, v in enumerate(nodes)}

        # the full transition matrix, zeros and all
        M = [[0.0] * n for _ in range(n)]
        for v, outs in graph.items():
            if outs:
                share = 1.0 / len(outs)
                for w in outs:
                    M[index[w]][index[v]] = share
            else:
                for i in range(n):           # dead end: spread it everywhere
                    M[i][index[v]] = 1.0 / n

        r = [1.0 / n] * n
        for self.iterations in range(1, self.max_iter + 1):
            nr = [0.0] * n
            for i in range(n):
                row = M[i]
                s = 0.0
                for j in range(n):
                    if row[j]:
                        s += row[j] * r[j]
                nr[i] = self.beta * s + (1 - self.beta) / n
            delta = sum(abs(a - b) for a, b in zip(nr, r))
            r = nr
            if delta < self.tol:
                break
        return {v: r[index[v]] for v in nodes}

    def memory_floats(self):
        return getattr(self, "_n", 0) ** 2


class YourPageRank:
    """Your PageRank.

        __init__(beta=0.85, tol=1e-10, max_iter=100)
        run(graph) -> {node: rank}
        memory_floats() -> the largest number of floats you held at once

    Same ranks, to within 1e-9 per node. Far less memory.

    `graph` is {node: [out-neighbours]}. Note what that already is: an adjacency
    list, which is the sparse representation. The dense version throws that
    structure away and then pays to get it back.

    Two things to be careful about, and they are the same two as Task 1:

      * dead ends, whose rank has to go somewhere
      * the teleport term, which touches every node and is therefore the one
        part that looks like it needs a dense operation - it does not, and
        working out why is the point of §5.2.3

    `memory_floats()` is on your honour and the harness reads it. Count the
    numbers you actually hold at once.
    """

    def __init__(self, beta=0.85, tol=1e-10, max_iter=100):
        self.beta, self.tol, self.max_iter = beta, tol, max_iter
        self._floats = 0

    def run(self, graph):
        nodes = list(graph)
        n = len(nodes)
        dead_ends = [v for v in nodes if not graph[v]]

        # M 을 만들지 않는다. 인접 리스트(graph)가 이미 희소 표현이다.
        # 들고 있는 float 은 rank 벡터 두 개(r, nr)뿐 = 2n.
        r = {v: 1.0 / n for v in nodes}
        self._floats = 2 * n

        for self.iterations in range(1, self.max_iter + 1):
            # 텔레포트 (1-beta)/n 와 dead end 재분배 beta*(sum r_dead)/n 는
            # 둘 다 '모든 노드에 같은 상수를 더하는' 연산 -> 스칼라 하나로 처리(밀집 아님).
            dead_mass = sum(r[d] for d in dead_ends) / n
            base = self.beta * dead_mass + (1.0 - self.beta) / n
            nr = {v: base for v in nodes}
            # 링크 기여는 엣지 수만큼만 순회 (n^2 아님)
            for v in nodes:
                outs = graph[v]
                if outs:
                    share = self.beta * r[v] / len(outs)
                    for w in outs:
                        nr[w] += share
            delta = sum(abs(nr[v] - r[v]) for v in nodes)
            r = nr
            if delta < self.tol:
                break
        return r

    def memory_floats(self):
        return self._floats
