---
title: "Enterprise AX Agent Platform 12단계: Operator Dashboard"
date: 2026-06-19 21:38:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, operations, dashboard, backend]
---

지난 단계에서 `GET /v1/operations/summary`를 만들었다.

이번 단계에서는 그 read model을 실제 운영 화면으로 연결했다.

Agent 제품은 API만 있어도 동작한다.
하지만 운영자는 curl로 시스템 상태를 보지 않는다.

운영자가 필요한 것은 하나의 화면에서 다음 흐름을 보는 것이다.

```text
현재 지표
승인 대기 작업
tool catalog
최근 audit event
승인 / 반려 action
```

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 목표

새 route는 다음이다.

```text
GET /dashboard
```

별도 frontend build system은 붙이지 않았다.
FastAPI router가 HTML, CSS, JavaScript를 반환한다.

이 선택은 단순화가 목적이다.

```text
운영 화면이 필요한 데이터 계약을 먼저 검증한다.
backend endpoint와 화면 interaction을 한 repo에서 고정한다.
별도 SPA build pipeline 없이 로컬에서 바로 확인한다.
```

## 화면 구성

Operator dashboard는 네 영역으로 나눴다.

```text
1. summary metrics
2. pending approvals
3. tool catalog
4. audit events
```

summary 영역은 `GET /v1/operations/summary`를 호출한다.

approval 영역은 다음 API를 사용한다.

```text
GET  /v1/approvals/pending
POST /v1/approvals/{approval_id}/approve
POST /v1/approvals/{approval_id}/reject
```

tool catalog는 `GET /v1/tools`를 읽는다.

audit 영역은 `GET /v1/audit/events`를 읽는다.

## API Key 입력

dashboard에는 API key 입력 필드가 있다.

인증이 꺼진 로컬 모드에서는 비워도 동작한다.
인증을 켠 환경에서는 입력한 key를 `X-API-Key` 헤더로 보낸다.

이 방식으로 dashboard는 두 모드를 모두 지원한다.

```text
AUTH_ENABLED=false -> 로컬 확인
AUTH_ENABLED=true  -> scope guard 확인
```

중요한 점은 dashboard가 인증을 우회하지 않는다는 것이다.
화면에서 누르는 승인/반려도 일반 API와 같은 권한 경계를 통과한다.

## Approval Action

승인 대기 row는 두 가지 action을 가진다.

```text
Approve
Reject
```

Approve는 pending approval을 실행 상태로 전이하고, replay 결과를 저장한다.
Reject는 replay를 실행하지 않고 rejected 상태로 닫는다.

운영 화면에서 가장 중요한 것은 상태 전이가 눈에 보이는 것이다.

```text
pending -> executed
pending -> rejected
```

이 상태가 audit event와 같이 남아야 나중에 실행 책임을 추적할 수 있다.

## Backend 관점

이 단계에서 중요한 것은 화면의 장식이 아니다.

dashboard는 backend read model의 소비자다.

```text
OperationsSummaryUseCase
ApprovalRepositoryPort
ToolRegistryPort
AuditLogPort
```

화면이 이 포트들을 직접 알지는 않는다.
화면은 HTTP API만 알고, API가 use case와 repository를 호출한다.

이 경계를 유지하면 나중에 React나 다른 운영 UI로 바꿔도 backend 계약은 그대로 남는다.

## 검증

테스트는 dashboard route가 살아 있고, 핵심 문구와 action endpoint가 포함되는지 확인한다.

추가로 dashboard approval action test를 넣어 승인/반려 버튼이 호출하는 API 흐름을 확인했다.

현재 검증 명령은 다음이다.

```text
make verify
ruff check .                       -> 통과
mypy apps --explicit-package-bases -> 통과
pytest                             -> 통과
regression evaluation              -> 통과
```

## 다음 단계

운영 화면이 생기면 다음 질문은 권한이다.

누구나 dashboard에 접근해서 승인 버튼을 누르면 안 된다.
다음 단계에서는 HTTP API key와 scope guard를 추가한다.
