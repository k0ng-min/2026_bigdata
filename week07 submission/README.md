# Week 07 · Clustering (k-means & 차원의 저주)

교재 MMDS §7.1–7.3 · 작업 폴더 [`w07-kmeans/`](./w07-kmeans/)

클러스터링은 어느 점들이 한 묶음인지를 묻는 건데, 그러려면 "가깝다"가 뭔가를 의미해야 한다. 표준 방법을 만들고, 그 답을 뭐가 결정하는지 보고, 차원이 얼마나 올라가면 "가깝다"가 의미를 잃는지 재고, 같은 클러스터링을 훨씬 적은 일로 해본다.

## 결과 요약

| Task | 내용 | 결과 |
|---|---|---|
| Task 1 | k-means + 초기화 (k-means++) | `--verify` → all ok |
| Task 2 | 거리가 의미를 잃는 지점 측정 | 내 기계에서 측정 (curse.json/md) |
| Task 3 | 같은 클러스터링, 더 적은 거리 계산 | 거리 88.1% 절감, SSE 차이 0 (strong) |

## Task 1 — k-means와 초기화

빈 클러스터는 직전 centroid를 그대로 유지하는 쪽을 택했다(결정론적이고 단순해서). 9개 점·3블롭에서 40시드로 돌려보니 무작위 초기화는 평균 SSE 38.5로 자주 틀렸고, k-means++는 40번 다 맞혔다(평균 0.120). SSE로는 k를 못 고른다(k 커질수록 항상 줄어서 k=n을 고르게 됨). 자세히: `w07-kmeans/out/observation.md`.

## Task 2 — 차원의 저주

n=1,000에서 contrast가 약 50차원에서 1 아래로 떨어지고(200차원에선 최원접이 최근접의 1.37배), 평균거리는 √d에 비례(평균÷√d ≈ 0.41)해 커졌다. "거리가 의미를 잃었다"는 contrast보다 상대표준편차(1/√d로 감소)가 더 잘 잡는다. 측정값은 `w07-kmeans/out/curse.md`.

## Task 3 — 더 적은 거리 계산

Hamerly 경계(점마다 숫자 3개: 라벨 a, 상한 u, 하한 l)로 "안 바뀜이 증명된 점"만 건너뛴다. 근사를 전혀 안 해서 baseline이랑 SSE 차이가 정확히 0이고, 거리 계산은 10,320,000 → 1,225,740으로 88.1% 줄었다. 자세히: `w07-kmeans/out/observation.md`.

## 검증

```bash
cd w07-kmeans
python test_tasks.py
python ../check.py w07
```
