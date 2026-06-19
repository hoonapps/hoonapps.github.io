---
title: "Enterprise AX Agent Platform 07: Audit Trail과 Webhook Outbox"
date: 2026-06-20 00:53:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, audit, webhook, outbox, backend]
description: "Agent 실행, 승인, 평가, 정책 결과를 audit event로 남기고 webhook delivery outbox로 외부 연동을 분리했다."
---

Agent 시스템의 audit event는 로그가 아니다. 나중에 실행을 설명하고 외부 workflow를 연결하는 원장성 이벤트다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## Audit Event

다음 이벤트는 모두 audit trail에 남긴다.

```text
document_ingested
agent_run_created
tool_execution_requested
approval_requested
approval_executed
approval_rejected
policy_blocked
evaluation_completed
webhook_delivery_created
```

payload에는 tenant, actor, request id, 관련 resource id를 포함한다. 운영자가 한 request id로 HTTP 응답, audit event, webhook delivery를 연결해 볼 수 있어야 하기 때문이다.

## Export

운영자는 API 조회만으로 충분하지 않은 경우가 많다. 그래서 audit export를 둔다.

```text
GET /v1/audit/events
GET /v1/audit/export?format=jsonl
GET /v1/audit/export?format=csv
```

필터 기준에는 tenant, event type, request id가 포함된다. 특정 장애나 승인 요청을 조사할 때 필요한 최소 검색 축이다.

## Webhook Outbox

audit event가 외부 workflow로 이어질 수 있도록 webhook subscription과 delivery outbox를 분리했다.

```text
AuditEvent
  -> WebhookDelivery(pending)
  -> Dispatcher
  -> delivered / failed / dead_letter
```

외부 endpoint가 느리거나 실패해도 AgentRun 저장이 실패하면 안 된다. 그래서 event 생성과 외부 전송을 같은 transaction 흐름 안에서 느슨하게 분리한다.

## Dispatcher

dispatcher는 delivery 하나를 전송하고 상태를 업데이트한다.

```text
POST /v1/webhooks/deliveries/{delivery_id}/dispatch
POST /v1/webhooks/deliveries/dispatch-pending
POST /v1/webhooks/deliveries/{delivery_id}/retry
```

retry 횟수를 넘으면 dead-letter 상태로 격리한다. 실패를 무한 재시도하면 장애가 다른 시스템으로 전파된다.

## Request Correlation

모든 HTTP 응답에는 request id와 처리 시간을 붙인다.

```text
X-Request-ID
X-Process-Time-Ms
```

같은 request id가 audit event payload와 webhook delivery payload에도 전파된다. 오류 응답 body에도 request id를 넣되 기존 `detail` 계약은 깨지지 않게 했다.

## 결과

이 단계에서 Agent 실행은 나중에 조사 가능한 이벤트 흐름이 됐다.

- audit event API
- JSONL/CSV export
- request id filter
- webhook subscription
- outbox delivery
- dispatcher, retry, dead-letter
- HTTP response correlation header

운영 가능한 Agent는 답변을 잘하는 것만으로 부족하다. 왜 그런 답변과 실행이 발생했는지 추적할 수 있어야 한다.
