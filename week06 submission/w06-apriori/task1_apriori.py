#!/usr/bin/env python3
"""Week 6 · Task 1 — A-Priori, and why the second pass is the whole problem.

Textbook §6.1 (market-basket model), §6.2 (A-Priori).

Finding frequent pairs is easy until you count how many pairs there are. With
n items there are n(n-1)/2 of them, and for a supermarket's 10,000 items that
is 50 million counters before you have read a single basket.

A-Priori's observation is one sentence long: **a pair cannot be frequent unless
both of its items are frequent.** One extra pass over the data buys you a much
smaller second pass, and the whole chapter is consequences of that trade.

    python3 task1_apriori.py --verify
"""
import argparse
from itertools import combinations

# Small enough to check by hand. support threshold 3 unless stated.
BASKETS = [
    {"bread", "milk"},
    {"bread", "diaper", "beer", "egg"},
    {"milk", "diaper", "beer", "cola"},
    {"bread", "milk", "diaper", "beer"},
    {"bread", "milk", "diaper", "cola"},
    {"bread", "milk", "beer"},
    {"diaper", "beer"},
]


def _item_counts(baskets):
    counts = {}
    for basket in baskets:
        for item in basket:
            counts[item] = counts.get(item, 0) + 1
    return counts


def frequent_singletons(baskets, support):
    """Items appearing in at least `support` baskets. Return {item: count}."""
    return {i: c for i, c in _item_counts(baskets).items() if c >= support}


def frequent_pairs(baskets, support):
    """Pairs appearing in at least `support` baskets, using A-Priori.

    Return {frozenset({a, b}): count}.

    pass 1 로 빈발 단일 아이템을 구한 뒤, pass 2 는 **두 아이템이 모두 빈발일 때만**
    그 쌍을 센다. 모든 쌍을 세고 나중에 거르는 건 답은 같아도 A-Priori 가 피하려는
    바로 그것이다(Task 3 가 그 차이를 측정한다).
    """
    frequent = set(frequent_singletons(baskets, support))     # pass 1 생존자
    pair_counts = {}
    for basket in baskets:
        survivors = sorted(basket & frequent)                 # 빈발 아이템만
        for pair in combinations(survivors, 2):
            key = frozenset(pair)
            pair_counts[key] = pair_counts.get(key, 0) + 1
    return {k: c for k, c in pair_counts.items() if c >= support}


def association_rules(baskets, support, min_confidence):
    """Rules I -> j from the frequent pairs.

    For a frequent pair {i, j}, confidence of i -> j is
    support({i, j}) / support({i}). 방향에 따라 다르다(비대칭).

    Return [(antecedent, consequent, confidence, lift), ...] for rules whose
    confidence is at least `min_confidence`, sorted by confidence descending.

    `lift` = confidence / (consequent 자체의 지지 비율). confidence 는 높은데 lift 가
    1 근처면 그 결론 아이템이 원래 흔했다는 뜻일 뿐, 관계를 말해주지 않는다(§6.1.3).
    """
    item_counts = _item_counts(baskets)
    n = len(baskets)
    pairs = frequent_pairs(baskets, support)

    rules = []
    for pair, pc in pairs.items():
        i, j = tuple(pair)
        for ante, cons in ((i, j), (j, i)):                   # 양방향
            confidence = pc / item_counts[ante]
            lift = confidence / (item_counts[cons] / n)
            if confidence >= min_confidence:
                rules.append((ante, cons, confidence, lift))
    rules.sort(key=lambda r: r[2], reverse=True)              # confidence 내림차순
    return rules


# ------------------------------------------------------------------- harness
def verify():
    fails = 0

    def check(label, got, want):
        nonlocal fails
        ok = got == want
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<44} {got}"
              + ("" if ok else f"\n{'':>54}want {want}"))
        fails += not ok

    try:
        singles = frequent_singletons(BASKETS, 3)
    except NotImplementedError:
        print("  frequent_singletons is still a stub"); return 1
    # counted by hand: bread 5, milk 5, diaper 5, beer 5, cola 2, egg 1
    check("frequent singletons at support 3",
          dict(sorted(singles.items())),
          {"beer": 5, "bread": 5, "diaper": 5, "milk": 5})

    try:
        pairs = frequent_pairs(BASKETS, 3)
    except NotImplementedError:
        print("  frequent_pairs is still a stub"); return 1
    got = {tuple(sorted(k)): v for k, v in pairs.items()}
    check("frequent pairs at support 3", dict(sorted(got.items())),
          {("beer", "bread"): 3, ("beer", "diaper"): 4, ("beer", "milk"): 3,
           ("bread", "diaper"): 3, ("bread", "milk"): 4, ("diaper", "milk"): 3})

    # cola appears twice, so it must never reach pass two
    check("infrequent items excluded from pairs",
          any("cola" in k or "egg" in k for k in got), False)

    try:
        rules = association_rules(BASKETS, 3, 0.75)
    except NotImplementedError:
        print("  association_rules is still a stub"); return 1
    # diaper -> beer: support 4, diaper 5, confidence 0.8
    hit = [r for r in rules if r[0] == "diaper" and r[1] == "beer"]
    check("diaper -> beer confidence", round(hit[0][2], 3) if hit else None, 0.8)
    check("rules are sorted by confidence",
          all(rules[i][2] >= rules[i + 1][2] for i in range(len(rules) - 1)), True)

    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())
