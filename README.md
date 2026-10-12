v# 빅데이터개론 실습 과제 (2026-2)

Korea University · Introduction to Big Data
교재 *Mining of Massive Datasets* 기반으로 주차별 실습 과제를 모아둔 저장소다.

## 주차별 현황

| 주차 | 주제 | 폴더 | 상태 |
|---|---|---|---|
| Week 03 | Finding Similar Items — Minhash & LSH | [`week03 submission/`](./week03%20submission/) | 완료 |
| Week 04 | Mining Data Streams — Bloom / FM / Reservoir | [`week04 submission/`](./week04%20submission/) | 완료 |
| Week 05 | Link Analysis — PageRank | [`week05 submission/`](./week05%20submission/) | 완료 |
| Week 06 | Frequent Itemsets — A-Priori / PCY | [`week06 submission/`](./week06%20submission/) | 완료 |
| Week 07 | Clustering — k-means / 차원의 저주 | [`week07 submission/`](./week07%20submission/) | 완료 |

각 주차 폴더에는 강의가 지정한 구조(`wXX-*/` + `check.py`)랑 그 주차 결과 정리(`README.md`)가 같이 들어있다.

## 검증 방법 (예: week05)

```bash
cd "week05 submission/w05-pagerank"
python test_tasks.py       # 각 Task 자동 채점
python ../check.py w05     # 제출 형식 확인
```