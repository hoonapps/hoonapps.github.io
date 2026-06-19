---
title: "Enterprise AX Agent Platform 11단계: Operations Summary API"
date: 2026-06-19 21:18:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, operations, dashboard, read-model, backend]
---

운영 화면을 만들기 전에 먼저 필요한 것이 있다.

```text
대시보드가 어떤 데이터를 봐야 하는가?
그 데이터는 어디에서 계산할 것인가?
별도 집계 테이블이 지금 필요한가?
```

이번 단계에서는 operator dashboard를 위한 backend read model을 먼저 만들었다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 목표

새 API는 다음이다.

```text
GET /v1/operations/summary
```

목표는 운영자가 보는 핵심 지표를 한 번에 반환하는 것이다.

```text
문서 수
pending approval 수
Agent 실행 수
평균 latency
평균 confidence
event type별 count
tool decision별 count
approval 상태별 count
gateway fallback count
최신 evaluation metrics
```

이 API는 dashboard의 데이터 계약이다.

## Read Model

이번 구현에서 별도 metrics table은 만들지 않았다.

현재 시스템에는 이미 세 가지 데이터 원천이 있다.

```text
DocumentRepositoryPort
ApprovalRepositoryPort
AuditLogPort
```

`OperationsSummaryUseCase`는 이 세 포트를 읽어서 summary를 계산한다.

```text
DocumentRepositoryPort
ApprovalRepositoryPort
AuditLogPort
  -> OperationsSummaryUseCase
  -> OperationsSummary
```

MVP 단계에서는 이 방식이 더 낫다.

- schema를 불필요하게 늘리지 않는다.
- 이미 쌓이는 audit event를 활용한다.
- 나중에 materialized view나 metrics table로 교체할 수 있다.
- dashboard API 계약을 먼저 고정할 수 있다.

## 응답 구조

응답 예시는 다음과 같다.

```json
{
  "tenant_id": "default",
  "event_limit": 500,
  "document_count": 12,
  "pending_approval_count": 2,
  "agent_run_count": 31,
  "average_latency_ms": 42.3,
  "average_confidence": 0.81,
  "event_counts": {
    "agent.answer.generated": 31,
    "tool.approval_required": 5
  },
  "tool_decision_counts": {
    "allowed": 8,
    "approval_required": 5,
    "denied": 1
  },
  "approval_counts": {
    "requested": 5,
    "executed": 2,
    "rejected": 1
  },
  "gateway_fallback_count": 0,
  "latest_evaluation_metrics": {
    "average_score": 1.0,
    "pass_rate": 1.0
  }
}
```

운영자가 지금 시스템이 어떤 상태인지 빠르게 판단할 수 있는 값만 넣었다.

## 계산 방식

`OperationsSummaryUseCase`는 최근 audit event를 기준으로 집계한다.

```text
agent.answer.generated -> agent run count, latency, confidence
tool.*                 -> tool decision count
approval.*             -> approval count
evaluation.completed   -> latest evaluation metrics
tool output _gateway   -> fallback count
```

pending approval 수는 approval repository에서 직접 읽는다.  
문서 수는 document repository에서 직접 읽는다.

이 둘은 현재 상태값이고, 나머지는 이벤트 기반 지표다.

## 테스트

테스트는 실제 이벤트를 만든 뒤 summary를 검증한다.

```text
문서 적재
-> Agent 실행
-> MCP write tool call로 approval_required 생성
-> evaluation run 실행
-> operations summary 조회
```

검증하는 것:

- document count가 증가한다.
- agent run count가 잡힌다.
- pending approval count가 잡힌다.
- event count가 잡힌다.
- tool decision count가 잡힌다.
- latest evaluation metrics가 포함된다.

검증 결과:

```text
make verify
ruff check .                       -> 통과
mypy apps --explicit-package-bases -> 통과
pytest                             -> 14 passed
regression evaluation              -> 통과
```

## 다음 단계

이제 dashboard가 사용할 backend contract가 생겼다.

다음 단계는 두 가지 방향 중 하나다.

1. operator dashboard 화면 구현
2. summary API에 time window, scenario filter, aggregation bucket 추가

화면을 바로 만들 수도 있지만, 좋은 운영 화면은 먼저 좋은 read model이 있어야 한다.  
이번 단계는 그 기반을 고정한 작업이다.
