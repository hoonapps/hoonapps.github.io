---
title: "Enterprise AX Agent Platform 19단계: Request Observability Headers"
date: 2026-06-19 23:58:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, observability, request-id, backend]
---

Agent 시스템은 기능이 늘수록 장애를 설명하기 어려워진다.

질문 하나가 다음 흐름을 지난다.

```text
HTTP request
-> 인증
-> 정책 검사
-> 검색
-> tool runtime
-> audit event
-> webhook outbox
```

이 흐름에서 가장 먼저 필요한 관측성은 request id다.

이번 단계에서는 모든 HTTP 응답에 request id와 처리 시간 헤더를 추가했다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 목표

모든 HTTP 응답은 두 헤더를 가진다.

```text
X-Request-ID
X-Process-Time-Ms
```

호출자가 `X-Request-ID`를 보내면 같은 값을 응답한다.

보내지 않으면 서버가 UUID를 생성한다.

```bash
curl http://127.0.0.1:8000/health \
  -H "X-Request-ID: local-trace-001" \
  -i
```

## Middleware

구현은 FastAPI middleware로 넣었다.

```text
RequestContextMiddleware
```

흐름은 다음과 같다.

```text
read X-Request-ID
or generate UUID
-> contextvar에 저장
-> downstream endpoint 실행
-> X-Request-ID response header
-> X-Process-Time-Ms response header
-> structured log extra
```

request id는 `ContextVar`에 저장한다.

```text
current_request_id()
```

지금은 middleware와 log context에서 사용한다.
나중에는 audit event payload, error response, external webhook correlation id에도 연결할 수 있다.

## 처리 시간

`X-Process-Time-Ms`는 app 경계에서 측정한다.

이 값은 네트워크 전체 시간이 아니다.

```text
ASGI app에 들어온 뒤
endpoint와 middleware를 지나
response가 만들어질 때까지의 시간
```

이 값을 넣는 이유는 운영자가 request 단위 지연을 빠르게 볼 수 있게 하기 위해서다.

정밀한 metrics system이 없더라도 다음 질문에 답할 수 있다.

```text
이 요청이 느렸는가?
같은 request id로 서버 로그를 찾을 수 있는가?
클라이언트 timeout과 서버 처리 시간이 다른가?
```

## 로그 Context

middleware는 request 완료 시 structured extra를 붙여 로그를 남긴다.

```text
request_id
method
path
status_code
elapsed_ms
client_host
```

예외가 발생하면 `http.request.failed`로 exception log를 남긴다.

중요한 점은 API 응답, 서버 로그, 나중에 추가될 audit payload가 같은 request id를 공유할 수
있게 됐다는 것이다.

## Header Contract

API 문서의 헤더 계약도 업데이트했다.

```text
X-Request-ID       -> 호출자 request id 또는 서버 생성 UUID
X-Process-Time-Ms  -> 애플리케이션 처리 시간
Idempotency-Key    -> write API 재시도 안전성
X-Tenant-Id        -> 요청 body가 없을 때 tenant 지정
```

request id와 idempotency key는 역할이 다르다.

```text
X-Request-ID     -> 추적
Idempotency-Key  -> 중복 실행 방지
```

둘을 섞으면 안 된다.

## 테스트

테스트는 두 가지를 검증한다.

```text
호출자가 X-Request-ID를 보내면 같은 값이 응답된다.
호출자가 보내지 않으면 UUID가 생성된다.
두 경우 모두 X-Process-Time-Ms가 포함된다.
```

현재 검증 결과:

```text
make verify
ruff check .                       -> 통과
mypy apps --explicit-package-bases -> 통과
pytest                             -> 30 passed
regression evaluation              -> 통과
docker compose build               -> 통과
```

## 다음 단계

request id는 시작점이다.

다음 개선은 이 id를 더 깊은 이벤트에 연결하는 것이다.

```text
audit event payload에 request_id 포함
error response의 trace id 정리
dashboard에서 latency distribution 표시
structured log JSON formatter
```

관측성은 별도 도구를 붙이는 일이 아니라, 시스템 내부의 중요한 상태를 같은 언어로 연결하는 일이다.
