---
title: "Enterprise AX Agent Platform 3단계: 승인 요청과 멱등적 replay"
date: 2026-06-19 17:45:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, approval, idempotency, tool-runtime, audit-log, backend]
---

지난 단계에서 Agent와 외부 시스템 사이에 `Tool Runtime`을 넣었다.  
쓰기성 tool은 바로 실행하지 않고 `approval_required` 상태로 남겼다.

그 다음 문제는 자연스럽다.

```text
승인이 필요한 요청을 운영자가 어디서 보고,
승인 후 어떻게 실행하며,
같은 승인이 두 번 눌렸을 때 어떻게 막을 것인가?
```

이번 단계에서는 승인 요청을 별도 리소스로 승격하고, 승인 후 replay를 멱등적으로 처리했다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 문제

Agent가 외부 상태를 바꾸는 순간부터 일반적인 답변 생성과 다른 문제가 생긴다.

- 실행 전 승인이 필요한가
- 누가 승인했는가
- 승인 후 실제 실행 결과는 무엇인가
- 같은 승인 요청이 두 번 실행되면 어떻게 되는가
- 나중에 감사할 때 원래 Agent 실행과 승인 실행을 연결할 수 있는가

그래서 `tool_executions` 안에 문자열로만 남기지 않고 `approval_requests`라는 리소스를 추가했다.

## 도메인 모델

새 모델은 `ApprovalRequest`다.

```text
ApprovalRequest
  id
  tenant_id
  agent_run_id
  tool_execution_id
  tool_name
  action_type
  input_payload
  reason
  status
  requested_by
  approved_by
  replay_result
```

상태는 작게 시작했다.

```text
pending -> executed
pending -> rejected
```

이번 구현 범위는 `pending -> executed`다.

## 생성 흐름

Agent 실행 중 Tool Runtime이 `approval_required`를 반환하면 승인 요청을 만든다.

```text
Agent Run
  -> Tool Runtime
  -> ToolExecution(decision=approval_required)
  -> ApprovalRequest(status=pending)
  -> audit event: approval.requested
```

승인 요청 id는 tool execution id와 맞췄다.  
운영자가 API 응답의 `tool_executions[0].id`를 그대로 승인 API에 사용할 수 있게 하기 위해서다.

## API

pending 승인 목록:

```text
GET /v1/approvals/pending?tenant_id=default
```

승인 후 replay:

```text
POST /v1/approvals/{approval_id}/approve
```

요청:

```json
{
  "tenant_id": "default",
  "approved_by": "operator-01"
}
```

응답:

```json
{
  "status": "executed",
  "approved_by": "operator-01",
  "replay_result": {
    "tool_name": "workflow.request-change",
    "decision": "allowed",
    "status": "succeeded"
  }
}
```

## 멱등성

승인 API의 중요한 동작은 중복 실행 방지다.

이미 `executed` 상태인 승인 요청을 다시 승인하면 tool을 다시 replay하지 않는다.  
기존 `replay_result`를 그대로 반환한다.

```text
if approval.status == executed:
    return existing approval
```

이건 작은 코드지만 운영에서는 중요하다.  
브라우저 재시도, 네트워크 timeout, 사용자의 더블 클릭, workflow 재전송이 모두 생길 수 있기 때문이다.

## 감사 이벤트

이번 단계에서는 두 이벤트가 남는다.

```text
approval.requested
approval.executed
```

`approval.requested`는 Agent가 승인 필요한 tool call을 만들었을 때 기록된다.  
`approval.executed`는 운영자가 승인하고 replay가 완료됐을 때 기록된다.

이렇게 하면 실행을 나중에 재구성할 수 있다.

```text
agent_run
  -> tool.approval_required
  -> approval.requested
  -> approval.executed
```

## 저장소

메모리 저장소와 Postgres 저장소 모두 같은 Port를 구현한다.

```text
ApprovalRepositoryPort
  save
  list_pending
  get
```

Postgres에는 `approval_requests` 테이블을 추가했다.

```text
approval_requests
  id
  tenant_id
  agent_run_id
  tool_execution_id
  tool_name
  action_type
  input_payload
  reason
  status
  requested_by
  approved_by
  replay_result
```

승인 요청은 tool call의 부가 로그가 아니라 운영자가 처리하는 업무 리소스다.

## 검증

이번 단계에서 확인한 것:

- action 요청이 approval request를 생성한다.
- pending approval 목록을 API로 조회할 수 있다.
- approve API가 replay를 실행하고 `executed`로 바꾼다.
- 같은 approval을 다시 approve해도 replay 결과가 바뀌지 않는다.
- audit event가 남는다.

검증 결과:

```text
make verify
ruff check .                       -> 통과
mypy apps --explicit-package-bases -> 통과
pytest                             -> 5 passed
```

## 다음 단계

이제 남은 경계는 실제 외부 tool server다.

다음에는 local runtime을 MCP 서버 경계로 밀어낼 생각이다.

1. MCP Streamable HTTP server
2. tool schema registry
3. required scope
4. 승인 후 MCP tool replay
5. tool call timeout/retry
6. 운영자 dashboard

Agent가 외부 시스템을 실행하는 제품이라면, 승인과 replay는 부가 기능이 아니라 핵심 실행 경계다.
