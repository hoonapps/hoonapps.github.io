---
title: "Enterprise AX Agent Platform 04: 승인, 권한, 멱등성"
date: 2026-06-20 00:56:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, approval, security, idempotency, backend]
description: "쓰기성 tool call을 승인 리소스로 승격하고 API key scope, tenant guard, Idempotency-Key를 연결했다."
---

Agent가 외부 상태를 바꾸면 실행 권한과 승인 상태가 제품 모델이 된다. 단순히 `confirm=true` 같은 flag로 처리할 문제가 아니다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## Approval Resource

쓰기성 tool call은 즉시 실행하지 않고 approval request로 전환한다.

```text
pending
-> executed
-> rejected
```

승인과 반려는 모두 닫힌 상태다. 이미 executed 또는 rejected가 된 approval을 다시 처리하면 중복 실행이 발생할 수 있다. 그래서 replay는 상태 전이를 기준으로 멱등적으로 막는다.

## Approve와 Reject

운영 API는 approval을 명시적인 리소스로 다룬다.

```text
GET  /v1/approvals/pending
POST /v1/approvals/{approval_id}/approve
POST /v1/approvals/{approval_id}/reject
```

승인하면 원래 tool request를 replay한다. 반려하면 실행하지 않고 audit event만 남긴다. 반려도 중요한 상태 전이다. 실행하지 않기로 결정한 사실이 기록되어야 나중에 같은 요청을 설명할 수 있다.

## API Key Scope

API key 인증은 선택형으로 만들었다. 로컬 기본 모드는 열어두고, 설정을 넣으면 운영 API가 scope guard를 통과해야 한다.

```text
documents:read
documents:write
agents:run
approvals:write
operations:read
operations:write
audit:read
```

scope는 endpoint 접근과 tool 실행 양쪽에서 사용한다. HTTP API를 통과했더라도 tool registry의 required scope를 만족하지 못하면 실행하지 않는다.

## Tenant Guard

tenant 접근은 scope와 별도다.

```text
scope: 무엇을 할 수 있는가
tenant: 어디에 할 수 있는가
```

같은 `agents:run` scope를 가져도 다른 tenant의 문서와 audit event에 접근하면 안 된다. 이 구분을 API dependency와 repository query 경계에 반영했다.

## Idempotent Write

쓰기 API에는 `Idempotency-Key`를 붙였다.

```text
Idempotency-Key: agent-run-001
```

동일 key와 동일 payload는 저장된 응답을 replay한다. 동일 key에 다른 payload가 오면 거절한다. 네트워크 timeout 이후 클라이언트가 재시도해도 문서 적재, Agent 실행, 승인 replay가 중복 처리되지 않게 하기 위한 장치다.

## 결과

이 단계에서 실행 제어가 UI 버튼이 아니라 백엔드 상태 모델로 올라왔다.

- approval pending/executed/rejected 상태 전이
- approve replay 중복 방지
- reject audit event
- API key scope guard
- tenant scoped credential
- Idempotency-Key 기반 write replay

Agent 시스템에서 권한과 승인은 보조 기능이 아니라 실행 모델의 일부다.
