#!/usr/bin/env python3
"""Week 7 · Task 1 — k-means, and the thing that decides the answer.

Textbook §7.1 (clustering, the curse of dimensionality), §7.3 (k-means).

k-means is four lines: pick centroids, assign every point to the nearest one,
move each centroid to the mean of its points, repeat. It always converges.

It converges to a **local** optimum, and which one depends entirely on where you
started. That is not a footnote - it is the difference between a clustering that
means something and one that does not, and you can watch it happen on nine points.

    python3 task1_kmeans.py --verify
"""
import argparse, math, random

# Three obvious blobs of three points each. Any sensible clustering finds them.
BLOBS = [(0.0, 0.0), (0.2, 0.1), (0.1, 0.2),
         (8.0, 8.0), (8.2, 8.1), (8.1, 8.2),
         (0.0, 8.0), (0.2, 8.1), (0.1, 8.2)]


def euclidean(a, b):
    """Distance between two points of any dimension."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def assign(points, centroids):
    """Nearest centroid for each point. Return a list of centroid indices.

    Ties go to the lower index, so that everybody's answer is the same.
    """
    labels = []
    for p in points:
        best, bi = None, 0
        for j, c in enumerate(centroids):
            d = euclidean(p, c)
            if best is None or d < best - 1e-12:     # 동률은 낮은 인덱스 유지
                best, bi = d, j
        labels.append(bi)
    return labels


def update(points, labels, k):
    """Move each centroid to the mean of its points.

    빈 클러스터(점이 하나도 없는 경우)는 평균이 정의되지 않는다 — 여기선 그 자리를
    None 으로 돌려주고, kmeans() 가 **직전 centroid 를 그대로 유지**하도록 처리한다
    (R3 결정: '이전 centroid 유지'. 대안은 가장 먼 점으로 옮기는 것이며 다른 군집을
    만든다). 반환: centroid 리스트(빈 클러스터는 None).
    """
    if not points:
        return [None] * k
    dim = len(points[0])
    sums = [[0.0] * dim for _ in range(k)]
    counts = [0] * k
    for p, l in zip(points, labels):
        counts[l] += 1
        s = sums[l]
        for d in range(dim):
            s[d] += p[d]
    centroids = []
    for j in range(k):
        if counts[j] == 0:
            centroids.append(None)                   # 빈 클러스터
        else:
            centroids.append(tuple(v / counts[j] for v in sums[j]))
    return centroids


def kmeans(points, k, init="random", seed=246, max_iter=100):
    """Run to convergence. Return (labels, centroids, sse).

    `sse` is the sum over points of the squared distance to their own centroid.
    It is what k-means minimises, and it is how you compare two runs.

    `init` is either:
        "random"   pick k points at random as the starting centroids
        "++"       k-means++ (§7.3.2): pick the first at random, then pick each
                   next one with probability proportional to the squared distance
                   to the nearest centroid already chosen

    Set `kmeans.iterations` to how many passes you used.
    """
    rng = random.Random(seed)

    if init == "++":
        centroids = [rng.choice(points)]                 # 첫 센터는 무작위
        while len(centroids) < k:
            # 각 점에서 '이미 고른 센터들' 중 최근접까지의 제곱거리
            d2 = []
            for p in points:
                m = min(sum((x - y) ** 2 for x, y in zip(p, c)) for c in centroids)
                d2.append(m)
            total = sum(d2)
            if total == 0:                               # 모든 점이 센터와 겹침
                centroids.append(rng.choice(points))
                continue
            # 제곱거리에 비례하는 확률로 다음 센터 선택
            r = rng.random() * total
            acc = 0.0
            for p, w in zip(points, d2):
                acc += w
                if acc >= r:
                    centroids.append(p)
                    break
    else:  # "random"
        centroids = list(rng.sample(points, k))

    labels = assign(points, centroids)
    for it in range(1, max_iter + 1):
        new_centroids = update(points, labels, k)
        for j in range(k):
            if new_centroids[j] is None:                 # 빈 클러스터 -> 이전 유지
                new_centroids[j] = centroids[j]
        centroids = new_centroids
        new_labels = assign(points, centroids)
        kmeans.iterations = it
        if new_labels == labels:                         # 라벨이 안 바뀌면 수렴
            labels = new_labels
            break
        labels = new_labels

    return labels, centroids, sse_of(points, labels, centroids)


def sse_of(points, labels, centroids):
    """Sum of squared distances from each point to its assigned centroid."""
    return sum(euclidean(p, centroids[l]) ** 2 for p, l in zip(points, labels))


# ------------------------------------------------------------------- harness
def verify():
    fails = 0

    def check(label, ok, detail=""):
        nonlocal fails
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<50} {detail}")
        fails += not ok

    try:
        check("distance in 2d", abs(euclidean((0, 0), (3, 4)) - 5) < 1e-9)
        check("distance in 5d",
              abs(euclidean((0,) * 5, (1,) * 5) - math.sqrt(5)) < 1e-9)
    except NotImplementedError:
        print("  euclidean is still a stub"); return 1

    try:
        labels, cents, sse = kmeans(BLOBS, 3, init="++", seed=1)
    except NotImplementedError:
        print("  kmeans is still a stub"); return 1

    groups = {}
    for p, l in zip(BLOBS, labels):
        groups.setdefault(l, []).append(p)
    check("three clusters of three", sorted(len(g) for g in groups.values()) == [3, 3, 3],
          sorted(len(g) for g in groups.values()))
    check("the three blobs were recovered",
          all(max(q[0] for q in g) - min(q[0] for q in g) < 1 and
              max(q[1] for q in g) - min(q[1] for q in g) < 1
              for g in groups.values()))
    check("sse is small when clusters are right", sse < 1.0, f"sse {sse:.4f}")

    # Bad luck with random starts should sometimes be visibly worse.
    randoms = [kmeans(BLOBS, 3, init="random", seed=s)[2] for s in range(40)]
    plusplus = [kmeans(BLOBS, 3, init="++", seed=s)[2] for s in range(40)]
    check("random init sometimes lands badly", max(randoms) > min(randoms) * 5,
          f"sse from {min(randoms):.3f} to {max(randoms):.3f}")
    check("k-means++ is more reliable than random",
          sum(plusplus) / len(plusplus) <= sum(randoms) / len(randoms),
          f"mean sse: ++ {sum(plusplus) / len(plusplus):.3f} vs "
          f"random {sum(randoms) / len(randoms):.3f}")

    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())
