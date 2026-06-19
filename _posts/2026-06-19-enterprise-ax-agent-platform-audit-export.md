---
title: "Enterprise AX Agent Platform 10단계: Audit Event Export"
date: 2026-06-19 19:24:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, audit, jsonl, csv, backend]
---

Agent 시스템에서 audit event는 단순 로그가 아니다.

운영자가 나중에 답해야 하는 질문은 구체적이다.

```text
누가 실행했는가?
어떤 정책을 통과했는가?
어떤 tool call이 차단되었는가?
어떤 승인 요청이 반려되었는가?
어떤 평가 실행이 품질 기준을 만족했는가?
```

지난 단계까지는 audit event를 API로 조회할 수 있었다.  
이번 단계에서는 JSONL/CSV export를 추가했다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 목표

이번 기능의 목표는 audit event를 외부 분석 흐름으로 넘길 수 있게 만드는 것이다.

```text
GET /v1/audit/events  -> 화면/운영 조회
GET /v1/audit/export  -> 외부 분석/감사 export
```

export는 두 가지 포맷을 지원한다.

```text
jsonl
csv
```

JSONL은 로그 파이프라인이나 데이터 레이크에 적합하고, CSV는 운영자가 바로 열어보기 쉽다.

## 필터

기존 `AuditLogPort`는 limit만 받았다.

이번 단계에서 다음 필터를 추가했다.

```text
event_type
resource_type
```

메모리 저장소와 Postgres 저장소 모두 같은 필터 규칙을 구현했다.

```text
InMemoryAuditLog.list_events(...)
PostgresAuditLog.list_events(...)
```

저장소가 바뀌어도 API 의미가 바뀌지 않는다.

## API

JSONL export:

```text
GET /v1/audit/export?tenant_id=default&event_type=document.ingested&format=jsonl
```

CSV export:

```text
GET /v1/audit/export?tenant_id=default&resource_type=agent_run&format=csv
```

지원 query parameter:

```text
tenant_id
event_type
resource_type
limit
format
```

## JSONL

JSONL 응답은 한 줄에 이벤트 하나를 담는다.

```json
{"id":"...","tenant_id":"default","event_type":"document.ingested","resource_type":"document","payload":{"title":"..."}}
```

이 형태는 로그 수집기나 배치 파이프라인으로 넘기기 좋다.

## CSV

CSV export는 다음 컬럼을 가진다.

```text
id
tenant_id
actor_type
actor_id
event_type
resource_type
resource_id
payload
created_at
```

`payload`는 JSON 문자열로 직렬화한다.  
이렇게 하면 event별 payload 구조가 달라도 한 파일에 담을 수 있다.

## 테스트

이번 단계에서 추가한 테스트는 다음을 검증한다.

```text
문서 적재
-> document.ingested audit event 생성
-> event_type 필터 조회
-> JSONL export
-> CSV export
```

검증 포인트:

- 필터링된 이벤트만 반환된다.
- JSONL은 line 단위 JSON으로 파싱 가능하다.
- CSV에는 header와 event payload가 포함된다.
- 기존 regression gate까지 함께 통과한다.

검증 결과:

```text
make verify
ruff check .                       -> 통과
mypy apps --explicit-package-bases -> 통과
pytest                             -> 13 passed
regression evaluation              -> 통과
```

## 다음 단계

이제 운영 데이터는 내부에 갇혀 있지 않다.

다음 단계에서는 이 데이터를 보는 화면이나 집계 기능으로 확장할 수 있다.

1. operator dashboard
2. audit metric aggregation
3. evaluation history comparison
4. tool latency metric aggregation
5. approval comment history

Agent 운영에서 중요한 것은 실행 자체보다 실행을 설명할 수 있는 데이터다.  
Audit export는 그 데이터를 제품 밖의 분석 도구와 연결하는 경계다.
