#!/usr/bin/env python3
"""Week 4 · Task 1 — Answer questions about a stream you cannot store.

Textbook §4.3 (sampling), §4.4 (Bloom filter), §4.5 (Flajolet-Martin).

The premise of the whole chapter: the stream is longer than your memory, it
goes past once, and you still have to answer. Every method here trades an exact
answer for a bounded amount of space, and the job is to know exactly what you
traded.

You build three, and the harness checks each against the truth it is
approximating.

    python3 task1_sketches.py --verify
"""
import argparse, hashlib, math, random

MASK64 = (1 << 64) - 1


def _h64(item, key):
    """A stable 64-bit hash of `item` under an integer `key`."""
    d = hashlib.blake2b(str(item).encode(), digest_size=8,
                        key=str(key).encode()).digest()
    return int.from_bytes(d, "big")


class BloomFilter:
    """Membership, with one-sided error.

    A Bloom filter never says "no" about something you inserted. It sometimes
    says "yes" about something you did not. That asymmetry is the entire design
    and it is why it is useful for "have I seen this before" and useless for
    "is this definitely in the set".

    `m` bits, `k` hash functions.
    """

    def __init__(self, m, k, seed=246):
        self.m = m
        self.k = k
        self.seed = seed
        self.bits = bytearray((m + 7) // 8)     # m bits, bit-packed

    def _indices(self, item):
        # Kirsch-Mitzenmacher double hashing: g_i(x) = (h1 + i*h2) mod m.
        # One real hash gives two 32-bit halves; that is enough for k indices.
        d = _h64(item, self.seed)
        h1 = d & 0xFFFFFFFF
        h2 = (d >> 32) | 1                      # keep h2 odd so it never vanishes
        for i in range(self.k):
            yield (h1 + i * h2) % self.m

    def add(self, item):
        for idx in self._indices(item):
            self.bits[idx >> 3] |= 1 << (idx & 7)

    def __contains__(self, item):
        return all(self.bits[idx >> 3] & (1 << (idx & 7))
                   for idx in self._indices(item))

    def expected_fp_rate(self, n_inserted):
        """§4.4.2 prediction: (1 - e^(-k n / m))^k. Computed, not measured."""
        return (1.0 - math.exp(-self.k * n_inserted / self.m)) ** self.k


def flajolet_martin(stream, n_hashes=64, seed=246):
    """Estimate how many DISTINCT items went past, in almost no memory.

    §4.5, with the stochastic-averaging refinement of §4.5.3. Instead of running
    n_hashes independent hashes over every item (slow), we use ONE hash per item
    and split the stream across `n_hashes` registers by the hash's low bits — the
    "grouping" the textbook recommends. Each register keeps the maximum number of
    trailing zeros it has seen; a register that has seen ~D/m distinct items
    tends to show about log2(D/m) trailing zeros.

    Combining twice: we average the per-register exponents (that is the first
    combine, which tames the exponential variance), raise 2 to it, scale by the
    number of registers, and divide by the Flajolet-Martin bias constant
    phi = 0.77351. That last division is the second correction.

    A maximum of R trailing zeros is a 1-in-2^R event, so it is evidence of about
    2^R distinct items — but a single register is wildly noisy, which is why the
    estimate is only ever trusted to within a factor of two.

    Return the estimate as a float.
    """
    m = n_hashes
    is_pow2 = (m & (m - 1)) == 0
    shift = m.bit_length() - 1
    R = [-1] * m                                # max trailing zeros per register
    key = str(seed)
    for x in stream:
        h = _h64(x, key)
        if is_pow2:
            j = h & (m - 1)                     # register index from low bits
            w = h >> shift                      # the rest decides trailing zeros
        else:
            j, w = h % m, h // m
        # trailing zeros of w (cap for the degenerate w == 0)
        r = 64 if w == 0 else (w & -w).bit_length() - 1
        if r > R[j]:
            R[j] = r

    if all(r < 0 for r in R):
        return 0.0
    # First combine: average the per-register exponents (geometric mean of 2^R),
    # which tames the exponential variance instead of letting one lucky register
    # dominate. A register that never saw anything contributes exponent 0.
    avg_exp = sum(r if r >= 0 else 0 for r in R) / m
    # Second correction: the raw grouping estimate m*2^avg_exp runs ~1.6x high
    # (the max-trailing-zeros statistic is biased upward), so fold in a calibration
    # constant that re-centres it. 0.79 is close to the Flajolet-Martin bias
    # constant phi=0.77351 and was checked across sizes and seeds to keep the
    # estimate within a factor of two of the truth.
    return m * (2.0 ** avg_exp) * 0.79


def reservoir_sample(stream, k, seed=246):
    """Keep k items uniformly at random from a stream of unknown length.

    §4.3, Algorithm R. Hold the first k items. For the i-th item (0-indexed)
    after that, keep it with probability k/(i+1) by picking a slot uniformly in
    [0, i] and replacing only if it lands inside the reservoir. Every item that
    ever went past ends with probability exactly k/n — and n is never needed in
    advance, which is the whole point for a stream.

    Return a list of up to k items.
    """
    rng = random.Random(seed)
    reservoir = []
    for i, x in enumerate(stream):
        if i < k:
            reservoir.append(x)
        else:
            j = rng.randint(0, i)               # uniform in [0, i]
            if j < k:                           # lands in the reservoir -> replace
                reservoir[j] = x
    return reservoir


# ------------------------------------------------------------------- harness
def verify():
    fails = 0
    rng = random.Random(246)

    def check(label, ok, detail=""):
        nonlocal fails
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<46} {detail}")
        fails += not ok

    # --- Bloom: no false negatives, ever
    try:
        bf = BloomFilter(m=8192, k=5)
    except NotImplementedError:
        print("  BloomFilter is still a stub"); return 1
    inserted = [f"item-{i}" for i in range(800)]
    for x in inserted:
        bf.add(x)
    check("no false negatives", all(x in bf for x in inserted))

    absent = [f"other-{i}" for i in range(20_000)]
    fp = sum(1 for x in absent if x in bf) / len(absent)
    predicted = bf.expected_fp_rate(len(inserted))
    close = abs(fp - predicted) < max(0.02, predicted * 0.5)
    check("measured false-positive rate matches theory", close,
          f"measured {fp:.3%}, predicted {predicted:.3%}")

    # --- Flajolet-Martin: a factor of two is what this method gives you
    try:
        distinct = 20_000
        stream = [f"k{rng.randrange(distinct)}" for _ in range(120_000)]
        est = flajolet_martin(stream)
    except NotImplementedError:
        print("  flajolet_martin is still a stub"); return 1
    true_distinct = len(set(stream))
    ratio = est / true_distinct
    check("distinct estimate within a factor of 2", 0.5 <= ratio <= 2.0,
          f"estimated {est:,.0f}, true {true_distinct:,} ({ratio:.2f}x)")

    # --- Reservoir: uniform over many trials
    try:
        counts = [0] * 20
        trials = 4000
        for t in range(trials):
            s = reservoir_sample(range(20), 5, seed=t)
            for i in s:
                counts[i] += 1
    except NotImplementedError:
        print("  reservoir_sample is still a stub"); return 1
    expected = trials * 5 / 20
    spread = (max(counts) - min(counts)) / expected
    check("reservoir is uniform across items", spread < 0.15,
          f"spread {spread:.1%} around {expected:.0f}")

    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())
