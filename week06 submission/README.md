# Week 06 · Frequent Itemsets (A-Priori & PCY)

교재 MMDS §6.1–6.4 · 작업 폴더 [`w06-apriori/`](./w06-apriori/)

"X 산 사람이 Y도 산다"는 말하긴 쉬운데 계산은 비싸다. 가능한 쌍 수가 아이템 수에 이차로 늘기 때문이다. 이 과제는 그 비용을 안 내는 표준 방법이랑, 그래도 남는 비용을 재보는 거다.

## 결과 요약

| Task | 내용 | 결과 |
|---|---|---|
| Task 1 | A-Priori + 연관규칙 (confidence·lift) | `--verify` → all ok |
| Task 2 | 임계값 낮추면서 폭발 측정 | 내 기계에서 측정 (explosion.json/md) |
| Task 3 | Pass 2 맞추기 (PCY) | peak 카운터 820,259 → 23,356 (97.2% 절감) (strong) |

## Task 1 — A-Priori와 연관규칙

confidence가 비대칭이라는 걸 봤다. 1468 → 0은 0.839인데 반대 방향 0 → 1468은 0.004다(1468은 62번, 0은 13,080번 등장). 쓸모 있는 규칙은 희귀한 쪽 → 흔한 쪽이다. 가장 confidence 높은 규칙(1468 → 0, lift 1.282)도 lift가 1 근처라 믿을 만하진 않은데, 아이템 0이 전체 65% 바스켓에 든 인기 품목이라 그냥 흔해서 같이 보일 뿐이기 때문이다. 자세히: `w06-apriori/out/observation.md`.

## Task 2 — 임계값을 낮추면

support를 반씩 낮출 때마다 peak 카운터가 3~5배씩 뛰다가, 아이템이 2,000개뿐이라 893,456(전체 동시출현 쌍 수)에서 포화된다. 답(빈발 쌍)은 포화 없이 계속 느는데, 그 답을 찾으려고 세야 하는 카운터가 훨씬 빨리 불어난다. 측정값은 `w06-apriori/out/explosion.md`.

## Task 3 — PCY

버킷 1,000,003개(소수)로 1패스 해시를 돌리고 2패스 전에 1비트 비트맵으로 접었다. 같은 빈발 쌍을 찾으면서 peak 카운터를 820,259 → 23,356으로 97.2% 줄였다. 자세히: `w06-apriori/out/observation.md`.

## 검증

```bash
cd w06-apriori
python test_tasks.py
python ../check.py w06
```
