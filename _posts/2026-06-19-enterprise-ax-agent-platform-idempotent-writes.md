---
title: "Enterprise AX Agent Platform 14단계: Idempotent Write Requests"
date: 2026-06-19 22:18:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, idempotency, api-design, backend]
---

운영 API에서 write 요청은 네트워크 실패와 함께 생각해야 한다.

클라이언트가 다음 상황을 만나면 어떻게 해야 할까?

```text
문서 적재 요청을 보냈다.
서버는 처리했다.
응답을 받기 전에 클라이언트 timeout이 났다.
클라이언트가 같은 요청을 다시 보냈다.
```

서버가 같은 작업을 두 번 실행하면 문제가 생긴다.

이번 단계에서는 주요 write API에 `Idempotency-Key`를 붙였다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 적용 대상

멱등 처리는 side effect가 있는 write API에 적용했다.

```text
POST /v1/documents/ingest
POST /v1/agents/runs
POST /v1/evaluations/runs
```

요청자는 헤더를 보낸다.

```http
Idempotency-Key: agent-run-20260619-001
```

## 동작 규칙

규칙은 단순하다.

```text
같은 key + 같은 payload   -> 저장된 response replay
같은 key + 다른 payload   -> 409 Conflict
처음 보는 key             -> use case 실행 후 response 저장
```

여기서 중요한 것은 key만 보는 것이 아니라 payload hash도 같이 본다는 점이다.

같은 key로 다른 요청을 보내면 그것은 안전한 재시도가 아니다.
그래서 `409 Conflict`로 막는다.

## 저장 모델

도메인 모델은 `IdempotencyRecord`다.

```text
tenant_id
key
request_hash
response_payload
created_at
```

repository port는 두 구현을 가진다.

```text
InMemoryIdempotencyRepository
PostgresIdempotencyRepository
```

메모리 모드는 로컬 실행과 테스트용이다.
Postgres 모드는 `idempotency_keys` 테이블에 기록한다.

## Router Boundary

멱등성은 use case 내부가 아니라 HTTP router 경계에서 처리했다.

이유는 명확하다.

```text
Idempotency-Key는 HTTP 요청 계약이다.
use case는 같은 command가 한 번 실행된다고 가정한다.
저장소는 record를 어떻게 보관할지만 안다.
```

이렇게 나누면 use case가 HTTP 헤더를 알 필요가 없다.

```text
router
  -> idempotency guard
  -> use case
  -> response 저장
```

## Approval Replay와의 차이

이미 approval replay 멱등성이 있다.

하지만 두 멱등성은 책임이 다르다.

```text
Idempotency-Key
  -> HTTP write API 재시도 중복 방지

Approval replay guard
  -> 승인 이후 tool 실행 중복 방지
```

둘 다 중복 실행을 막지만, 발생하는 위치가 다르다.

## 테스트

테스트는 다음을 검증한다.

```text
첫 요청은 정상 처리된다.
같은 key와 같은 payload는 같은 응답을 반환한다.
같은 key와 다른 payload는 409를 반환한다.
```

이 테스트는 문서 적재, Agent 실행, evaluation run처럼 서로 다른 write API에 같은 규칙이
적용되는지 확인한다.

## 다음 단계

멱등성이 생기면 재시도는 안전해진다.

다음 문제는 데이터 경계다.
API key가 여러 tenant에 접근할 수 있으면 운영 환경에서 실수가 커진다.

다음 단계에서는 API key에 tenant 접근 범위를 붙인다.
