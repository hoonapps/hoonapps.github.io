---
title: "Enterprise AX Agent Platform 8단계: Evaluation Runs와 답변 회귀 평가"
date: 2026-06-19 20:18:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, evaluation, rag, regression-test, backend]
---

Agent 제품은 답변을 생성하는 것만으로 끝나지 않는다.

운영 중에는 더 중요한 질문이 생긴다.

```text
검색 품질이 나빠졌는가?
답변이 기대 사실을 포함하는가?
문서나 retrieval 전략을 바꾼 뒤 품질이 유지되는가?
품질 하락을 어떤 지표로 볼 것인가?
```

이번 단계에서는 `EvaluationRun`과 `EvaluationCase`를 추가해 Agent 답변을 반복 측정할 수 있게 만들었다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 목표

이번 기능의 목표는 단순한 테스트 endpoint가 아니다.

```text
평가 dataset을 입력한다.
각 케이스를 실제 Agent 실행 흐름에 태운다.
답변이 expected facts를 포함하는지 채점한다.
케이스별 점수와 실패 사유를 저장한다.
전체 metrics를 계산한다.
감사 이벤트를 남긴다.
```

외부 LLM 없이도 재현 가능해야 하므로, 현재 로컬 답변 생성기는 검색된 근거 문장을 답변에 포함한다.  
이 덕분에 expected facts 기반 평가가 결정론적으로 동작한다.

## 도메인 모델

새로 추가한 모델은 두 개다.

```text
EvaluationRun
  tenant_id
  name
  scenario
  status
  metrics
  cases
  created_at
  completed_at

EvaluationCase
  input_query
  expected_facts
  actual_answer
  score
  failure_reason
```

DB schema에는 이미 `evaluation_runs`, `evaluation_cases`가 있었고, 이번 단계에서 애플리케이션 코드가 붙었다.

## API

새 endpoint는 두 개다.

```text
POST /v1/evaluations/runs
GET  /v1/evaluations/runs/{evaluation_run_id}
```

요청 예시:

```json
{
  "tenant_id": "default",
  "name": "운영 정책 회귀 평가",
  "scenario": "operations",
  "cases": [
    {
      "input_query": "Agent 운영 정책을 정리해줘",
      "expected_facts": ["개인정보 마스킹", "감사로그"]
    }
  ]
}
```

응답 예시:

```json
{
  "status": "completed",
  "metrics": {
    "case_count": 1,
    "average_score": 1.0,
    "pass_rate": 1.0,
    "failed_count": 0
  },
  "cases": [
    {
      "input_query": "Agent 운영 정책을 정리해줘",
      "expected_facts": ["개인정보 마스킹", "감사로그"],
      "score": 1.0,
      "failure_reason": null
    }
  ]
}
```

## 채점 방식

현재 scoring은 단순하고 명시적이다.

```text
score = 답변에 포함된 expected facts 수 / 전체 expected facts 수
```

예를 들어 expected facts가 두 개인데 하나만 답변에 있으면 `0.5`가 된다.

기본 pass threshold는 `0.7`이다.

threshold를 넘지 못하면 `failure_reason`에 누락된 기대 사실을 남긴다.

```text
누락된 기대 사실: 감사로그
```

이 방식은 LLM judge보다 단순하지만, 장점이 있다.

- 결정론적이다.
- 외부 모델 비용이 없다.
- CI에서 반복 실행하기 쉽다.
- retrieval/synthesizer 변경의 회귀를 빠르게 잡을 수 있다.

## 저장소

이번 단계에서는 memory와 Postgres 양쪽 repository를 구현했다.

```text
InMemoryEvaluationRepository
PostgresEvaluationRepository
```

로컬 기본 모드에서는 메모리에 저장되고, Postgres 모드에서는 기존 schema의
`evaluation_runs`, `evaluation_cases`에 저장된다.

## 감사 이벤트

평가 실행이 끝나면 다음 이벤트가 남는다.

```text
event_type: evaluation.completed
resource_type: evaluation_run
payload:
  name
  scenario
  metrics
  case_count
```

평가도 운영 이벤트다.  
품질 지표가 언제, 어떤 dataset으로, 어떤 결과를 냈는지 추적 가능해야 한다.

## 테스트

이번 단계에서 추가한 테스트는 다음 흐름을 검증한다.

```text
문서 적재
-> evaluation run 생성
-> 각 케이스별 Agent 실행
-> expected facts scoring
-> metrics 계산
-> evaluation run 조회
```

검증 결과:

```text
make verify
ruff check .                       -> 통과
mypy apps --explicit-package-bases -> 통과
pytest                             -> 12 passed
```

## 다음 단계

이제 품질 측정의 기본 뼈대가 들어왔다.

다음 확장은 세 방향이다.

1. evaluation dataset 파일 로딩
2. CI regression gate
3. retrieval strategy별 score 비교
4. audit event export
5. operator dashboard

Agent 시스템은 기능이 늘어날수록 품질이 흔들리기 쉽다.  
그래서 평가 기능은 부가 기능이 아니라 운영 백엔드의 핵심 축이다.
