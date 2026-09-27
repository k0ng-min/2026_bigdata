# Week 04 · Mining Data Streams

교재 MMDS §4.1–4.7 · 작업 폴더 [`w04-stream/`](./w04-stream/)

메모리보다 긴 스트림이 한 번만 지나가는데도 답해야 하는 상황. 정확함을 정해진 크기의 공간과 맞바꾸고, **무엇을 포기했는지 정확히 아는 것**이 과제의 핵심이다.

## 결과 요약

| Task | 내용 | 결과 |
|---|---|---|
| Task 1 | 세 스케치 (Bloom·Flajolet-Martin·Reservoir) | `--verify` → **all ok** ✅ |
| Task 2 | Exact가 안 되는 크기 측정 | 내 기계에서 측정 (limits.json/limits.md) ✅ |
| Task 3 | 같은 비트, 더 적은 실수 (최적 Bloom) | FP율 0.831% (바닥 0.82%) → **strong** ✅ |

## Task 1 — 세 스케치
Bloom filter(무거짓음성 구조 + §4.4.2 예측 FP율 0.86% ≈ 실측 0.905%), Flajolet-Martin(확률적 평균화로 참값의 ~1.16배, 2배 이내), Reservoir sampling(Algorithm R, 길이 몰라도 균등 k/n). 자세히: `w04-stream/out/observation.md`.

## Task 2 — 메모리 한계
정확 set의 메모리는 고유값 수에 비례해 커지고, Flajolet-Martin은 레지스터 수(해시 수)로 고정돼 평평하다. 측정값·성장률·정확도 비율은 `w04-stream/out/limits.md`.

## Task 3 — 최적 Bloom
§4.4.2에서 FP율 `(1-e^(-kn/m))^k`를 k로 미분해 최적 `k=(m/n)ln2=7`을 도출. m/n=10에서 이론 바닥 ≈0.82%, 실측 0.831% 달성(거짓 음성 0, 예산 내). 자세히: `w04-stream/out/observation.md`.

## 검증
```bash
cd w04-stream
python test_tasks.py
python ../check.py w04
```
