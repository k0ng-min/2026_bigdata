# 빅데이터개론 실습 과제 (2026-2)

Korea University · Introduction to Big Data
교재 *Mining of Massive Datasets* 기반 주차별 실습 과제 모음입니다.

## 주차별 현황

| 주차 | 주제 | 폴더 | 상태 |
|---|---|---|---|
| Week 03 | Finding Similar Items — Minhash & LSH | [`week03 submission/`](./week03%20submission/) | ✅ 완료 |
| Week 04 | Mining Data Streams — Bloom / FM / Reservoir | [`week04 submission/`](./week04%20submission/) | ✅ 완료 |
| Week 05 | Link Analysis — PageRank | [`week05 submission/`](./week05%20submission/) | ✅ 완료 |
| Week 06 | (예정) | `week06 submission/` | ⬜ 예정 |
| Week 07 | (예정) | `week07 submission/` | ⬜ 예정 |

각 주차 폴더에는 강의가 지정한 구조(`wXX-*/` + `check.py`)와 그 주차의 결과 정리(`README.md`)가 함께 들어 있습니다.

## 검증 방법 (예: week05)

```bash
cd "week05 submission/w05-pagerank"
python test_tasks.py       # 각 Task 자동 채점
python ../check.py w05     # 제출 형식 확인
```
