---
title: "Enterprise AX Agent Platform 22단계: Request ID Audit Filter"
date: 2026-06-19 23:59:45 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, audit, observability, backend]
---

지난 단계까지 request id를 세 군데에 연결했다.

```text
HTTP response header
audit event payload
webhook delivery payload
```

하지만 운영자가 실제로 필요한 것은 다음 질문에 답하는 것이다.

```text
이 request id로 발생한 audit event를 보여줘.
이 request id 관련 이벤트를 JSONL로 export해줘.
```

이번 단계에서는 audit 조회와 export에 `request_id` 필터를 추가했다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 목표

새로운 query parameter는 다음이다.

```text
request_id
```

사용 예시는 다음과 같다.

```text
GET /v1/audit/events?tenant_id=default&request_id=local-trace-001
GET /v1/audit/export?tenant_id=default&request_id=local-trace-001&format=jsonl
```

기존 필터와 같이 조합할 수 있다.

```text
event_type=document.ingested
resource_type=agent_run
request_id=local-trace-001
limit=500
```

## Port 변경

`AuditLogPort.list_events`에 optional filter를 추가했다.

```text
request_id: str | None = None
```

이 포트는 여러 구현체가 공유한다.

```text
InMemoryAuditLog
PostgresAuditLog
OutboxAuditLog
RequestContextAuditLog
```

decorator도 같은 시그니처를 유지해야 한다.
그래야 라우터가 어떤 audit log 구현이 들어왔는지 몰라도 된다.

## Memory Adapter

메모리 구현은 payload dict에서 직접 비교한다.

```text
event.payload.get("request_id") == request_id
```

테스트와 로컬 기본 실행에서 충분하다.

## Postgres Adapter

Postgres 구현은 JSONB expression을 사용한다.

```sql
e.payload ->> 'request_id' = %s
```

이 필터는 운영에서 자주 쓰일 수 있으므로 초기 schema에 expression index를 추가했다.

```sql
create index ix_audit_events_request_id
  on audit_events (tenant_id, (payload ->> 'request_id'), created_at desc);
```

단순히 query parameter를 붙이는 것이 아니라, 조회 패턴에 맞춰 DB index까지 같이 설계해야 한다.

## API

라우터는 `/events`와 `/export` 모두 같은 필터를 받는다.

```text
GET /v1/audit/events
GET /v1/audit/export
```

export도 같은 필터를 지원해야 하는 이유는 운영자가 화면에서 본 이벤트를 파일로 넘기는 흐름이
자연스럽기 때문이다.

```text
화면 조회 -> request_id로 좁힘 -> JSONL/CSV export
```

## 테스트

테스트는 같은 tenant에 서로 다른 request id로 두 문서를 적재한다.

```text
request-filter-001 -> document A
request-filter-002 -> document B
```

그 다음 `request-filter-001`로 audit events를 조회한다.

검증하는 것:

```text
결과가 1개만 나온다.
payload.request_id가 request-filter-001이다.
export JSONL도 같은 이벤트 1개만 포함한다.
```

이 테스트는 단순 조회뿐 아니라 export 경로까지 같이 확인한다.

## 검증 결과

```text
make verify
ruff check .                       -> 통과
mypy apps --explicit-package-bases -> 통과
pytest                             -> 35 passed
regression evaluation              -> 통과
docker compose build               -> 통과
```

## 다음 단계

이제 request id는 남고, 조회되고, export된다.

다음 개선은 dashboard에서 이 기능을 직접 사용할 수 있게 만드는 것이다.

```text
audit event request id 검색 input
최근 오류 request id quick filter
latency가 높은 request 추적
```

관측성은 저장보다 조회가 중요하다. 찾을 수 없는 trace는 운영 도구가 아니다.
