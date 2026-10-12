#!/usr/bin/env python3
"""Week 7 · Task 3 — The same clustering, with far fewer distances.

Textbook §7.3, and §7.1.3 for why distance is the expensive part.

`NaiveKMeans` does what the definition says: every iteration, compare every
point with every centroid. That is n x k distance computations per pass, and on
a real dataset the distance computation is almost the entire cost.

Most of that work is wasted. After the first couple of iterations, most points
do not change cluster, and most centroids barely move. The triangle inequality
lets you prove a point cannot have changed cluster **without measuring it**.

    python3 bench.py
    python3 bench.py --yours

Correctness first: your final SSE must match the baseline's. Fewer distances
with a worse clustering is not an improvement, it is a different algorithm.
"""


class NaiveKMeans:
    """Every point against every centroid, every iteration."""

    def __init__(self, k, max_iter=50):
        self.k, self.max_iter = k, max_iter

    def run(self, points, initial_centroids, distance):
        centroids = list(initial_centroids)
        labels = [None] * len(points)
        for self.iterations in range(1, self.max_iter + 1):
            changed = False
            for i, p in enumerate(points):
                best, bi = None, 0
                for j, c in enumerate(centroids):
                    d = distance(p, c)
                    if best is None or d < best - 1e-12:
                        best, bi = d, j
                if labels[i] != bi:
                    labels[i] = bi
                    changed = True
            centroids = _means(points, labels, self.k, centroids)
            if not changed:
                break
        return labels, centroids


def _means(points, labels, k, previous):
    out = []
    for j in range(k):
        group = [p for p, l in zip(points, labels) if l == j]
        if group:
            out.append(tuple(sum(v) / len(group) for v in zip(*group)))
        else:
            out.append(previous[j])
    return out


class YourKMeans:
    """Your k-means.

        __init__(k, max_iter=50)
        run(points, initial_centroids, distance) -> (labels, centroids)

    Same starting centroids, same `distance` function - which is counted. That
    counter is your score.

    The idea, from §7.3 and the triangle inequality:

        if a point is much closer to its current centroid than that centroid
        moved, and than any other centroid could have come, then it cannot have
        changed cluster, and you do not have to measure anything

    Keeping enough bookkeeping to make that test cheap, without keeping so much
    that the bookkeeping costs more than the distances, is the task.

    You may call `distance` on two centroids, and those calls are counted too -
    which is the correct accounting, since that is real work. There are k of
    them and n points, and k is much smaller than n. That asymmetry is the
    whole opening.
    """

    def __init__(self, k, max_iter=50):
        self.k, self.max_iter = k, max_iter

    def run(self, points, initial_centroids, distance):
        # Hamerly 의 경계 기반 k-means. 근사가 아니라 '바뀔 수 없음을 증명되면 재지 않는다'.
        # 점마다: a=배정 centroid, u=자기 centroid 까지 거리 상한, l=다른 centroid 까지 하한.
        k, n = self.k, len(points)
        centroids = list(initial_centroids)
        a = [0] * n
        u = [0.0] * n
        l = [0.0] * n

        def nearest_two(p):
            ds = [distance(p, c) for c in centroids]     # k distances
            bi, best = 0, ds[0]
            for j in range(1, k):
                if ds[j] < best - 1e-12:                 # 동률은 낮은 인덱스
                    best, bi = ds[j], j
            second = min(ds[j] for j in range(k) if j != bi)
            return bi, best, second

        first = True
        for self.iterations in range(1, self.max_iter + 1):
            if first:
                # 1회차: 가지치기 불가, 전부 전탐색하며 경계 초기화
                for i, p in enumerate(points):
                    a[i], u[i], l[i] = nearest_two(p)
                changed = True
                first = False
            else:
                changed = False
                # s[j] = 자기 외 가장 가까운 centroid 까지 거리의 절반
                s = [0.0] * k
                for j in range(k):
                    s[j] = 0.5 * min(distance(centroids[j], centroids[j2])
                                     for j2 in range(k) if j2 != j)
                for i, p in enumerate(points):
                    m = l[i] if l[i] > s[a[i]] else s[a[i]]
                    if u[i] <= m:                        # 증명: 바뀔 수 없음 -> 0 계산
                        continue
                    u[i] = distance(p, centroids[a[i]])  # 상한 조이기 (1 계산)
                    if u[i] <= m:
                        continue
                    bi, best, second = nearest_two(p)    # 그래도 애매하면 전탐색
                    if bi != a[i]:
                        changed = True
                    a[i], u[i], l[i] = bi, best, second

            labels = a[:]
            prev = centroids
            centroids = _means(points, labels, k, centroids)
            if not changed:
                break
            # centroid 이동량으로 경계 갱신 (iteration 당 k 계산)
            moves = [distance(prev[j], centroids[j]) for j in range(k)]
            pmax = max(moves)
            for i in range(n):
                u[i] += moves[a[i]]
                l[i] -= pmax

        return labels, centroids
