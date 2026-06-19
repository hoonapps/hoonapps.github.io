---
title: "Enterprise AX Agent Platform 13단계: API Key Scope Guard"
date: 2026-06-19 21:58:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, security, api-key, backend]
---

운영 콘솔을 만들면 바로 다음 문제가 생긴다.

```text
누가 문서를 적재할 수 있는가?
누가 Agent를 실행할 수 있는가?
누가 승인 버튼을 누를 수 있는가?
누가 audit event를 볼 수 있는가?
```

이번 단계에서는 HTTP API에 선택형 API key 인증과 scope guard를 붙였다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 목표

기본 로컬 실행은 그대로 열어둔다.

```text
AUTH_ENABLED=false
```

운영형 실행에서는 API key를 요구한다.

```text
AUTH_ENABLED=true
```

호출자는 `X-API-Key` 헤더를 보낸다.

```http
X-API-Key: local-dev-key
```

## Credential Format

credential은 환경변수 하나로 주입한다.

```text
API_KEY_CREDENTIALS=key:actor_id:scope|scope[@tenant|tenant]
```

예시는 다음과 같다.

```text
local-dev-key:operator-01:documents:read|agents:run|approvals:write@default
```

이 값은 세 가지 정보를 가진다.

```text
key      -> 실제 API key
actor_id -> audit와 실행 주체
scope    -> 호출 가능한 HTTP 기능
tenant   -> 접근 가능한 tenant
```

## HTTP Scope

scope는 endpoint 단위로 나눴다.

```text
documents:read
documents:write
knowledge:read
agents:read
agents:run
approvals:read
approvals:write
audit:read
operations:read
ontology:read
tools:read
webhooks:read
webhooks:write
evaluations:read
evaluations:write
mcp:use
```

중요한 점은 HTTP scope와 Agent tool scope를 분리한 것이다.

```text
HTTP API scope      -> endpoint 호출 권한
Agent actor_scopes  -> tool runtime 실행 권한
```

API를 호출할 수 있다고 해서 외부 tool을 실행할 수 있는 것은 아니다.
Agent 실행 요청 안의 `actor_scopes`가 tool registry의 `required_scope`를 다시 통과해야 한다.

## FastAPI Dependency

구현은 FastAPI dependency로 넣었다.

```text
require_scopes("agents:run")
require_scopes("approvals:write")
require_scopes("audit:read")
```

router는 비즈니스 로직 전에 principal을 얻는다.

```text
X-API-Key
  -> parse credential
  -> AuthPrincipal
  -> required scope check
  -> tenant access check
```

권한이 없으면 `403 Forbidden`, key가 없거나 틀리면 `401 Unauthorized`를 반환한다.

## 왜 선택형인가

로컬 개발에서는 인증이 생산성을 떨어뜨릴 수 있다.

그래서 기본값은 비활성화다.

하지만 인증이 선택형이라고 해서 코드 경계가 약한 것은 아니다.
인증을 켜면 보호 대상 router는 모두 같은 dependency를 통과한다.

```text
local mode      -> 빠른 실행
protected mode  -> 동일한 app에서 권한 검증
```

## 테스트

테스트는 세 가지를 확인한다.

```text
인증이 꺼지면 기존 API가 그대로 동작한다.
인증이 켜진 상태에서 key가 없으면 401이다.
scope가 부족하면 403이다.
scope가 맞으면 요청이 통과한다.
```

이 단계에서 security code는 별도 파일로 분리했다.

```text
apps/api/core/security.py
```

## 다음 단계

권한이 생기면 다음 문제는 중복 요청이다.

Agent 실행이나 문서 적재 같은 write API는 클라이언트가 timeout 후 재시도할 수 있다.
다음 단계에서는 `Idempotency-Key`로 write API 재시도를 안전하게 만든다.
