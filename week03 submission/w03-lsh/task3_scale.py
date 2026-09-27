#!/usr/bin/env python3
"""Week 3 · Task 3 — Find the same pairs without comparing everything.

Textbook §3.4.

`BruteForce` compares every pair. On 3,000 documents that is 4.5 million
comparisons and it is completely correct. On 3 million documents it is 4.5
trillion and it is completely useless.

Beat it. Find the same near-duplicate pairs while making far fewer comparisons.

    python3 bench.py
    python3 bench.py --yours

The harness counts every call you make to `similarity()`. That is your score.
It also checks **recall** - which of the truly similar pairs you found. Skipping
comparisons is easy; skipping comparisons without losing the pairs is the task.
"""
import random

from task1_minhash import lsh_candidates   # Task 1의 밴딩을 그대로 재사용


class BruteForce:
    """Correct, and quadratic."""

    def __init__(self, threshold):
        self.threshold = threshold

    def find(self, docs, similarity):
        """docs is [set_of_shingles, ...]. Return {(i, j), ...} with i < j."""
        out = set()
        for i in range(len(docs)):
            for j in range(i + 1, len(docs)):
                if similarity(docs[i], docs[j]) >= self.threshold:
                    out.add((i, j))
        return out


class YourFinder:
    """Minhash + LSH 밴딩으로 후보 쌍만 추린 뒤, 그 후보에 대해서만 similarity()를 부른다.

    §3.4.2의 S-곡선으로 파라미터를 고른다. 시그니처 길이 n을 b개 밴드(밴드당 r=n/b행)
    로 나누면, 유사도 s인 쌍이 후보가 될 확률은

        P(s) = 1 - (1 - s**r)**b

    이고 곡선의 계단(P=0.5 지점)은 근사적으로 (1/b)**(1/r)에 있다.

    이 과제의 임계는 0.6이다. 심어둔 쌍들의 실제 유사도는 최소 0.622(가장 어려운 쌍)
    부터 0.889까지고, 무관한 쌍은 대부분 ~0.006로 완전히 갈라져 있다.

    선택: n=128, b=32, r=4  ->  계단 ≈ (1/32)**(1/4) = 0.420.
      계단을 임계 0.6보다 '아래'에 일부러 둔다. 강의의 설계 트레이드오프대로,
      진짜 쌍을 놓치는 비용(거짓 음성)이 더 크기 때문이다. 대가는 후보가 늘어나는
      것인데, 무관한 쌍(s≈0.006)이 후보가 될 확률은 P(0.006)≈4e-8로 사실상 0이라
      추가 후보가 거의 생기지 않는다. 반면 가장 어려운 쌍(s=0.622)도
      P=0.994로 거의 확실히 후보가 된다.

    후보는 '공짜'(harness가 과금하지 않음)이고, 각 후보를 similarity()로 한 번씩
    확인해 임계 이상만 최종 결과에 넣는다. 이 확인 호출이 유일하게 과금되는 비교다.
    """

    def __init__(self, threshold, n_hashes=128, bands=32, seed=1):
        self.threshold = threshold
        self.n_hashes = n_hashes
        self.bands = bands
        self.seed = seed

    def _signatures(self, docs):
        """각 문서를 n_hashes개의 minhash 값으로 압축한다.

        명시적 순열은 구현 불가능하므로(§3.3의 "Permutation Is Not Implementable"),
        무작위 선형 해시 h(x) = (a*x + b) mod p 로 순열을 흉내 낸다. 문서 하나에서
        모든 해시의 최소값을 구하는 것이 그 문서의 시그니처다. 시드를 고정해 재현 가능.
        """
        rng = random.Random(self.seed)
        P = 4294967311                       # 2^32보다 큰 소수
        n = self.n_hashes
        A = [rng.randrange(1, P) for _ in range(n)]
        B = [rng.randrange(0, P) for _ in range(n)]
        INF = float("inf")

        sigs = []
        for d in docs:
            sig = [INF] * n
            for x in d:
                for i in range(n):
                    hv = (A[i] * x + B[i]) % P
                    if hv < sig[i]:
                        sig[i] = hv
            sigs.append(sig)
        return sigs

    def find(self, docs, similarity):
        sigs = self._signatures(docs)
        candidates = lsh_candidates(sigs, self.bands)

        out = set()
        for i, j in candidates:
            # 후보에 대해서만 실제 비교 — 유일하게 과금되는 연산.
            if similarity(docs[i], docs[j]) >= self.threshold:
                out.add((i, j))
        return out
