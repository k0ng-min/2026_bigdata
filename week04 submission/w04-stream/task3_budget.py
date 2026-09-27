#!/usr/bin/env python3
"""Week 4 · Task 3 — Same memory, fewer mistakes.

Textbook §4.4 (Bloom filters), §4.5 (counting distinct).

`NaiveFilter` is a membership filter in a fixed number of bits. It works. It
also makes far more mistakes than it has to with the memory it was given, and
it does so for a reason you can find by reading §4.4.2 and doing one derivative.

You get **exactly the same number of bits**. Make fewer mistakes.

    python3 bench.py
    python3 bench.py --yours

The rule that makes this interesting: a false negative is not allowed. Ever.
The whole point of this structure is that "no" means no. A filter that gets a
better score by occasionally forgetting something it was given has not improved
anything, it has broken the contract.
"""
import hashlib, math


class NaiveFilter:
    """One hash function, and the bits it was given."""

    def __init__(self, n_bits, seed=246):
        self.n_bits = n_bits
        self.seed = seed
        self.bits = bytearray(n_bits)

    def _index(self, item):
        d = hashlib.blake2b(str(item).encode(), digest_size=8,
                            key=str(self.seed).encode()).digest()
        return int.from_bytes(d, "big") % self.n_bits

    def add(self, item):
        self.bits[self._index(item)] = 1

    def __contains__(self, item):
        return bool(self.bits[self._index(item)])

    def memory_bits(self):
        return self.n_bits


class YourFilter:
    """Your filter.

        __init__(n_bits, seed=246)
        add(item)
        item in filter  ->  bool
        memory_bits()   ->  how many bits you are using

    `memory_bits()` must not exceed the `n_bits` you were given. The harness
    checks. Counting only some of your memory is not an optimisation.

    §4.4.2 gives the false-positive rate of a filter with m bits, k hashes and
    n items inserted. There is a k that minimises it, and it depends on m/n.
    The harness tells you n before you start, so you have no excuse for guessing.

    Then there is a second question, which is worth more: the harness inserts
    a **known** number of items, but a real stream does not tell you n in
    advance. What would you do then? You do not have to implement it - but
    observation.md asks.
    """

    # 과제가 알려준 값: 삽입 아이템 수 n = 8,000, 예산 m = 80,000 bits -> m/n = 10.
    # §4.4.2: m bits, n items, k hashes일 때 FP율 = (1 - e^(-kn/m))^k 이고,
    # 이를 k로 미분해 0으로 두면 최소가 k* = (m/n) ln 2 에서 나온다.
    # (m/n=10) -> k* = 10 * 0.6931 = 6.93 -> k = 7.  이때 FP율 ≈ 0.82% (이론 바닥).
    N_ITEMS = 8_000

    def __init__(self, n_bits, seed=246):
        self.m = n_bits
        self.seed = seed
        self.k = max(1, round((n_bits / self.N_ITEMS) * math.log(2)))   # = 7
        self.bits = bytearray((n_bits + 7) // 8)     # m bits, bit-packed

    def _indices(self, item):
        # Kirsch-Mitzenmacher 이중 해싱: 진짜 해시 하나에서 두 조각을 뽑아
        # g_i(x) = (h1 + i*h2) mod m 로 k개의 인덱스를 만든다.
        d = hashlib.blake2b(str(item).encode(), digest_size=16,
                            key=str(self.seed).encode()).digest()
        h1 = int.from_bytes(d[:8], "big")
        h2 = int.from_bytes(d[8:], "big") | 1        # h2는 홀수로 유지
        for i in range(self.k):
            yield (h1 + i * h2) % self.m

    def add(self, item):
        for idx in self._indices(item):
            self.bits[idx >> 3] |= 1 << (idx & 7)

    def __contains__(self, item):
        return all(self.bits[idx >> 3] & (1 << (idx & 7))
                   for idx in self._indices(item))

    def memory_bits(self):
        # 전부 계산: 실제 사용하는 저장소는 비트배열 하나(m 비트)뿐.
        return self.m
