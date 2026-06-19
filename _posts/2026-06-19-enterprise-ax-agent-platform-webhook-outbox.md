---
title: "Enterprise AX Agent Platform 17단계: Webhook Delivery Outbox"
date: 2026-06-19 23:18:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, outbox, webhook, backend]
---

Agent 시스템의 audit event는 내부 기록으로 끝나지 않는다.

운영 환경에서는 audit event가 외부 workflow로 이어져야 한다.

```text
문서 적재 이벤트 -> downstream indexing
승인 요청 이벤트 -> 알림 workflow
평가 완료 이벤트 -> 품질 리포트
정책 차단 이벤트 -> 보안 검토 queue
```

하지만 외부 workflow가 느리거나 실패한다고 Agent 실행이 실패하면 안 된다.

이번 단계에서는 audit event와 외부 전송을 분리하는 webhook delivery outbox를 만들었다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 목표

새 API는 다음이다.

```text
POST /v1/webhooks/subscriptions
GET  /v1/webhooks/subscriptions
GET  /v1/webhooks/deliveries
POST /v1/webhooks/deliveries/{delivery_id}/mark-delivered
POST /v1/webhooks/deliveries/{delivery_id}/mark-failed
```

subscription은 어떤 event type을 어디로 보낼지 정의한다.

delivery는 실제 전송 작업 단위다.

## Outbox Flow

흐름은 다음과 같다.

```text
AuditEvent
  -> OutboxAuditLog
  -> AuditLogPort.append
  -> WebhookSubscription match
  -> WebhookDelivery(status=pending)
```

핵심은 audit event 저장과 외부 HTTP 전송을 분리하는 것이다.

Agent 실행 경로는 delivery 생성까지만 책임진다.
실제 외부 전송은 dispatcher가 처리한다.

## Subscription

subscription은 다음 값을 가진다.

```text
tenant_id
name
target_url
event_types
secret
enabled
```

`event_types`는 `*`를 지원한다.

```json
{
  "tenant_id": "default",
  "name": "approval-workflow",
  "target_url": "https://workflow.internal/hooks/approval",
  "event_types": ["approval.requested"]
}
```

## Delivery

delivery는 audit event를 외부로 보낼 수 있는 작업 단위다.

```text
subscription_id
event_id
event_type
target_url
payload
status
attempt_count
next_attempt_at
last_error
```

target URL과 payload는 delivery 생성 시점의 snapshot으로 저장한다.
subscription이 나중에 바뀌어도 이미 생성된 delivery의 의미가 흔들리지 않게 하기 위해서다.

## Repository

repository는 memory와 Postgres 구현을 모두 제공한다.

```text
WebhookSubscriptionRepositoryPort
WebhookDeliveryRepositoryPort
```

Postgres에는 다음 테이블을 둔다.

```text
webhook_subscriptions
webhook_deliveries
```

delivery status는 처음에는 `pending`, `delivered`, `failed`로 시작했다.
이후 dispatcher 단계에서 `dispatching`, `dead_letter`가 추가된다.

## 테스트

테스트는 subscription을 만든 뒤 문서를 적재한다.

검증하는 흐름:

```text
subscription 생성
문서 적재
document.ingested audit event 생성
matching subscription 조회
pending delivery 생성
delivery 조회 API 확인
```

이 테스트로 audit event와 outbox delivery가 같은 실행 흐름 안에서 만들어지는지 확인했다.

## 다음 단계

outbox는 큐를 만드는 단계다.

다음에는 큐를 안전하게 비우는 dispatcher가 필요하다.

```text
서명
timeout
retry backoff
batch dispatch
worker 중복 실행 방지
dead-letter
```

다음 단계에서 이 전송 경계를 만든다.
