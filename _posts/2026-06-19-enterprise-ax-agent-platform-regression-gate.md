---
title: "Enterprise AX Agent Platform 9단계: CI Regression Gate"
date: 2026-06-19 20:38:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, evaluation, ci, regression-gate, backend]
---

지난 단계에서 `EvaluationRun` API를 만들었다.

하지만 운영 제품에서 평가는 API로 한 번 실행할 수 있는 기능에 그치면 부족하다.  
코드를 바꿀 때 품질이 떨어지는지 자동으로 막을 수 있어야 한다.

이번 단계에서는 evaluation dataset을 파일로 만들고, CI regression gate를 추가했다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 목표

이번 단계의 목표는 명확하다.

```text
sample documents를 적재한다.
evaluation dataset을 로드한다.
실제 EvaluateAgentUseCase를 실행한다.
average_score와 pass_rate를 검사한다.
기준 미달이면 CI를 실패시킨다.
```

이제 답변 품질은 수동 확인이 아니라 품질 게이트의 일부가 됐다.

## Dataset

새 파일을 추가했다.

```text
data/evaluation/regression_ko.json
```

구조는 다음과 같다.

```json
{
  "tenant_id": "default",
  "name": "core-agent-regression-ko",
  "scenario": "operations",
  "minimum_average_score": 0.8,
  "minimum_pass_rate": 1.0,
  "cases": [
    {
      "input_query": "AX Agent 거버넌스 기준을 설명해줘",
      "expected_facts": ["개인정보", "감사 이벤트", "쓰기 작업"]
    }
  ]
}
```

dataset은 API request와 비슷하게 생겼지만, CI 기준값을 추가로 가진다.

```text
minimum_average_score
minimum_pass_rate
```

품질 기준이 코드가 아니라 dataset에 들어가므로, 평가 기준을 버전 관리할 수 있다.

## Regression Script

새 스크립트는 다음이다.

```text
scripts/run_regression_eval.py
```

이 스크립트는 서버를 띄우지 않는다.  
FastAPI endpoint를 우회하고 애플리케이션 use case를 직접 실행한다.

```text
load dataset
-> ingest sample docs
-> EvaluateAgentUseCase.execute()
-> print metrics
-> compare thresholds
-> exit 1 on failure
```

서버 없이 실행되므로 CI가 빠르고 안정적이다.

## Makefile

새 target을 추가했다.

```bash
make regression
```

그리고 `make verify`에 포함했다.

```text
verify: lint typecheck test regression
```

이제 로컬 검증과 CI 검증이 같은 품질 게이트를 탄다.

## CI

GitHub Actions에도 regression evaluation 단계를 추가했다.

```text
Lint
Typecheck
Test
Regression evaluation
```

일반 테스트가 코드의 동작을 본다면, regression evaluation은 Agent 답변 품질이 기준 아래로 내려갔는지 본다.

## 답변 근거 길이 조정

처음 gate를 돌렸을 때 실패했다.

원인은 두 가지였다.

```text
1. expected fact 표현이 실제 제품 언어와 다른 케이스
2. 답변의 evidence compact 길이가 짧아 핵심 문장이 잘리는 케이스
```

그래서 dataset 표현을 제품 용어에 맞추고, `GroundedAnswerSynthesizer`의 근거 compact 길이를 늘렸다.

이 변경은 평가를 통과시키기 위한 꼼수가 아니라 답변 품질 개선이다.  
근거 문장을 너무 짧게 자르면 사용자가 확인해야 할 내용도 같이 사라진다.

## 실행 결과

최종 regression 결과:

```json
{
  "metrics": {
    "average_score": 1.0,
    "case_count": 4,
    "failed_count": 0,
    "pass_rate": 1.0
  }
}
```

전체 검증 결과:

```text
make verify
ruff check .                       -> 통과
mypy apps --explicit-package-bases -> 통과
pytest                             -> 12 passed
regression evaluation              -> 통과
```

## 다음 단계

품질 게이트가 들어왔으니 다음 확장은 더 운영적인 영역이다.

1. audit event export
2. operator dashboard
3. evaluation history comparison
4. tool latency metric aggregation
5. approval comment history

Agent 시스템은 기능을 추가할수록 답변 품질과 실행 경계가 흔들릴 수 있다.  
CI regression gate는 그 흔들림을 조기에 잡는 최소 장치다.
