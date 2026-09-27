#!/usr/bin/env python3
"""Week 3 · Task 1 — Minhash and LSH, built from the matrix up.

Textbook §3.2 - §3.4.

Comparing every pair is quadratic, so it stops being possible somewhere around
a hundred thousand documents. The way out is two ideas stacked:

    minhash   replace a set with a short signature, such that the chance two
              signatures agree in a position equals their Jaccard similarity
    LSH       hash bands of those signatures so that similar pairs collide and
              you only ever compare the ones that did

You build both. The textbook's §3.3.5 example is small enough to check by hand,
and the harness checks you against it.

    python3 task1_minhash.py --verify
"""
import argparse

# §3.3.5. Rows are elements 0..4, columns are the sets S1..S4.
BOOK = [[1, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 1, 1],
        [0, 0, 1, 0]]
# The two hash functions the textbook uses on the row numbers.
BOOK_HASHES = [lambda r: (r + 1) % 5, lambda r: (3 * r + 1) % 5]


def jaccard(a, b):
    """|a and b| / |a or b|. Empty union is 0, not an error."""
    union = a | b
    if not union:                 # 두 집합 모두 공집합 -> 합집합 크기 0
        return 0.0
    return len(a & b) / len(union)


def minhash_signatures(columns, hashes, n_rows):
    """Build the signature matrix, one pass over the rows.

    `columns` is [set_of_row_numbers, ...], one entry per document.
    Return [[sig for each hash] for each column].

    §3.3.5의 "One Pass Over the Rows" 알고리즘 그대로:
      1) 모든 SIG(i, c)를 무한대로 초기화한다.
      2) 행 r을 원래 순서대로 딱 한 번만 방문한다 (정렬/재스캔 없음).
      3) 그 행에서 n개의 해시값 h_i(r)을 한 번씩 계산한다.
      4) 열 c가 그 행에 1을 가질 때만 SIG(i, c) = min(SIG(i, c), h_i(r)).

    행을 정렬하거나 열마다 행렬을 다시 훑으면 답은 맞지만, 메모리에 안 들어가는
    행렬에서는 죽는다. 그래서 바깥 루프를 '행'으로 두는 one-pass로 작성한다.
    """
    n_hashes = len(hashes)
    INF = float("inf")
    # SIG(i, c): 열별 시그니처. sig[c][i] = 열 c, 해시 i의 최소 해시값.
    sig = [[INF] * n_hashes for _ in columns]

    for r in range(n_rows):
        # 이 행의 해시값을 한 번씩만 계산 (행당 1회 계산).
        hv = [h(r) for h in hashes]
        for c, rows_in_col in enumerate(columns):
            if r in rows_in_col:          # 이 열이 행 r에 1을 가질 때만 갱신
                sc = sig[c]
                for i in range(n_hashes):
                    if hv[i] < sc[i]:
                        sc[i] = hv[i]
    return sig


def lsh_candidates(signatures, bands):
    """Split each signature into `bands` bands and hash each band.

    Two columns are candidates if they land in the same bucket for **at least
    one** band. Return {(i, j), ...} with i < j.

    R5 결정 — 시그니처 길이가 bands로 나눠떨어지지 않을 때:
      행을 버리지 않고 최대한 고르게 나눈다 (numpy.array_split 방식). 즉
      나머지 rem = n % bands 개의 밴드가 한 행씩 더 갖는다. 정보를 버리는 것보다
      약간 불균일한 밴드가 낫다 — 버려진 행의 일치 신호는 영영 복구할 수 없다.
      나눠떨어지면 모든 밴드가 정확히 r = n // bands 행이 된다.
    """
    n = len(signatures[0]) if signatures else 0
    bands = min(bands, n) if n else bands

    # array_split 방식의 밴드 경계: 앞쪽 rem개 밴드가 한 행씩 더 갖는다.
    base, rem = divmod(n, bands)
    bounds, start = [], 0
    for b in range(bands):
        size = base + (1 if b < rem else 0)
        bounds.append((start, start + size))
        start += size

    candidates = set()
    for band_idx, (lo, hi) in enumerate(bounds):
        # 밴드마다 자기만의 버킷 배열을 쓴다 (다른 밴드 위치의 동일 벡터가
        # 섞여 매치되지 않도록 band_idx를 키에 포함).
        buckets = {}
        for col, sig in enumerate(signatures):
            key = tuple(sig[lo:hi])
            buckets.setdefault(key, []).append(col)
        for cols in buckets.values():
            if len(cols) > 1:
                for a in range(len(cols)):
                    for b in range(a + 1, len(cols)):
                        i, j = cols[a], cols[b]
                        candidates.add((i, j) if i < j else (j, i))
    return candidates


# ------------------------------------------------------------------- harness
def columns_from_matrix(matrix):
    n_rows, n_cols = len(matrix), len(matrix[0])
    return [{r for r in range(n_rows) if matrix[r][c]} for c in range(n_cols)]


def verify():
    fails = 0

    def check(label, got, want):
        nonlocal fails
        ok = got == want
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<44} {got}"
              + ("" if ok else f"\n{'':>54}want {want}"))
        fails += not ok

    cols = columns_from_matrix(BOOK)
    try:
        # S1 = {0,3}, S4 = {0,2,3}: intersection 2, union 3
        check("jaccard(S1, S4)", round(jaccard(cols[0], cols[3]), 4), round(2 / 3, 4))
        check("jaccard(S1, S2)", jaccard(cols[0], cols[1]), 0.0)
        check("jaccard on empty sets", jaccard(set(), set()), 0)
    except NotImplementedError:
        print("  jaccard is still a stub"); return 1

    try:
        sig = minhash_signatures(cols, BOOK_HASHES, len(BOOK))
    except NotImplementedError:
        print("  minhash_signatures is still a stub"); return 1

    # Figure 3.4 in the textbook.
    check("signature of S1", sig[0], [1, 0])
    check("signature of S2", sig[1], [3, 2])
    check("signature of S3", sig[2], [0, 0])
    check("signature of S4", sig[3], [1, 0])

    try:
        cands = lsh_candidates([[1, 0], [3, 2], [0, 0], [1, 0]], bands=2)
    except NotImplementedError:
        print("  lsh_candidates is still a stub"); return 1
    # With one row per band, S1 and S4 are identical, so they must collide.
    check("S1 and S4 are candidates", (0, 3) in cands, True)
    check("S1 and S2 are not", (0, 1) in cands, False)

    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    if not fails:
        print("  Note that S1 and S4 agree in both signature positions, which "
              "estimates\n  their similarity as 1.0 when it is actually 2/3. "
              "Two hashes is not many.")
    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())
