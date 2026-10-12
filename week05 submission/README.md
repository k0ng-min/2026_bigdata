# Week 05 · Link Analysis (PageRank)

교재 MMDS §5.1–5.4 · 작업 폴더 [`w05-pagerank/`](./w05-pagerank/)

누가 누구를 가리키는지만으로 페이지 중요도를 계산한다. 작동하는 PageRank랑 그걸 깨뜨리는 두 구조(dead end·spider trap)를 만들고, 수렴 비용을 재고, 행렬로는 안 들어가는 그래프에서 희소하게 돌린다.

## 결과 요약

| Task | 내용 | 결과 |
|---|---|---|
| Task 1 | PageRank + 깨진 버전 (dead end·spider trap) | `--verify` → all ok (7/7) |
| Task 2 | 수렴 비용 (beta·크기·tol) | 내 기계에서 측정 (convergence.json/md) |
| Task 3 | 행렬로 안 들어가는 그래프 (희소) | dense와 1e-15 일치, 600× 적은 메모리·66× 빠름 (strong) |

## Task 1 — PageRank와 두 고장

dead end는 rank가 증발해서 그래프가 고갈되고, spider trap은 rank가 갇힌다. 텔레포트(새어나간 몫 + `1-beta`를 모든 노드에 균등 재분배) 한 줄이 두 고장을 동시에 잡는다. 자세히: `w05-pagerank/out/observation.md`.

## Task 2 — 수렴 비용

beta가 1에 가까울수록 반복 수가 늘고, 그래프 크기를 키우면 반복 수는 거의 그대로인데 시간이 늘어난다. 측정값이랑 곡선 형태는 `w05-pagerank/out/convergence.md`에 있다.

## Task 3 — 희소 PageRank

M(n² floats)을 안 만들고 인접 리스트 + rank 벡터 2n floats만 쓴다. dense랑 1e-15 이내로 같은 답을 600배 적은 메모리로 계산한다. 자세히: `w05-pagerank/out/observation.md`.

## 검증

```bash
cd w05-pagerank
python test_tasks.py
python ../check.py w05
```
