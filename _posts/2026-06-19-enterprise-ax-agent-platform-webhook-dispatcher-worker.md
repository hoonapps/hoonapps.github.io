---
title: "Enterprise AX Agent Platform 18단계: Webhook Dispatcher와 Worker"
date: 2026-06-19 23:38:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, webhook, worker, reliability, backend]
---

outbox를 만들면 다음 질문은 명확하다.

```text
누가 pending delivery를 보낼 것인가?
외부 endpoint가 실패하면 언제 다시 시도할 것인가?
worker가 여러 개 떠도 같은 delivery를 중복 전송하지 않는가?
최대 재시도 횟수를 넘으면 어떻게 격리할 것인가?
```

이번 단계에서는 webhook dispatcher와 worker 실행 경로를 만들었다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## Dispatcher

dispatcher는 delivery 하나를 전송한다.

```text
WebhookDispatcher.dispatch(tenant_id, delivery_id)
```

전송 전에 subscription을 조회하고, secret이 있으면 payload를 HMAC으로 서명한다.

전송 헤더는 다음과 같다.

```text
X-AX-Delivery-Id
X-AX-Event-Id
X-AX-Event-Type
X-AX-Signature
```

signature는 `sha256=...` 형식이다.

## HTTP Client Port

실제 HTTP 호출은 port로 분리했다.

```text
WebhookHttpClientPort
UrllibWebhookHttpClient
```

dispatcher는 HTTP library를 직접 알지 않는다.

이 경계 덕분에 테스트에서는 fake client로 성공, 실패, timeout을 쉽게 검증할 수 있다.

## Retry Backoff

2xx 응답이면 delivery는 `delivered`가 된다.

실패하면 다음 값을 저장한다.

```text
status=failed
attempt_count += 1
next_attempt_at = now + backoff
last_error = failure reason
```

backoff는 30초부터 시작해 최대 900초까지 증가한다.

## Batch Dispatch

단건 API만 있으면 운영자가 직접 눌러야 한다.

그래서 batch dispatch API를 추가했다.

```text
POST /v1/webhooks/deliveries/dispatch-pending
```

이 API는 전송 가능한 delivery를 가져와 같은 dispatcher로 처리한다.

전송 가능한 대상:

```text
pending
failed + next_attempt_at <= now
dispatching + lease expired
```

## Claim Lease

여러 worker가 동시에 뜨면 같은 delivery를 동시에 가져갈 수 있다.

이를 막기 위해 `dispatching` 상태와 lease를 추가했다.

```text
claim dispatchable deliveries
-> status=dispatching
-> next_attempt_at=lease_until
-> HTTP dispatch
-> delivered / failed / dead_letter
```

Postgres adapter는 `FOR UPDATE SKIP LOCKED`를 사용한다.

```sql
for update skip locked
```

이 방식은 여러 worker가 같은 row를 잡지 않게 한다.
worker가 중간에 죽으면 lease가 만료된 뒤 다시 claim 대상이 된다.

## Dead Letter

최대 시도 횟수를 넘은 delivery는 `dead_letter`가 된다.

```text
failed -> dead_letter
```

`dead_letter`는 자동 재시도 대상에서 빠진다.

운영자가 원인을 처리한 뒤 수동 retry를 호출할 수 있다.

```text
POST /v1/webhooks/deliveries/{delivery_id}/retry
```

retry는 상태와 attempt count를 초기화한다.

```text
status=pending
attempt_count=0
next_attempt_at=null
last_error=null
```

## Worker

CLI worker도 추가했다.

```text
python scripts/dispatch_webhooks.py --tenant-id default --limit 100 --loop --interval-seconds 15
```

Docker Compose에서는 worker profile로 실행한다.

```bash
docker compose --profile worker up --build api webhook-worker
```

API와 worker는 같은 image를 사용한다.
차이는 command뿐이다.

## CI

운영 구성도 깨지면 안 된다.

그래서 CI에 두 단계를 추가했다.

```text
docker compose --profile worker config
docker compose build api webhook-worker
```

이제 Python 테스트뿐 아니라 Compose 설정과 Docker image build도 기본 검증 경로에 들어간다.

## 테스트

테스트는 다음을 확인한다.

```text
서명 헤더가 생성된다.
성공 응답은 delivered로 전이한다.
실패 응답은 failed와 next_attempt_at을 저장한다.
batch dispatch는 due delivery만 처리한다.
claim lease는 중복 dispatch를 막는다.
최대 시도 횟수 초과는 dead_letter로 전이한다.
retry API는 pending으로 되돌린다.
```

현재 검증 명령은 다음이다.

```text
make verify
docker compose --profile worker config
docker compose build api webhook-worker
```

## 다음 단계

이제 Agent 실행, 권한, 평가, 감사, 외부 workflow 전송까지 하나의 운영 흐름으로 이어졌다.

다음 개선은 관측성이다.

```text
request id
structured logging
latency bucket
error taxonomy
dashboard time window
```

운영 제품은 기능이 많아지는 순간보다, 장애를 설명할 수 있을 때 더 강해진다.
