---
title: "Enterprise AX Agent Platform 21단계: Compatible Error Envelope"
date: 2026-06-19 23:59:30 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, error-handling, observability, backend]
---

지난 단계에서 request id를 audit event와 webhook delivery까지 전파했다.

이번 단계에서는 오류 응답 body에도 같은 request id를 넣었다.

다만 중요한 조건이 있었다.

```text
기존 FastAPI detail 계약을 깨지 않는다.
```

운영 추적성을 높이겠다고 클라이언트가 이미 읽고 있는 오류 구조를 바꾸면 안 된다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 목표

오류 응답은 다음 구조를 따른다.

```json
{
  "detail": "Agent 실행 이력을 찾을 수 없습니다.",
  "request_id": "error-trace-001"
}
```

validation error도 같은 envelope를 쓴다.

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "content"],
      "msg": "String should have at least 20 characters"
    }
  ],
  "request_id": "validation-trace-001"
}
```

핵심은 `detail`을 그대로 두고 `request_id`만 추가하는 것이다.

## 왜 error 객체로 바꾸지 않았나

처음 생각하기 쉬운 구조는 이런 형태다.

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "...",
    "request_id": "..."
  }
}
```

하지만 이 프로젝트는 이미 FastAPI 기본 오류 구조 위에서 동작한다.

기존 테스트와 클라이언트는 다음 값을 읽는다.

```text
body.detail
```

따라서 오류 구조를 바꾸면 관측성을 얻는 대신 호환성을 잃는다.

이번 단계에서는 안정적인 확장을 선택했다.

```text
before: { "detail": ... }
after:  { "detail": ..., "request_id": ... }
```

## Exception Handlers

새 파일을 추가했다.

```text
apps/api/core/errors.py
```

handler는 세 종류다.

```text
HTTPException
RequestValidationError
Exception
```

FastAPI app 생성 시 handler를 설치한다.

```text
install_exception_handlers(app)
```

## HTTPException

`HTTPException.detail`은 그대로 둔다.

```text
404 -> detail string
403 -> detail object
409 -> detail string
```

이렇게 해야 기존 클라이언트가 `detail["missing_scopes"]` 같은 값을 계속 읽을 수 있다.

## Validation Error

validation error는 `detail`이 list다.

이 구조도 바꾸지 않는다.

```text
detail: list[validation_error]
request_id: string
```

Pydantic validation error에는 직렬화가 애매한 값이 들어갈 수 있으므로 `jsonable_encoder`를 거친다.

## Unhandled Error

예상하지 못한 예외는 내부 정보를 노출하지 않는다.

```json
{
  "detail": "Internal Server Error",
  "request_id": "..."
}
```

서버 로그에는 middleware가 이미 `http.request.failed`와 request id를 남긴다.

클라이언트는 request id를 운영자에게 전달할 수 있고, 운영자는 같은 id로 서버 로그를 찾을 수 있다.

## 테스트

두 가지 경로를 테스트했다.

```text
GET /v1/agents/runs/{missing_id}
  X-Request-ID: error-trace-001
-> 404
-> detail 유지
-> request_id 포함
```

그리고 validation error:

```text
POST /v1/documents/ingest
  content too short
  X-Request-ID: validation-trace-001
-> 422
-> detail list 유지
-> request_id 포함
```

기존 403 테스트도 그대로 통과한다.

```text
forbidden.json()["detail"]["missing_scopes"]
```

이 검증이 중요하다. 새 envelope가 기존 오류 계약을 깨지 않았다는 뜻이다.

## 검증 결과

```text
make verify
ruff check .                       -> 통과
mypy apps --explicit-package-bases -> 62 source files 통과
pytest                             -> 34 passed
regression evaluation              -> 통과
docker compose build               -> 통과
```

## 다음 단계

이제 HTTP request, audit event, webhook delivery, error response가 같은 request id를 공유한다.

다음으로 할 일은 이 데이터를 운영자가 더 쉽게 보는 것이다.

```text
dashboard latency panel
request id 검색
최근 오류 이벤트 요약
structured JSON logging
```

관측성은 필드를 추가하는 것으로 끝나지 않는다. 운영자가 장애를 설명할 수 있는 화면과 흐름까지
이어져야 한다.
