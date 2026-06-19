---
title: "Enterprise AX Agent Platform 20단계: Audit Correlation ID 전파"
date: 2026-06-19 23:59:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, audit, observability, backend]
---

지난 단계에서 모든 HTTP 응답에 `X-Request-ID`와 `X-Process-Time-Ms`를 붙였다.

하지만 request id가 응답 헤더에만 있으면 추적성은 아직 얕다.

운영자가 실제로 봐야 하는 것은 다음 연결이다.

```text
HTTP request
-> audit event
-> webhook delivery
-> external workflow
```

이번 단계에서는 request id를 audit event payload와 webhook delivery payload까지 전파했다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 목표

HTTP 요청이 만든 audit event에는 같은 request id가 들어간다.

```json
{
  "event_type": "document.ingested",
  "payload": {
    "title": "Request context 문서",
    "request_id": "audit-trace-001"
  }
}
```

Webhook delivery payload도 audit event payload를 포함하므로 같은 값을 가진다.

```json
{
  "event_type": "document.ingested",
  "payload": {
    "payload": {
      "request_id": "audit-trace-001"
    }
  }
}
```

이제 외부 workflow 로그에서도 같은 correlation id를 볼 수 있다.

## Decorator 위치

request id를 use case마다 직접 넣지 않았다.

대신 `AuditLogPort` decorator를 추가했다.

```text
RequestContextAuditLog
```

흐름은 다음과 같다.

```text
RequestContextMiddleware
  -> current_request_id()
  -> RequestContextAuditLog
  -> AuditEvent.payload.request_id
  -> OutboxAuditLog
  -> WebhookDelivery.payload.payload.request_id
```

중요한 점은 decorator 순서다.

```text
RequestContextAuditLog(
  inner=OutboxAuditLog(...)
)
```

request id를 먼저 audit event에 붙이고, 그 다음 outbox가 delivery payload를 만든다.
그래야 audit 저장과 webhook delivery가 같은 payload를 공유한다.

## 왜 Use Case에 넣지 않았나

request id는 HTTP context다.

`IngestDocumentUseCase`, `RunAgentUseCase`, `EvaluateAgentUseCase`가 `X-Request-ID`를 알기 시작하면
애플리케이션 계층이 HTTP 헤더에 묶인다.

그래서 use case는 그대로 둔다.

```text
use case -> AuditEvent 생성
decorator -> request context 보강
repository/outbox -> 저장과 delivery 생성
```

이 구조는 HTTP 밖에서 실행되는 regression script나 worker에도 자연스럽다.

HTTP context가 없으면 request id 없이 audit event가 기록된다.

## 덮어쓰기 방지

이미 payload에 `request_id`가 있으면 덮어쓰지 않는다.

이유는 두 가지다.

```text
상위 시스템이 이미 correlation id를 정했을 수 있다.
worker나 batch job이 자체 request id를 넣을 수 있다.
```

관측성 데이터는 보강해야지, 호출자가 명시한 값을 조용히 바꾸면 안 된다.

## 테스트

테스트는 두 경로를 확인한다.

```text
POST /v1/documents/ingest
  X-Request-ID: audit-trace-001
-> GET /v1/audit/events
-> payload.request_id == audit-trace-001
```

그리고 webhook outbox 경로도 확인한다.

```text
subscription 생성
POST /v1/documents/ingest
  X-Request-ID: webhook-trace-001
-> GET /v1/webhooks/deliveries
-> payload.payload.request_id == webhook-trace-001
```

검증 결과:

```text
make verify
pytest -> 32 passed
mypy   -> 61 source files 통과
docker compose build api webhook-worker -> 통과
```

## 다음 단계

request id가 audit와 outbox까지 이어졌다.

다음으로 할 수 있는 일은 두 가지다.

```text
1. error response에도 request id를 표준 구조로 포함한다.
2. dashboard에서 latency와 request id를 더 쉽게 찾게 만든다.
```

오류 응답은 기존 `detail` 계약과 호환성을 고려해야 하므로 별도 단계로 다룬다.
